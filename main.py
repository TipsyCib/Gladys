#!/usr/bin/env python3
"""Main CLI entry point for the agentic chatbot."""
import sys
import os
import numpy as np
import pyaudio
import torch
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from elevenlabs import stream
from elevenlabs.client import ElevenLabs
from agent import Agent
from memory import load_memory, save_memory
from config import PROJECT_DIR
from dotenv import load_dotenv

# Load environment variables
load_dotenv(PROJECT_DIR / ".env")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Global variables for voice features
whisper_processor = None
whisper_model = None
elevenlabs_client = None


def print_help():
    """Print help message."""
    print("""
Available commands:
  /help    - Show this help message
  /clear   - Clear conversation history
  /exit    - Exit the chatbot
  /quit    - Exit the chatbot
  /voice   - Enable voice input mode
  /text    - Enable text input mode

Just type your message to chat with the agent!
    """)


def setup_whisper():
    """Initialize Whisper model for voice recognition."""
    global whisper_processor, whisper_model

    try:
        print("Loading Whisper model (this may take a moment)...")
        whisper_processor = AutoProcessor.from_pretrained("openai/whisper-small")
        whisper_model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small")

        # Use GPU if available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        whisper_model = whisper_model.to(device)

        print(f"✅ Whisper model loaded on {device}")
        return True
    except Exception as e:
        print(f"❌ Error loading Whisper: {e}")
        return False


def setup_elevenlabs():
    """Initialize ElevenLabs client for text-to-speech."""
    global elevenlabs_client

    if ELEVENLABS_API_KEY:
        try:
            elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
            print("✅ ElevenLabs TTS enabled")
            return True
        except Exception as e:
            print(f"❌ Error initializing ElevenLabs: {e}")
            return False
    else:
        print("⚠️  ELEVENLABS_API_KEY not found - TTS disabled")
        return False


def record_audio(duration=5, sample_rate=16000):
    """Record audio from microphone."""
    mic = pyaudio.PyAudio()
    stream_audio = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=sample_rate,
        input=True,
        frames_per_buffer=1024
    )

    print(f"🎤 Listening ({duration}s)... Speak now!")

    frames = []
    for _ in range(0, int(sample_rate / 1024 * duration)):
        data = stream_audio.read(1024, exception_on_overflow=False)
        frames.append(data)

    print("⏹️  Recording finished")

    stream_audio.stop_stream()
    stream_audio.close()
    mic.terminate()

    # Convert to numpy array
    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
    audio_data = audio_data.astype(np.float32) / 32768.0  # Normalize

    return audio_data


def transcribe_audio(audio_data, sample_rate=16000):
    """Transcribe audio to text using Whisper."""
    if whisper_processor is None or whisper_model is None:
        return ""

    try:
        # Prepare input
        inputs = whisper_processor(
            audio_data,
            sampling_rate=sample_rate,
            return_tensors="pt"
        )

        # Move to same device as model
        device = whisper_model.device
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Force English language
        forced_decoder_ids = whisper_processor.get_decoder_prompt_ids(language="french", task="transcribe")

        # Generate transcription
        with torch.no_grad():
            generated_ids = whisper_model.generate(
                inputs["input_features"],
                forced_decoder_ids=forced_decoder_ids
            )

        # Decode
        transcription = whisper_processor.batch_decode(
            generated_ids,
            skip_special_tokens=True
        )[0]

        return transcription.strip()
    except Exception as e:
        print(f"❌ Error transcribing audio: {e}")
        return ""


def listen_microphone():
    """Listen to microphone and return recognized text."""
    audio_data = record_audio(duration=5)
    text = transcribe_audio(audio_data)
    return text


def speak_text(text, voice_id="19STyYD15bswVz51nqLf"):
    """Speak text using ElevenLabs TTS."""
    if not elevenlabs_client:
        return

    try:
        audio_stream = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id="eleven_multilingual_v2"
        )
        stream(audio_stream)
    except Exception as e:
        print(f"⚠️  Error with TTS: {e}")


def get_user_input(use_voice=False, whisper_available=False):
    """Get user input via text or voice."""
    if use_voice and whisper_available:
        print("\n[Press Ctrl+C to type instead of speaking]")
        try:
            text = listen_microphone()
            print(f"\nYou (voice): {text}")
            return text
        except KeyboardInterrupt:
            print("\n[Keyboard mode enabled for this message]")
            return input("\nYou: ")
    else:
        return input("You: ")


def main():
    """Main CLI chat loop."""
    print("=" * 60)
    print("  Gladys CLI")
    print("  Powered by Mistral AI")
    print("=" * 60)
    print("\nType /help for commands, /exit to quit\n")

    # Initialize agent
    try:
        agent = Agent()
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease set MISTRAL_API_KEY environment variable:")
        print("  export MISTRAL_API_KEY='your-api-key'")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing agent: {e}")
        sys.exit(1)

    # Initialize voice features
    print("\nInitializing voice features...")
    whisper_available = setup_whisper()
    tts_available = setup_elevenlabs()

    print("\n" + "=" * 60)
    if whisper_available:
        print("✅ Voice recognition enabled (Whisper)")
        use_voice = False  # Start with text mode by default
    else:
        print("⚠️  Voice recognition disabled")
        use_voice = False

    if tts_available:
        print("✅ Text-to-speech enabled (ElevenLabs)")
    else:
        print("⚠️  Text-to-speech disabled")
    print("=" * 60)

    # Load conversation history
    messages = load_memory()
    if messages:
        print(f"[Loaded {len(messages)} messages from previous session]\n")

    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = get_user_input(use_voice, whisper_available).strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command in ["/exit", "/quit"]:
                    print("\nSaving conversation and exiting...")
                    save_memory(messages)
                    print("Goodbye!")
                    break

                elif command == "/help":
                    print_help()
                    continue

                elif command == "/clear":
                    messages = []
                    save_memory(messages)
                    print("[Conversation history cleared]\n")
                    continue

                elif command == "/voice" and whisper_available:
                    use_voice = True
                    print("🎤 Voice input mode enabled\n")
                    continue

                elif command == "/text":
                    use_voice = False
                    print("⌨️  Text input mode enabled\n")
                    continue

                else:
                    print(f"Unknown command: {user_input}")
                    print("Type /help for available commands\n")
                    continue

            # Process message with agent
            try:
                messages, response = agent.process_message(messages, user_input)
                print(f"\nGladys: {response}\n")

                # Speak the response if TTS is available
                if tts_available:
                    speak_text(response)

                # Save after each interaction
                save_memory(messages)

            except Exception as e:
                print(f"\nError processing message: {e}\n")
                # Continue the loop even if there's an error

        except KeyboardInterrupt:
            print("\n\nInterrupted. Saving conversation...")
            save_memory(messages)
            print("Goodbye!")
            break

        except EOFError:
            print("\n\nSaving conversation...")
            save_memory(messages)
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
