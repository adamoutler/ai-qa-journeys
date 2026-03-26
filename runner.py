# runner.py
import os
import sys
import yaml
import subprocess

def execute_journey(relative_filepath):
    # relative_filepath looks like "user-journies/create-paste.md"
    # Resolve it against our generic Docker mount
    container_filepath = os.path.join("/app/project", relative_filepath)

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
        subprocess.run(cmd, shell=True, check=True)

    # 3. Export Journey-Specific Env Vars (Expands ${RANDOM_TEXT})
    for key, val in metadata.get("environmental_variables", {}).items():
        os.environ[key] = os.path.expandvars(str(val))

    # 4. Read the persona to construct the system prompt
    with open("/app/persona.md", "r") as f:
        persona = f.read()

    sys_instruct = f"{persona}\n\nConstraints: {metadata.get('limitations')}"
    prompt = f"System Instruction:\n{sys_instruct}\n\nTask:\n{markdown_body}"

    print(f"Executing: {metadata.get('name', relative_filepath)}")
    
    # 5. Execute Gemini CLI with the prompt in the project directory
    try:
        # Run the gemini CLI command in headless (-p) and YOLO (-y) mode
        # We capture output to check for QA FAILED string
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

        if "QA FAILED" in result.stdout:
            print(f"Journey Result: FAILED (detected 'QA FAILED' in output)")
            return False
        
        if result.returncode != 0:
            print(f"Journey Result: FAILED (gemini CLI exited with code {result.returncode})")
            return False

        print("Journey Result: PASSED")
        return True

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
        print("\nOverall Result: FAIL")
        sys.exit(1)
    else:
        print("\nOverall Result: PASS")
        sys.exit(0)
