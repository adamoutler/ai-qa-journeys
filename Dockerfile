FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy 
WORKDIR /app

# Install Node.js for Gemini CLI
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @google/gemini-cli

# Pre-install dependencies and Playwright browsers to speed up execution
COPY requirements.txt .
RUN pip install -r requirements.txt && \
    playwright install --with-deps chromium

COPY . .
ENTRYPOINT ["python", "runner.py"]
