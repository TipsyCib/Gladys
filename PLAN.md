# Project Plan

## Design Principles
- **Simplicity First**: Few files, clear structure, easy to understand
- **Working Incrementally**: Each phase delivers a fully functional system
- **Good Practices**: Clean code without overengineering
- **Pedagogical**: Code should clearly demonstrate agentic concepts

## Current Status

**✅ Phase 1: COMPLETE** - Fully functional agentic chatbot with tool calling and memory management. 

**⏳ Phase 1.5: PENDING** - IoT control starting with Tapo smart lightbulbs. 

**✅ Phase 2: COMPLETE** - Service integration with Gmail, Contacts, and Browser automation. 

**⏳ Phase 3: PENDING** - Voice interface with STT/TTS for natural interaction. 

**⏳ Phase 4: PENDING** - Animated character (Gladys) with visual presence and emotions

## Architecture Overview (Implemented File Structure)
```
your-folder/
├── main.py                    # ✅ CLI entry point and chat loop with Rich TUI
├── agent.py                   # ✅ Mistral API integration and agent logic
├── tools.py                   # ✅ Tool definitions and registry
├── memory.py                  # ✅ JSON-based context management with auto-summarization
├── config.py                  # ✅ Configuration and environment management
├── prompts.yaml               # ✅ System and summarization prompts
├── .env                       # ✅ API key configuration (not in git)
├── memory.json                # ✅ Auto-generated conversation history
├── README.md                  # ✅ Comprehensive educational guide
├── requirements.txt           # ✅ Core dependencies
├── requirements_browser.txt   # ✅ Browser automation dependencies
├── credentials/               # ✅ Google API credentials (not in git)
├── tests/                     # ✅ Unit tests (18 tests, all passing)
│   ├── test_core.py          # ✅ Tool execution tests
│   └── test_memory.py        # ✅ Memory management tests
└── services/                  # ✅ Extended service integrations
    ├── browser/
    │   └── browser_agent.py  # ✅ Browser automation service
    └── google/
        ├── gmail/
        │   ├── __init__.py
        │   ├── access_mail_gmail.py  # ✅ Gmail reading service
        │   └── write_mail_gmail.py   # ✅ Gmail writing service
        └── contacts/
            ├── get_google_contacts.py  # ✅ Contacts retrieval service
            └── add_google_contacts.py  # ✅ Contacts management service
```

### Core Components:
- **main.py**: Simple CLI chat loop with command handling (exit, clear, help)
- **agent.py**: Mistral API client with function calling and automatic memory summarization
- **tools.py**: Extensible tool registry with function schemas and execution dispatcher
- **memory.py**: JSON-based conversation persistence with size-based compression
- **config.py**: Environment configuration loading (API keys, model settings, prompts)
- **prompts.yaml**: System prompts and summarization templates

### Service Integrations:
- **Browser Automation**: Selenium + Browser Use + Gemini for web tasks
- **Gmail Service**: OAuth2 email reading and sending
- **Google Contacts**: Contact retrieval and management

### Available Tools:
- `get_date()`: Returns current date in readable format
- `access_gmail()`: Read Gmail messages
- `send_mail_gmail(draft)`: Send emails from draft text
- `get_google_contacts()`: Retrieve contact list
- `add_google_contacts(name, email, phone)`: Add new contacts
- `execute_browser_task(task_description, expected_result)`: Automated web browsing

## Phase 1: Simple Working Version ✓ Core Deliverable
**Goal**: Deliver a fully functional agentic chatbot demonstrating all key concepts

### Components to Build:
1. **Project Setup** ✅
   - ~~Initialize `pyproject.toml` with minimal dependencies: `typer`, `mistralai`~~ (using direct pip install)
   - ✅ Create simple project structure (no complex packaging yet)

2. **CLI Chat Loop** (`main.py`) ✅
   - ✅ Simple line-by-line chat interface (no `rich` TUI yet)
   - ✅ Basic command handling (exit, clear, help)
   - ✅ Load memory on startup, save on exit

3. **Mistral API Integration** (`agent.py`) ✅
   - ✅ Connect to Mistral API with function calling support
   - ✅ System prompt for agentic behavior
   - ✅ Tool call parsing and execution loop
   - ✅ Return formatted responses to user

4. **Tool System** (`tools.py`) ✅
   - ✅ Define tool schema compatible with Mistral API
   - ✅ Implement two demonstration tools:
     - ✅ `write_to_file(filename, content)`: Write content to a file
     - ✅ `get_date()`: Return today's date in readable format
   - ✅ Tool registry and dispatcher

5. **Memory Management** (`memory.py`) ✅
   - ✅ Save conversation history as JSON in project folder
   - ✅ Load existing history on startup
   - ✅ Append new messages (user, assistant, tool calls)
   - ✅ **Context management logic**:
     - ✅ Check total memory size in KB before each turn
     - ✅ If above threshold (e.g., 50KB), call Mistral to summarize conversation
     - ✅ Keep last N messages + summary, discard old details
     - ✅ Continue conversation with compressed context

