# runner.py
import os
import yaml
import subprocess

def execute_journey(relative_filepath):
    # relative_filepath looks like "user-journies/create-paste.md"
    # Resolve it against our generic Docker mount
    container_filepath = os.path.join("/app/project", relative_filepath)

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

    print(f"Executing: {metadata.get('name')}")
    
    # 5. Execute Gemini CLI with the prompt in the project directory
    # The gemini CLI will automatically pick up /app/project/.gemini/settings.json
    try:
        # Run the gemini CLI command in headless (-p) and YOLO (-y) mode
        result = subprocess.run(
            ["gemini", "-y", "-p", prompt], 
            cwd="/app/project",
            check=True
        )
        print("Journey completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Journey execution failed with exit code: {e.returncode}")

if __name__ == "__main__":
    with open("/app/selected-journeys.txt") as f:
        journeys = f.read().splitlines()
    
    for j in journeys:
        if j.strip():
            execute_journey(j.strip())
