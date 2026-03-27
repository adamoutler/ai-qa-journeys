# AI QA Journeys

Automated end-to-end UI testing powered by Gemini and Playwright.

## Objective
This project provides a framework for running "Meticulous Visual QA" journeys. Unlike traditional automated tests that rely on DOM selectors and internal APIs, this system uses a Gemini-powered agent to interact with applications exactly like a human user would—interpreting the visual state of the screen and executing physical-style mouse and keyboard events.

## Features
*   **Human Emulation**: Strict constraints on interaction speeds, mouse movement curves, and keystroke cadences.
*   **Visual Truth**: Validates what is actually rendered, ensuring elements aren't hidden or obscured.
*   **Multi-Project Support**: Can be pointed at different project folders containing specific user journeys.
*   **Security Isolation**: Containers run with restricted access to journey files and a volatile `tmpfs` workspace.
*   **MCP Integration**: Native support for Model Context Protocol (MCP) servers (e.g., Plane Kanban) for issue reporting.
*   **Jenkins Integration**: Designed to run as a nightly cron job with dynamic variable injection.

## Project Structure
```
/
├── journeys/
│   └── [project_name]/
│       ├── .gemini/
│       │   └── settings.json      # Project-specific MCP/Model config
│       └── user-journies/
│           └── [journey].md       # Markdown journey definitions
├── Jenkinsfile                    # CI/CD pipeline
├── Dockerfile                     # Test execution environment
└── runner.py                      # Orchestration script
```

## Setup & Usage
1.  **Local Simulation**: Run `./simulate_jenkins.sh` to test the entire flow locally using your existing `~/.gemini` credentials.
2.  **Jenkins**: Create a pipeline job pointing to this repository. Ensure the `plane-kanban-api-key` credential is set.
3.  **Authentication**: The container expects a mounted `~/.gemini` directory containing valid Google OAuth credentials.

## Multi-Arch Support
The execution container is built for both `linux/amd64` and `linux/arm64`.
