# runner.py
import os
import sys
import yaml
import subprocess
import re

def execute_journey(filename):
    # Security: Read journeys from the restricted /app/journeys mount
    container_filepath = os.path.join("/app/journeys", filename)

    if not os.path.exists(container_filepath):
        print(f"Error: Journey file not found: {container_filepath}")
        return False

    with open(container_filepath, 'r') as f:
        content = f.read()

    # 1. Split YAML frontmatter from Markdown body
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            metadata = yaml.safe_load(parts[1])
            markdown_body = parts[2]
        else:
            metadata, markdown_body = {}, content
    else:
        metadata, markdown_body = {}, content

    # 2. Execute frontmatter dependencies dynamically
    if 'python_dependencies' in metadata:
        subprocess.run(["pip", "install"] + metadata['python_dependencies'], check=True)
    
    for cmd in metadata.get('setup_commands', []):
        expanded_cmd = os.path.expandvars(str(cmd))
        subprocess.run(expanded_cmd, shell=True, check=True)

    # 3. Export Journey-Specific Env Vars
    for key, val in metadata.get("environmental_variables", {}).items():
        os.environ[key] = os.path.expandvars(str(val))

    # 4. Read the persona to construct the system prompt
    with open("/app/persona.md", "r") as f:
        persona = f.read()

    purpose = metadata.get('purpose', 'Not specified')
    constraints = metadata.get('limitations', 'No specific constraints')

    sys_instruct = f"{persona}\n\nPURPOSE OF THIS JOURNEY:\n{purpose}\n\nCONSTRAINTS:\n{constraints}"
    prompt = f"System Instruction:\n{sys_instruct}\n\nTask:\n{markdown_body}"

    print(f"Executing Journey: {metadata.get('name', filename)}")
    
    # 5. Execute Gemini CLI with the prompt in the project directory
    try:
        # Run the gemini CLI command in headless (-p) and YOLO (-y) mode
        result = subprocess.run(
            ["gemini", "-y", "-p", prompt], 
            cwd="/app/project",
            text=True,
            capture_output=True
        )
        
        # Always print the output so it's visible in Jenkins/Docker logs
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        # 6. Validation Phase
        journey_success = True

        # Check for mandatory failure string from persona
        if "QA FAILED" in result.stdout:
            print(f"Result: FAILED (detected 'QA FAILED' in agent output)")
            journey_success = False
        
        # Check for exit code
        if result.returncode != 0:
            print(f"Result: FAILED (gemini CLI exited with code {result.returncode})")
            journey_success = False

        # Metadata-based validation assertions (Resolve environment variables first)
        assertions = metadata.get('assertions', [])
        if isinstance(assertions, str):
            assertions = [assertions]
        
        for raw_pattern in assertions:
            pattern = os.path.expandvars(str(raw_pattern))
            if not re.search(pattern, result.stdout):
                print(f"Result: FAILED (Assertion failed: pattern '{pattern}' not found in output)")
                journey_success = False

        if journey_success:
            print("Result: PASSED")
        
        return journey_success

    except Exception as e:
        print(f"Journey execution encountered a critical error: {e}")
        return False

if __name__ == "__main__":
    if not os.path.exists("/app/selected-journeys.txt"):
        print("No journeys selected. Exiting.")
        sys.exit(0)

    with open("/app/selected-journeys.txt") as f:
        journeys = f.read().splitlines()
    
    any_failed = False
    for j in journeys:
        if j.strip():
            success = execute_journey(j.strip())
            if not success:
                any_failed = True
    
    if any_failed:
        print("\nOverall Results: FAIL")
        sys.exit(1)
    else:
        print("\nOverall Results: PASS")
        sys.exit(0)
