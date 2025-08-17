# Open WebUI User Guide

Welcome to Open WebUI! This comprehensive guide will help you navigate and utilize all features of the platform.

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Interface Overview](#user-interface-overview)
3. [Chat with AI Models](#chat-with-ai-models)
4. [RAG (Retrieval Augmented Generation)](#rag-retrieval-augmented-generation)
5. [Web Browsing](#web-browsing)
6. [Image Generation](#image-generation)
7. [Voice and Video Calls](#voice-and-video-calls)
8. [Managing Models](#managing-models)
9. [User Settings](#user-settings)
10. [Advanced Features](#advanced-features)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

## Getting Started

### First-Time Login

1. Open your browser and navigate to Open WebUI (typically at http://localhost:3000 for local installations)
2. If this is your first time, you'll be prompted to create an admin account
3. Enter your desired username and a strong password
4. Click "Register" to create your account and log in

### Changing Your Password

1. Click on your profile icon in the top-right corner
2. Select "Settings" from the dropdown menu
3. Go to the "Account" tab
4. Click "Change Password" and follow the prompts

### Creating Additional Users (Admin Only)

1. Navigate to "Settings" > "Users" in the admin panel
2. Click "Add User"
3. Fill in the user details and assign appropriate roles
4. Click "Create User"

## User Interface Overview

The Open WebUI interface consists of several key components:

### Main Navigation Sidebar

- **Chat**: Start new conversations or continue existing ones
- **Explore**: Browse available models and discover capabilities
- **Files**: Access and manage your uploaded documents
- **Tools**: Access various tools like RAG, image generation, etc.
- **Settings**: Configure your user preferences and system settings

### Chat Interface

- **Model Selection**: Choose which AI model to chat with
- **Message Area**: View conversation history
- **Input Box**: Type your messages to the AI
- **Function Bar**: Access special functions (upload files, voice input, etc.)

### Settings Panel

- **General**: Core application settings
- **Models**: Configure model behavior
- **Appearance**: Customize the UI look and feel
- **Security**: Manage security settings (for admins)
- **Users**: Manage user accounts (for admins)

## Chat with AI Models

### Starting a New Chat

1. Click "New Chat" in the sidebar or the "+" icon
2. Select a model from the dropdown menu
3. Start typing your message in the input box
4. Press Enter or click the send button

### Continuing Previous Conversations

1. Click on any conversation in the sidebar
2. The chat history will load
3. Continue the conversation by typing in the input box

### Adjusting Model Parameters

1. Click the settings icon (gear) near the model selection dropdown
2. Adjust parameters like:
   - Temperature (controls randomness)
   - Top P (controls diversity)
   - Max tokens (controls response length)
3. Click "Save" to apply changes

### Using Markdown and Code

The chat interface supports Markdown formatting and code blocks:

- Use `*italic*` for *italic* text
- Use `**bold**` for **bold** text
- Use `` `code` `` for `inline code`
- Use triple backticks for code blocks with syntax highlighting:

```python
def hello_world():
    print("Hello, World!")
```

### LaTeX Support

Mathematical formulas can be entered using LaTeX syntax:

- Inline formulas: `$E = mc^2$`
- Block formulas: `$$\int_{a}^{b} f(x) dx$$`

## RAG (Retrieval Augmented Generation)

RAG allows the AI to reference documents you've uploaded when answering questions.

### Adding Documents to Your Library

1. Navigate to "Files" in the sidebar
2. Click "Upload" and select documents from your computer
3. Supported formats: PDF, TXT, DOCX, MD, CSV, and more
4. Wait for the documents to be processed (embedding)

### Querying Documents

1. Start a new chat
2. Type `#` followed by a keyword to search your documents
3. Select relevant documents from the dropdown
4. Ask your question, and the AI will incorporate information from the selected documents

### Document Management

1. Go to the "Files" section to see all your documents
2. Click on any document to see its content
3. Use the search bar to find specific documents
4. Delete documents by selecting them and clicking "Delete"

## Web Browsing

Open WebUI can browse the web and retrieve information for you.

### Browsing a Website

1. In chat, type `#` followed by a URL (e.g., `#https://example.com`)
2. The AI will visit the website and summarize its content
3. Ask questions about the website's content

### Web Search

1. Enable web search in Settings > Tools > Web Search
2. Configure your preferred search provider
3. In chat, ask questions that require up-to-date information
4. The AI will automatically search and include relevant information

## Image Generation

Generate images using integrated image models.

### Generating Images

1. In chat, type `/image` followed by your image description
2. Select an image model from the dropdown
3. Adjust settings like resolution and style
4. Click "Generate" and wait for the image to appear

### Image Settings

1. Go to Settings > Tools > Image Generation
2. Configure default settings for image generation
3. Connect to external image generation APIs if desired

## Voice and Video Calls

Interact with AI models using voice or video interfaces.

### Starting a Voice Call

1. Click the microphone icon in the chat input area
2. Grant microphone permissions if prompted
3. Speak your queries and listen to AI responses
4. Click the microphone icon again to end the call

### Video Call Features

1. Click the video icon to start a video call
2. Grant camera and microphone permissions
3. Use hand gestures to control the conversation
4. Click "End Call" when finished

## Managing Models

### Browsing Available Models

1. Navigate to the "Explore" section in the sidebar
2. See all available models categorized by type and capability
3. Click on any model to see details and parameters

### Downloading New Models (Ollama)

1. Go to "Explore" > "Ollama Models"
2. Search for models or browse categories
3. Click "Download" next to any model you want to use
4. Wait for the download to complete

### Creating Custom Models

1. Go to "Tools" > "Model Builder"
2. Select a base model to customize
3. Configure model parameters and training data
4. Click "Create" and follow the prompts

### Managing Model Access (Admin Only)

1. Go to "Settings" > "Security" > "Model Access"
2. Select a user group
3. Check/uncheck models to grant/revoke access
4. Click "Save Changes"

## User Settings

### Appearance Settings

1. Go to "Settings" > "Appearance"
2. Choose between light, dark, or system theme
3. Adjust font size and chat bubble style
4. Configure message grouping and timestamps

### Language Settings

1. Go to "Settings" > "General" > "Language"
2. Select your preferred interface language
3. Click "Save Changes"

### Notification Settings

1. Go to "Settings" > "Notifications"
2. Enable/disable various notification types
3. Configure sound alerts and desktop notifications

## Advanced Features

### Python Function Calling

1. Go to "Tools" > "Python Functions"
2. Create new functions or import existing ones
3. Use the functions in chat by typing `/function name(parameters)`
4. View outputs directly in the chat

### Pipelines Plugin

1. Install the Pipelines Plugin from Settings > Plugins
2. Configure your pipeline workflow in the Pipelines interface
3. Connect models and tools in a custom processing pipeline
4. Use your pipeline by typing `/pipeline name` in chat

### API Access

1. Go to "Settings" > "API Access"
2. Generate a new API key
3. Use this key to access Open WebUI programmatically
4. Reference the API documentation for endpoints and parameters

## Troubleshooting

### Connection Issues

If you can't connect to Open WebUI:

1. Check that the server is running
2. Verify the correct URL and port
3. Check your network connection
4. Review server logs for errors

### Model Loading Problems

If models fail to load:

1. Check that Ollama is running correctly
2. Verify model files exist in the expected location
3. Check disk space availability
4. Restart the Ollama service

### RAG Not Working

If RAG features aren't working properly:

1. Check that your documents were processed successfully
2. Verify embedding models are installed correctly
3. Try re-uploading problematic documents
4. Check server logs for embedding errors

## FAQ

### What is the difference between chat modes?

- **Standard Chat**: Regular conversation with the selected model
- **RAG Chat**: Conversation augmented with document knowledge
- **Multi-Model Chat**: Simultaneous conversation with multiple models

### How do I save my conversations?

Conversations are automatically saved in the sidebar. To export a conversation:

1. Open the conversation
2. Click the export icon (top-right of chat)
3. Choose export format (TXT, MD, or PDF)
4. Save the file to your computer

### What model should I use?

The best model depends on your needs:

- For general chat: Try Llama 3-8B or Mistral-7B
- For complex reasoning: Try larger models like Llama 3-70B
- For code: Try Code Llama or WizardCoder
- For multilingual: Try BLOOM or Mistral models

### How do I report issues or request features?

1. Go to our GitHub repository: https://github.com/open-webui/open-webui
2. Click on "Issues"
3. Search existing issues to see if yours has been reported
4. Click "New Issue" and select the appropriate template
5. Fill in the details and submit

---

Need more help? Join our [Discord community](https://discord.gg/5rJgQTnV4s) or check the [official documentation](https://docs.openwebui.com/).
