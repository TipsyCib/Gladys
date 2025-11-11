# Gladys - Agentic CLI Assistant

An intelligent conversational agent powered by Mistral AI with function calling, persistent memory, and real-world service integrations.

## 🌟 Features

### Core Capabilities
- **Agentic Function Calling**: Autonomous tool selection and execution
- **Persistent Memory**: JSON-based conversation history with automatic summarization
- **Smart Context Management**: Auto-compresses memory when size threshold is reached
- **Service Integrations**: Gmail, Google Contacts, and browser automation

### Available Tools
- 📅 **Date/Time**: Get current date in readable format
- 📧 **Gmail**: Read and send emails via OAuth2
- 👥 **Google Contacts**: Retrieve and manage contacts
- 🌐 **Browser Automation**: Automated web tasks with Selenium + Gemini

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Mistral API key
- (Optional) Node.js & npm for browser automation
- (Optional) Google API credentials for Gmail/Contacts
- (Optional) Gemini API key for browser automation

### Installation

1. **Clone and install core dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Create .env file

# Add your API keys to .env:
MISTRAL_API_KEY=your_mistral_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here  # For browser automation
GMAIL_MAIL_USER=your_email_adress
```

3. **Optional: Install browser automation:**
```bash
# Install Python dependencies
pip install -r requirements_browser.txt

# Install Browser Use via npm (required for web automation)
npm install -g browser-use
```

4. **Optional: Set up Google Services (Gmail/Contacts):**
   - Download OAuth2 credentials from Google Cloud Console
   - Save as `credentials/credentials.json`
   - First run will trigger OAuth flow and save token

### Run Gladys

```bash
python main.py
```

## 💬 Usage

### Basic Commands
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/exit` or `/quit` - Exit the chatbot

### Example Interactions

**Get current date:**
```
You: What's today's date?
Gladys: Today is Saturday, October 05, 2025
```

**Send an email (requires Gmail setup):**
```
You: Send an email to contact@example.com with subject "Meeting" and say "Let's meet tomorrow"
Gladys: [Executes tool: send_mail_gmail]
Gladys: Email sent successfully!
```

**Automate browser tasks (requires browser setup):**
```
You: Go to example.com and find the contact information
Gladys: [Executes tool: execute_browser_task]
Gladys: Found the following contact info: ...
```

## 🏗️ Architecture
 
```
your-folder/
├── main.py           # CLI entry point and chat loop
├── agent.py          # Mistral API client with function calling
├── tools.py          # Tool registry and execution
├── memory.py         # Conversation persistence and compression
├── config.py         # Configuration management
├── prompts.yaml      # System prompts and templates
├── .env              # API keys (not in git)
├── memory.json       # Auto-generated conversation history
└── services/         # Service integrations
    ├── browser/
    │   └── browser_agent.py
    └── google/
        ├── gmail/
        └── contacts/
```

## 🔧 Configuration

### Memory Management
Edit `config.py` to adjust:
- `MEMORY_THRESHOLD_KB`: Memory size before summarization (default: 50KB)
- `KEEP_RECENT_MESSAGES`: Number of recent messages to keep after compression (default: 10)

### Model Settings
- Default model: `mistral-large-latest`
- Configure in `config.py` via `MISTRAL_MODEL` variable

### Custom Prompts
Edit `prompts.yaml` to customize:
- System prompt (agent behavior and personality)
- Summarization prompt (memory compression instructions)

## 🛠️ Adding New Tools

1. **Implement the tool function** in `tools.py`:
```python
def my_new_tool(arg1: str, arg2: int) -> str:
    """Tool description."""
    # Your implementation
    return result
```

2. **Add to tool registry**:
```python
TOOL_FUNCTIONS = {
    "my_new_tool": my_new_tool,
    # ... other tools
}
```

3. **Define the schema**:
```python
TOOL_SCHEMAS.append({
    "type": "function",
    "function": {
        "name": "my_new_tool",
        "description": "What this tool does",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "Description"},
                "arg2": {"type": "integer", "description": "Description"}
            },
            "required": ["arg1", "arg2"]
        }
    }
})
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

Current test coverage:
- 10 tool execution tests (`tests/test_core.py`)
- 8 memory management tests (`tests/test_memory.py`)
- 18 tests total, all passing ✅

## 📋 Roadmap

- **Phase 1** ✅: Core chatbot with tools and memory
- **Phase 1.5** ⏳: IoT control (Tapo smart bulbs)
- **Phase 2** ✅: Service integrations (Gmail, Contacts, Browser)
- **Phase 3** ⏳: Voice interface (STT/TTS)
- **Phase 4** ⏳: Animated character with emotions

See [PLAN.md](PLAN.md) for detailed roadmap.

## 🔐 Security Notes

- API keys stored in `.env` (never commit to git)
- OAuth tokens saved in `credentials/` (git-ignored)
- Sensitive files listed in `.gitignore`

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a pedagogical project demonstrating agentic patterns. Feel free to fork and extend!

---

**Built with ❤️ using Mistral AI**
