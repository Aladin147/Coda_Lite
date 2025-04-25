# Coda Lite Installation and Setup Guide

This guide provides detailed instructions for installing and setting up Coda Lite on your system.

## Prerequisites

Before installing Coda Lite, ensure you have the following prerequisites:

### Hardware Requirements

- **CPU**: Modern multi-core processor (4+ cores recommended)
- **RAM**: 8GB minimum, 16GB+ recommended
- **GPU**: NVIDIA GPU with CUDA support recommended for optimal performance
- **Storage**: 10GB+ free space
- **Microphone**: Good quality microphone for voice input
- **Speakers**: Speakers or headphones for audio output

### Software Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: Python 3.10 or newer
- **Node.js**: Node.js 18 or newer (for dashboard)
- **CUDA**: CUDA 11.7+ and cuDNN (for GPU acceleration)
- **Git**: For cloning the repository

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Aladin147/Coda_Lite.git
cd Coda_Lite
```

### 2. Create a Python Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Ollama is required for running the LLM models locally.

#### Windows

Download and install from [Ollama's website](https://ollama.com/download).

#### macOS

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 5. Pull Required Models

```bash
# Pull Gemma 2B model
ollama pull gemma:2b

# Pull LLaMA 3 8B model (optional fallback)
ollama pull llama3:8b
```

### 6. Set Up ElevenLabs API (Optional)

If you want to use ElevenLabs for TTS:

1. Create an account at [ElevenLabs](https://elevenlabs.io/)
2. Get your API key from the dashboard
3. Create a `.env` file in the project root and add:

```
ELEVENLABS_API_KEY=your_api_key_here
```

### 7. Install Dashboard Dependencies

```bash
cd dashboard-v3
npm install
```

## Configuration

### Basic Configuration

The main configuration file is located at `config/config.yaml`. You can modify this file to customize Coda's behavior.

```yaml
# Example configuration
system:
  name: "Coda"
  debug: false
  websocket_port: 8765

llm:
  provider: "ollama"
  model: "gemma:2b"
  fallback_model: "llama3:8b"
  temperature: 0.7
  max_tokens: 1024

tts:
  provider: "elevenlabs"
  voice: "Alexandra"
  fallback_provider: "dia"

stt:
  provider: "whisper"
  model: "base"
  language: "en"

memory:
  vector_db: "chroma"
  importance_threshold: 0.5
  max_short_term_turns: 10
  summary_cache_ttl: 3600
```

### Advanced Configuration

For advanced configuration, you can modify the following files:

- `config/prompts/system_prompt.txt`: The system prompt for the LLM
- `config/prompts/user_profile.txt`: The user profile template
- `config/prompts/memory_prompt.txt`: The memory retrieval prompt

## Running Coda Lite

### 1. Start the Core System

```bash
# Activate the virtual environment if not already activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start the WebSocket server
python main_websocket.py
```

### 2. Start the Dashboard

In a new terminal:

```bash
cd dashboard-v3
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

## Troubleshooting

### Common Issues

#### CUDA/GPU Issues

If you encounter GPU-related errors:

1. Ensure CUDA and cuDNN are properly installed
2. Check that your GPU drivers are up to date
3. Verify that the CUDA version matches the requirements
4. Add CUDA to your system PATH

#### WebSocket Connection Issues

If the dashboard cannot connect to the WebSocket server:

1. Ensure the WebSocket server is running
2. Check that the port (default: 8765) is not blocked by a firewall
3. Verify that the WebSocket URL in the dashboard configuration is correct

#### Memory System Issues

If the memory system is not working correctly:

1. Check that the vector database is properly initialized
2. Verify that the memory configuration is correct
3. Ensure the system has write permissions to the data directory

#### TTS/STT Issues

If speech recognition or synthesis is not working:

1. Check that your microphone and speakers are properly connected
2. Verify that the correct audio devices are selected
3. Ensure the required models are properly installed
4. Check API keys for external services (e.g., ElevenLabs)

### Logs

Log files are stored in the `data/logs` directory. Check these logs for detailed error information.

## Updating Coda Lite

To update Coda Lite to the latest version:

```bash
git pull
pip install -r requirements.txt
cd dashboard-v3
npm install
```

## Advanced Setup

### Running with Docker

Docker support is planned for future releases.

### Running on a Headless Server

To run Coda Lite on a headless server:

1. Start the WebSocket server:
   ```bash
   python main_websocket.py
   ```

2. Connect to the server from a client machine using the dashboard.

### Custom Model Configuration

To use custom models:

1. For custom LLM models, add them to Ollama:
   ```bash
   ollama create custom-model -f Modelfile
   ```

2. Update the configuration to use your custom model:
   ```yaml
   llm:
     provider: "ollama"
     model: "custom-model"
   ```

## Next Steps

After installation, consider:

1. **Customizing the System Prompt**: Edit `config/prompts/system_prompt.txt` to customize Coda's personality and behavior.

2. **Setting Up User Profile**: Create a user profile to help Coda understand your preferences.

3. **Exploring the Dashboard**: Familiarize yourself with the dashboard features, including voice controls, memory visualization, and performance monitoring.

4. **Testing the Memory System**: Try having conversations that test Coda's memory capabilities, including fact recall and preference learning.

5. **Exploring Tool Integration**: Experiment with Coda's tool capabilities for enhanced functionality.

## Support

If you encounter issues or have questions, please:

1. Check the documentation in the `docs` directory
2. Look for similar issues in the GitHub repository
3. Create a new issue if your problem is not already addressed

## Contributing

Contributions to Coda Lite are welcome! See the `CONTRIBUTING.md` file for guidelines.