6. **Configuration** (`config.py`) ✅
   - ✅ API key management (from `.env` file using python-dotenv)
   - ✅ Memory thresholds and limits
   - ✅ Model selection and parameters
   - ✅ Prompts loaded from `prompts.yaml`

7. **Error Handling & Testing** ✅
   - ✅ Basic error handling for API failures and file operations
   - ✅ Simple unit tests (`pytest`) for core functions:
     - ✅ Tool execution (10 tests)
     - ✅ Memory save/load (8 tests)
     - ✅ All 18 tests passing
   - ✅ Basic logging for debugging

### End of Phase 1 Milestone: ✅ COMPLETED
✅ User can chat with agent → agent can call tools → memory persists and auto-summarizes → tested and working → complete demo

**Phase 1 Complete!** All core functionality implemented and tested. See [README.md](README.md) for comprehensive documentation.

## Phase 1.5: IoT Control & Smart Home Integration 🏠 Control Your World
**Goal**: Enable smart home device control, starting with TP-Link Tapo smart lightbulbs

### Components to Build:
1. **Tapo Smart Bulb Integration** ⏳
   - ⏳ Install and configure `PyP100` library for Tapo devices
   - ⏳ Device discovery and authentication
   - ⏳ Basic light control (on/off, brightness, color)
   - ⏳ Connection management and error handling

2. **IoT Control Tools** ⏳
   - ⏳ `control_tapo_light(device_name, action, params)`: Universal light control
   - ⏳ `list_tapo_devices()`: Discover and list available Tapo devices
   - ⏳ `set_light_color(device_name, color)`: RGB color control
   - ⏳ `set_light_brightness(device_name, level)`: Brightness adjustment
   - ⏳ Device state caching for faster responses

3. **Device Configuration** ⏳
   - ⏳ `.env` configuration for Tapo credentials (email/password)
   - ⏳ Device registry in `config.py` (device IPs, names, rooms)
   - ⏳ Scene configuration (preset lighting scenes)
   - ⏳ Schedule and automation rules storage

4. **Smart Home Features** ⏳
   - ⏳ Natural language device control ("turn on bedroom light")
   - ⏳ Room-based grouping ("turn off all living room lights")
   - ⏳ Scene activation ("set movie mode", "good morning scene")
   - ⏳ Contextual automation (time-based, event-triggered)
   - ⏳ Device status queries and feedback

5. **Future IoT Expansion** ⏳
   - ⏳ Support for Tapo smart plugs and power strips
   - ⏳ Camera integration (Tapo security cameras)
   - ⏳ Other smart home platforms (Philips Hue, LIFX, HomeKit)
   - ⏳ Cross-platform automation workflows
   - ⏳ Energy monitoring and optimization

6. **Error Handling & Reliability** ⏳
   - ⏳ Network timeout and retry logic
   - ⏳ Device offline detection and notifications
   - ⏳ Graceful degradation when devices unavailable
   - ⏳ Logging of device state changes
   - ⏳ Unit tests for IoT control functions

### End of Phase 1.5 Milestone: 🎯 TARGET
💡 Voice/text command → Device control → Real-time feedback → Smart scenes → Home automation → Gladys controls your environment

## Phase 2: Service Integration & Advanced Features ✓ Real-World Capabilities
**Goal**: Extend the agent with production-ready service integrations

### Components Completed:
1. **Rich TUI Integration** ✅
   - ✅ Syntax highlighting for code blocks
   - ✅ Formatted panels for agent responses
   - ✅ Loading spinners during API calls
   - ✅ Colorized tool call notifications
   - ✅ Enhanced user experience with visual feedback

2. **Google Services Integration** ✅
   - ✅ **Gmail Service**:
     - OAuth2 authentication flow
     - `access_gmail()`: Read and retrieve email messages
     - `send_mail_gmail()`: Compose and send emails from draft text
   - ✅ **Google Contacts Service**:
     - `get_google_contacts()`: Retrieve contact list with email addresses
     - `add_google_contacts()`: Add new contacts programmatically
   - ✅ Credential management and token persistence

3. **Browser Automation Service** ✅
   - ✅ `execute_browser_task()`: Selenium-based web automation
   - ✅ Integration with Browser Use + Gemini for intelligent browsing
   - ✅ Task-based browser operations (navigation, form filling, data extraction)
   - ✅ Separate requirements file for browser dependencies

4. **Extended Tool Ecosystem** ✅
   - ✅ Date/time utilities (`get_date`)
   - ✅ Email management (access, send)
   - ✅ Contact management (retrieve, add)
   - ✅ Web automation (browser tasks)
   - ✅ Extensible tool registry architecture

5. **Documentation & Configuration** ✅
   - ✅ Comprehensive README with service setup guides
   - ✅ Multiple requirements files for modular installation
   - ✅ OAuth credential configuration instructions
   - ✅ Architecture documentation with service integration patterns

### End of Phase 2 Milestone: ✅ COMPLETED
✅ Production-ready services → Gmail + Contacts + Browser automation → OAuth2 security → Extensible architecture → Real-world agent capabilities

