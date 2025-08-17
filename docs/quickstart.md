# Quick Start Guide

This guide will help you quickly set up and start using Open WebUI, a powerful AI platform that supports various LLM runners like Ollama and OpenAI-compatible APIs.

## Installation Options

Choose one of the following installation methods:

### Option 1: Docker (Recommended)

The easiest way to get started is using Docker Compose:

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) installed
2. Download the `docker-compose.yaml` file:
   ```bash
   curl -o docker-compose.yaml https://raw.githubusercontent.com/open-webui/open-webui/main/docker-compose.yaml
   ```
3. Start the containers:
   ```bash
   docker-compose up -d
   ```
4. Access Open WebUI at http://localhost:3000

### Option 2: Kubernetes

For Kubernetes deployment:

1. Install the Helm chart:
   ```bash
   helm repo add open-webui https://open-webui.github.io/helm-charts
   helm repo update
   helm install open-webui open-webui/open-webui
   ```

2. Follow the instructions displayed after installation to access Open WebUI

### Option 3: Manual Installation

For manual installation:

1. Clone the repository:
   ```bash
   git clone https://github.com/open-webui/open-webui.git
   cd open-webui
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   npm install
   ```

3. Start the backend server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080
   ```

4. In another terminal, start the frontend:
   ```bash
   npm run dev
   ```

5. Access Open WebUI at http://localhost:5173

## First-Time Setup

1. When you first access Open WebUI, you'll be prompted to create an admin account
2. Set up your admin username and password
3. You'll be taken to the dashboard after login

## Connecting to Model Providers

### Using Ollama (Local Models)

1. Make sure Ollama is running (included in Docker setup)
2. Go to Settings > Model Providers > Ollama
3. The default URL should be set to `http://ollama:11434` if using Docker, or `http://localhost:11434` for manual installation
4. Click "Test Connection" to verify

### Using OpenAI-Compatible APIs

1. Go to Settings > Model Providers > OpenAI API
2. Enter your API key or the URL of your OpenAI-compatible API
3. Click "Test Connection" to verify

### Other Providers

Open WebUI supports many other providers like:
- Mistral
- Anthropic
- Groq
- OpenRouter

Configure these in the Settings > Model Providers section.

## Pulling Models (Ollama)

1. Go to Models > Ollama Models
2. Click "Pull Model"
3. Select from the available models or enter a specific model name
4. Wait for the download to complete

## Creating Your First Chat

1. Click "New Chat" in the sidebar
2. Select a model from the dropdown
3. Start chatting!

## Using RAG (Retrieval Augmented Generation)

1. Go to Knowledge > Document Library
2. Click "Upload Document"
3. Select a document from your computer
4. Wait for the document to be processed
5. In a chat, use the `#` command to access your document:
   ```
   #my_document What information does this document contain?
   ```

## Voice/Video Calls

1. In a chat, click the microphone icon
2. Grant permission to use your microphone and camera
3. Start speaking to interact with the AI

## Advanced Features

### Creating Custom Characters

1. Go to Models > Model Library
2. Click "Create Model"
3. Select "Character" as the model type
4. Fill in the character details and customize its personality
5. Save the character

### Using Multiple Models in a Chat

1. Start a new chat
2. Click the settings icon in the chat
3. Enable "Multi-Model Chat"
4. Select the models you want to include
5. Each message will be processed by all selected models

### Creating Tools with Python Functions

1. Go to Tools > Function Library
2. Click "Create Function"
3. Enter your Python code in the editor
4. Test the function
5. Save the function
6. Use the function in your chats with the `/` command

## Customizing the UI

1. Go to Settings > Appearance
2. Choose a theme
3. Customize colors, font sizes, and other UI elements
4. Save your changes

## Next Steps

- Explore the [Documentation](https://docs.openwebui.com/) for more details
- Join our [Discord community](https://discord.gg/openwebui) for support
- Check out [advanced configuration options](configuration.md)
- Learn about [deployment in production](deployment/production.md)

## Troubleshooting

If you encounter any issues:

1. Check the [Troubleshooting Guide](troubleshooting/common_issues.md)
2. Look at the logs (available in Settings > Logs)
3. Ask for help in our Discord community
