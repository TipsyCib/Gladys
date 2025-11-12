#!/usr/bin/env python3
"""Web-based GUI interface for Gladys using Gradio with PyAudio recording."""
import os
import sys
import threading
import time
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
import gradio as gr

# Load environment variables
load_dotenv(PROJECT_DIR / ".env")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")


class GladysGradioApp:
    """Gradio-based GUI application for Gladys chatbot."""

    def __init__(self):
        """Initialize the application."""
        self.agent = None
        self.messages = []
        self.whisper_processor = None
        self.whisper_model = None
        self.elevenlabs_client = None
        self.whisper_available = False
        self.tts_available = False
        self.use_voice_output = True
        self.is_recording = False
        self.recorded_audio = None

        # Initialize services
        self.initialize_services()

    def initialize_services(self):
        """Initialize agent and voice services."""
        try:
            print("Initialisation de l'agent...")
            self.agent = Agent()

            # Load conversation history
            self.messages = load_memory()
            print(f"Loaded History: {len(self.messages)} messages")

            # Initialize Whisper
            print("Loading Whisper...")
            self.whisper_available = self.setup_whisper()

            # Initialize ElevenLabs
            print("Loading ElevenLabs...")
            self.tts_available = self.setup_elevenlabs()

            print("All services are ready!")

        except Exception as e:
            print(f"Initialization error : {e}")
            sys.exit(1)

    def setup_whisper(self):
        """Initialize Whisper model for voice recognition."""
        try:
            self.whisper_processor = AutoProcessor.from_pretrained("openai/whisper-small")
            self.whisper_model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small")

            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.whisper_model = self.whisper_model.to(device)
            print(f"Whisper loaded on {device}")
            return True
        except Exception as e:
            print(f"Whisper error: {e}")
            return False

    def setup_elevenlabs(self):
        """Initialize ElevenLabs client for text-to-speech."""
        if ELEVENLABS_API_KEY:
            try:
                self.elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
                print("ElevenLabs activated")
                return True
            except Exception as e:
                print(f"ElevenLabs error: {e}")
                return False
        print("ElevenLabs disabled(no API key)")
        return False

    def record_audio_pyaudio(self, duration=5, sample_rate=16000):
        """Record audio from microphone using PyAudio."""
        try:
            mic = pyaudio.PyAudio()

            # Get default input device
            default_device = mic.get_default_input_device_info()
            print(f"Using microphone: {default_device['name']}")

            stream_audio = mic.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=1024
            )

            print(f"🎤 Recording ({duration}s)... Speak now!")
            frames = []

            for i in range(0, int(sample_rate / 1024 * duration)):
                data = stream_audio.read(1024, exception_on_overflow=False)
                frames.append(data)

            print("⏹️  Recording finished")
            stream_audio.stop_stream()
            stream_audio.close()
            mic.terminate()

            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_data = audio_data.astype(np.float32) / 32768.0

            return audio_data, sample_rate

        except Exception as e:
            print(f"Recording error: {e}")
            return None, sample_rate

    def transcribe_audio(self, audio_data, sample_rate=16000):
        """Transcribe audio to text using Whisper."""
        if self.whisper_processor is None or self.whisper_model is None:
            return ""

        try:
            inputs = self.whisper_processor(
                audio_data,
                sampling_rate=sample_rate,
                return_tensors="pt"
            )

            device = self.whisper_model.device
            inputs = {k: v.to(device) for k, v in inputs.items()}

            forced_decoder_ids = self.whisper_processor.get_decoder_prompt_ids(
                language="french",
                task="transcribe"
            )

            with torch.no_grad():
                generated_ids = self.whisper_model.generate(
                    inputs["input_features"],
                    forced_decoder_ids=forced_decoder_ids
                )

            transcription = self.whisper_processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]

            return transcription.strip()
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""

    def speak_text(self, text, voice_id="19STyYD15bswVz51nqLf"):
        """Speak text using ElevenLabs TTS."""
        if not self.elevenlabs_client or not self.use_voice_output:
            return

        try:
            audio_stream = self.elevenlabs_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2"
            )
            stream(audio_stream)
        except Exception as e:
            print(f"⚠️  Erreur TTS: {e}")

    def process_text_message(self, message, history):
        """Process text message and return response."""
        if not message or not message.strip():
            return history, ""

        try:
            # Process with agent
            self.messages, response = self.agent.process_message(self.messages, message)

            # Save memory
            save_memory(self.messages)

            # Speak if TTS enabled
            if self.use_voice_output and self.tts_available:
                threading.Thread(target=self.speak_text, args=(response,), daemon=True).start()

            # Update history
            history.append((message, response))

            return history, ""

        except Exception as e:
            error_msg = f"Erreur: {e}"
            history.append((message, error_msg))
            return history, ""

    def start_recording(self, history, duration_slider):
        """Start recording audio with PyAudio."""
        if not self.whisper_available:
            return history, "Speech recognition not available"

        try:
            status_msg = f"Recording in progress ({int(duration_slider)}s)... Speak now!"

            # Record audio
            audio_data, sample_rate = self.record_audio_pyaudio(duration=int(duration_slider))

            if audio_data is None:
                return history, "Recording error"

            # Transcribe
            status_msg = "Transcribing..."
            text = self.transcribe_audio(audio_data, sample_rate=sample_rate)

            if not text:
                return history, "No text detected, please speak closer to the mic and louder."

            # Process message
            self.messages, response = self.agent.process_message(self.messages, text)
            save_memory(self.messages)

            # Speak if TTS enabled
            if self.use_voice_output and self.tts_available:
                threading.Thread(target=self.speak_text, args=(response,), daemon=True).start()

            # Update history
            history.append((f"{text}", response))

            return history, f"Sent: {text}"

        except Exception as e:
            error_msg = f"Error: {e}"
            return history, error_msg

    def clear_conversation(self):
        """Clear conversation history."""
        self.messages = []
        save_memory(self.messages)
        return [], "History cleared"

    def toggle_voice_output(self, enabled):
        """Toggle voice output."""
        self.use_voice_output = enabled
        return f"Voice output: {'Enabled' if enabled else 'Disabled'}"

    def build_interface(self):
        """Build Gradio interface."""
        with gr.Blocks(
            title="Gladys - Your AI Assistant",
            theme=gr.themes.Soft(primary_hue="blue")
        ) as demo:
            gr.Markdown("# Gladys - Your AI Assistant")
            gr.Markdown("Chat with Gladys in text or voice mode")

            # Status
            status_md = gr.Markdown(self.get_status_text())

            # Main chat interface
            chatbot = gr.Chatbot(
                label="Conversation",
                height=450,
                show_copy_button=True
            )

            # Tabs for input modes
            with gr.Tabs():
                # Text mode
                with gr.Tab("Text Mode"):
                    with gr.Row():
                        text_input = gr.Textbox(
                            label="Your message",
                            placeholder="Type your message here...",
                            lines=3,
                            scale=4
                        )
                    with gr.Row():
                        text_btn = gr.Button("Send", variant="primary", scale=1)

                # Voice mode
                with gr.Tab("Voice Mode"):
                    gr.Markdown("### Recording instructions")
                    gr.Markdown("Click 'Record' and speak for the chosen duration")

                    duration_slider = gr.Slider(
                        minimum=3,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Recording Duration (seconds)",
                        interactive=True
                    )

                    voice_status = gr.Textbox(
                        label="Status",
                        value="Ready to record",
                        interactive=False
                    )

                    with gr.Row():
                        record_btn = gr.Button(
                            "Record and transcribe",
                            variant="primary",
                            size="lg"
                        )

            # Controls
            with gr.Row():
                voice_output_checkbox = gr.Checkbox(
                    label="Voice Output",
                    value=True,
                    interactive=self.tts_available
                )
                clear_btn = gr.Button("Clear History", variant="stop")

            # Voice output status
            voice_output_status = gr.Markdown(
                f"Voice Output: {'Enabled' if self.use_voice_output else 'Disabled'}"
            )

            # Event handlers
            text_btn.click(
                fn=self.process_text_message,
                inputs=[text_input, chatbot],
                outputs=[chatbot, text_input]
            )

            text_input.submit(
                fn=self.process_text_message,
                inputs=[text_input, chatbot],
                outputs=[chatbot, text_input]
            )

            record_btn.click(
                fn=self.start_recording,
                inputs=[chatbot, duration_slider],
                outputs=[chatbot, voice_status]
            )

            clear_btn.click(
                fn=self.clear_conversation,
                inputs=[],
                outputs=[chatbot, voice_status]
            )

            voice_output_checkbox.change(
                fn=self.toggle_voice_output,
                inputs=[voice_output_checkbox],
                outputs=[voice_output_status]
            )

            # Load history on start
            demo.load(
                fn=self.load_history,
                inputs=[],
                outputs=[chatbot]
            )

        return demo

    def get_status_text(self):
        """Get status text."""
        status = "**Status:** "
        features = []

        if self.whisper_available:
            features.append("Pyaudio Speech Recognition : OK")
        else:
            features.append("Pyaudio Speech Recognition : ERROR")

        if self.tts_available:
            features.append("Speech Synthesis (ElevenLabs) : OK")
        else:
            features.append("Speech Synthesis : ERROR")

        status += " | ".join(features)
        return status

    def load_history(self):
        """Load conversation history."""
        history = []

        # Convert messages to chat history format
        i = 0
        while i < len(self.messages):
            if i + 1 < len(self.messages):
                user_msg = self.messages[i]
                assistant_msg = self.messages[i + 1]

                if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                    history.append((
                        user_msg.get("content", ""),
                        assistant_msg.get("content", "")
                    ))
                    i += 2
                else:
                    i += 1
            else:
                i += 1

        return history

    def launch(self, share=True):
        """Launch the Gradio interface."""
        demo = self.build_interface()
        demo.launch(
            share=share,
            server_name="localhost",
            server_port=7860,
            show_error=True
        )


def main():
    """Main entry point."""
    print("=" * 60)
    print("  Gladys - Web Interface with PyAudio")
    print("  Powered by Mistral AI & Gradio")
    print("=" * 60)

    app = GladysGradioApp()
    app.launch(share=True)


if __name__ == "__main__":
    main()