## Phase 3: Voice Interface & Natural Interaction ⏳ Human-Like Communication
**Goal**: Enable natural voice-based interaction with speech-to-text and text-to-speech

### Components to Build:
1. **Speech-to-Text (STT) Integration** ⏳
   - ⏳ Integrate STT service (Whisper API, Google Speech-to-Text, or local Whisper)
   - ⏳ Audio input capture from microphone
   - ⏳ Real-time transcription pipeline
   - ⏳ Voice command detection and processing
   - ⏳ Hotword/wake word activation (optional)

2. **Text-to-Speech (TTS) Integration** ⏳
   - ⏳ Integrate TTS service (OpenAI TTS, Google Cloud TTS, or ElevenLabs)
   - ⏳ Streaming audio playback for agent responses
   - ⏳ Voice selection and customization
   - ⏳ Natural speech pacing and intonation
   - ⏳ Background audio management (pause/resume)

3. **Voice Interaction Flow** ⏳
   - ⏳ Hands-free conversation mode
   - ⏳ Voice command mode toggle (CLI vs Voice)
   - ⏳ Audio feedback for tool execution
   - ⏳ Interrupt handling (stop speaking, cancel action)
   - ⏳ Multi-modal input (text + voice simultaneously)

4. **Audio Processing & Quality** ⏳
   - ⏳ Noise reduction and audio preprocessing
   - ⏳ Voice activity detection (VAD)
   - ⏳ Automatic language detection
   - ⏳ Multi-language support (French, English, etc.)
   - ⏳ Audio format optimization

5. **Configuration & Dependencies** ⏳
   - ⏳ `requirements_voice.txt` for voice dependencies
   - ⏳ Audio device configuration and selection
   - ⏳ API key management for STT/TTS services
   - ⏳ Voice settings in `config.py` (voice selection, speed, pitch)
   - ⏳ Environment-specific audio drivers

6. **Enhanced UX for Voice** ⏳
   - ⏳ Visual indicators for listening/speaking states
   - ⏳ Waveform visualization during audio capture
   - ⏳ Transcription preview in real-time
   - ⏳ Voice command history and corrections
   - ⏳ Accessibility features (voice-only mode)

### End of Phase 3 Milestone: 🎯 TARGET
🎤 Voice input capture → Real-time STT transcription → Agent processing → Natural TTS output → Hands-free conversation → Seamless multi-modal interaction

## Phase 4: Animated Character & Visual Presence 💫 Meet Gladys
**Goal**: Create an engaging animated character (Gladys) with visual personality and emotional expressions

### Components to Build:
1. **Character Design & Asset Creation** ⏳
   - ⏳ Design Gladys character (2D/3D avatar, illustrations, or sprite-based)
   - ⏳ Create emotion states (idle, listening, speaking, thinking, happy, confused, etc.)
   - ⏳ Animation frames or rigging setup
   - ⏳ Lip-sync data generation for speech alignment
   - ⏳ Expression transitions and blending

2. **Animation Engine Integration** ⏳
   - ⏳ Choose animation framework (Pygame, Pyglet, or web-based with Electron)
   - ⏳ Render animated character window/overlay
   - ⏳ Real-time animation state machine
   - ⏳ Synchronize animations with agent states
   - ⏳ Smooth transitions between emotional states

3. **Emotional Intelligence & Expression Mapping** ⏳
   - ⏳ Sentiment analysis of agent responses
   - ⏳ Context-aware emotion selection (task success/failure, user tone, etc.)
   - ⏳ Expression triggers from conversation flow
   - ⏳ Personality consistency (Gladys's character traits)
   - ⏳ Custom emotion override commands

4. **Speech-Animation Synchronization** ⏳
   - ⏳ Lip-sync engine for TTS output
   - ⏳ Phoneme-to-viseme mapping
   - ⏳ Head movements and gestures during speech
   - ⏳ Idle animations between interactions
   - ⏳ Attention mechanisms (looking at user, screen focus)

5. **Interactive Character Features** ⏳
   - ⏳ Character position and window management
   - ⏳ User interaction callbacks (click, hover, drag)
   - ⏳ Character reactions to tool execution results
   - ⏳ Visual feedback for system states (loading, error, success)
   - ⏳ Customizable character appearance settings

6. **GUI Integration & Display** ⏳
   - ⏳ Separate character window with transparency/overlay
   - ⏳ Integration with Rich TUI (character alongside terminal)
   - ⏳ Web-based dashboard option (browser view with character)
   - ⏳ Multi-monitor support and positioning
   - ⏳ Minimize/maximize/hide character controls

7. **Performance & Optimization** ⏳
   - ⏳ Efficient rendering pipeline (GPU acceleration if needed)
   - ⏳ Resource management for animation assets
   - ⏳ Low-latency animation updates
   - ⏳ Fallback mode for systems without GUI support
   - ⏳ Configuration options for animation quality/performance

### End of Phase 4 Milestone: 🎯 TARGET
✨ Gladys comes alive → Animated visual presence → Emotion-aware expressions → Lip-synced speech → Interactive personality → Engaging human-computer interaction

