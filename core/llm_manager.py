import os
import urllib.request
import threading
import time
from typing import Optional, Callable, Dict, Any, List
from gpt4all import GPT4All
import json
import traceback
import gpt4all


class LLMManager:
    """
    Manages local LLM models with enhanced capabilities for Android app generation
    """

    def __init__(self):
        # Configuration
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.models_dir = os.path.join(self.base_dir, "models")
        self.config_file = os.path.join(self.base_dir, "config", "llm_config.json")

        # Model settings - use a smaller, proven working model from GPT4All official repo
        self.model_name = "orca-mini-3b-gguf2-q4_0.gguf"
        self.model_url = "https://gpt4all.io/models/gguf/orca-mini-3b-gguf2-q4_0.gguf"
        self.model_path = os.path.join(self.models_dir, self.model_name)

        # Backup model if primary fails
        self.backup_model_name = "mistral-7b-instruct-v0.1.Q4_0.gguf"
        self.backup_model_url = "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf"
        self.backup_model_path = os.path.join(self.models_dir, self.backup_model_name)

        # Model instance
        self.model: Optional[GPT4All] = None
        self.is_initialized = False
        self.is_generating = False
        self.should_stop = False

        # Generation settings - optimized for small model
        self.default_params = {
            'max_tokens': 1024,  # Reduced for small model
            'temp': 0.1,
            'top_p': 0.95,
            'repeat_penalty': 1.1,
            'streaming': True
        }

        # System prompts for different tasks - optimized for small model
        self.system_prompts = {
            'default': self._get_default_prompt(),
            'android': self._get_android_prompt(),
            'architecture': self._get_architecture_prompt(),
            'code_review': self._get_code_review_prompt(),
            'debugging': self._get_debugging_prompt()
        }

        # Conversation history
        self.conversation_history = []
        self.max_history_length = 5  # Reduced for small model

        # Create directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)

    def _get_default_prompt(self) -> str:
        """Get default system prompt - optimized for small model"""
        return """You are a helpful AI coding assistant specialized in Android development.

Your capabilities:
- Generate Android applications in Kotlin
- Design Material Design UIs
- Implement basic Room databases
- Create simple REST API integrations
- Follow Android best practices

Keep responses concise and focused on one task at a time."""

    def _get_android_prompt(self) -> str:
        """Get Android-specific system prompt - optimized for small model"""
        return """You are an Android developer. Generate Android applications.

Focus on:
- Kotlin development
- Material Design components
- Basic MVVM architecture
- Simple Room database
- Basic error handling

Keep responses focused and practical."""

    def _get_architecture_prompt(self) -> str:
        """Get architecture design prompt - optimized for small model"""
        return """You are a software architect for Android applications.

Design:
- Simple, maintainable architecture
- Clear component separation
- Basic patterns
- File structure

Keep responses concise and actionable."""

    def _get_code_review_prompt(self) -> str:
        """Get code review prompt - optimized for small model"""
        return """You are an Android developer reviewing code.

Review for:
- Basic code quality
- Common issues
- Android best practices
- Simple improvements

Keep feedback focused and actionable."""

    def _get_debugging_prompt(self) -> str:
        """Get debugging prompt - optimized for small model"""
        return """You are a debugging expert for Android applications.

Analyze:
- Error messages
- Common issues
- Simple solutions
- Prevention tips

Keep responses practical and focused."""

    def initialize(self) -> bool:
        """Initialize the LLM manager"""
        try:
            # Load configuration first
            self._load_config()

            # Don't load model automatically - let user do it manually
            # This prevents segmentation faults during startup
            self.is_initialized = True
            return True

        except Exception as e:
            print(f"Failed to initialize LLM manager: {e}")
            self.is_initialized = False
            return False

    def _model_exists(self) -> bool:
        """Check if model file exists"""
        return os.path.exists(self.model_path)

    def _backup_model_exists(self) -> bool:
        """Check if backup model file exists"""
        return os.path.exists(self.backup_model_path)

    def _download_model(self):
        """Download the model file"""
        print(f"Downloading model from {self.model_url}...")

        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)

        # Download with progress
        try:
            with urllib.request.urlopen(self.model_url) as response, open(self.model_path, 'wb') as out_file:
                total_length = response.length or 0
                downloaded = 0
                chunk_size = 8192

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    out_file.write(chunk)
                    downloaded += len(chunk)

                    if total_length:
                        percent = int(downloaded * 100 / total_length)
                        print(f"\rDownloading: {percent}%", end="")

            print("\nModel downloaded successfully.")

        except Exception as e:
            print(f"Failed to download model: {e}")
            raise

    def _download_backup_model(self):
        """Download the backup model file"""
        print(f"Downloading backup model from {self.backup_model_url}...")

        # Create models directory
        os.makedirs(self.models_dir, exist_ok=True)

        # Download with progress
        try:
            with urllib.request.urlopen(self.backup_model_url) as response, open(self.backup_model_path, 'wb') as out_file:
                total_length = response.length or 0
                downloaded = 0
                chunk_size = 8192

                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break

                    out_file.write(chunk)
                    downloaded += len(chunk)

                    if total_length:
                        percent = int(downloaded * 100 / total_length)
                        print(f"\rDownloading backup model: {percent}%", end="")

            print("\nBackup model downloaded successfully.")

        except Exception as e:
            print(f"Failed to download backup model: {e}")
            raise

    def _load_model(self):
        """Load the GPT4All model with diagnostics and full traceback on error"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        # Diagnostics: print file info
        try:
            file_size = os.path.getsize(self.model_path)
            can_read = os.access(self.model_path, os.R_OK)
            print(f"Model file found: {self.model_path}")
            print(f"Model file size: {file_size} bytes")
            print(f"Model file readable: {can_read}")
            print(f"gpt4all version: {gpt4all.__version__ if hasattr(gpt4all, '__version__') else 'unknown'}")
        except Exception as diag_e:
            print(f"Could not check model file properties: {diag_e}")

        print("Loading model...")
        try:
            # Use the new GPT4All API
            self.model = GPT4All(self.model_name, model_path=self.models_dir)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load model: {e}")
            traceback.print_exc()
            print("Possible causes:")
            print("- Model file is corrupted or incomplete")
            print("- Model format is not supported by your gpt4all version")
            print("- File permissions issue")
            print("- Insufficient system memory")
            print("Suggestions:")
            print("1. Delete the model file and restart to re-download it.")
            print("2. Try a different GGUF model file.")
            print("3. Upgrade the gpt4all Python package.")
            print("4. Check available system memory.")
            self.model = None
            raise Exception(f"Model loading failed: {str(e)}")

    def _load_backup_model(self):
        """Load the backup GPT4All model if primary model fails"""
        if not os.path.exists(self.backup_model_path):
            raise FileNotFoundError(f"Backup model file not found: {self.backup_model_path}")

        print("Loading backup model...")
        try:
            # Use the new GPT4All API
            self.model = GPT4All(self.backup_model_name, model_path=self.models_dir)
            print("Backup model loaded successfully.")
        except Exception as e:
            print(f"Failed to load backup model: {e}")
            traceback.print_exc()
            raise Exception(f"Backup model loading failed: {str(e)}")

    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.default_params.update(config.get('generation_params', {}))
            except Exception as e:
                print(f"Failed to load config: {e}")

    def _save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'generation_params': self.default_params,
                'model_path': self.model_path,
                'last_updated': time.time()
            }

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            print(f"Failed to save config: {e}")

    def is_ready(self) -> bool:
        """Check if the model is ready for use"""
        return self.is_initialized and self.model is not None

    def load_model(self) -> bool:
        """Load the model on-demand with automatic model selection"""
        try:
            if self.model is not None:
                return True  # Already loaded

            print("Loading model using GPT4All automatic model selection...")

            # Try to use GPT4All's built-in model downloading
            # This will automatically download a compatible model
            try:
                # Use GPT4All's default model which is automatically downloaded
                self.model = GPT4All()  # No model name - uses default
                print("Default GPT4All model loaded successfully.")
                self.model_name = "default_gpt4all_model"
                return True

            except Exception as e:
                print(f"Failed to load default model: {e}")

                # Fallback: try specific known working models
                known_models = [
                    "orca-mini-3b-gguf2-q4_0.gguf",
                    "gpt4all-falcon-q4_0.gguf",
                    "wizardlm-13b-v1.2.q4_0.gguf"
                ]

                for model_name in known_models:
                    try:
                        print(f"Trying to load {model_name}...")
                        self.model = GPT4All(model_name, model_path=self.models_dir, allow_download=True)
                        print(f"Model {model_name} loaded successfully.")
                        self.model_name = model_name
                        return True
                    except Exception as model_e:
                        print(f"Failed to load {model_name}: {model_e}")
                        continue

                return False

        except Exception as e:
            print(f"Failed to load any model: {e}")
            return False

    def generate_response(self,
                          message: str,
                          prompt_type: str = 'default',
                          callback: Optional[Callable[[str], None]] = None,
                          **kwargs) -> str:
        """Generate a response from the model with real streaming"""
        print(f"[DEBUG] Generate response called with message: '{message}'")

        if not self.is_initialized:
            print("[DEBUG] LLM Manager not initialized")
            raise RuntimeError("LLM Manager is not initialized. Call initialize() first.")

        # Try to load model if not already loaded
        if self.model is None:
            print("[DEBUG] Model is None, attempting to load...")
            if not self.load_model():
                print("[DEBUG] Failed to load model")
                raise RuntimeError("Failed to load model. Please check if the model file exists.")

        if self.is_generating:
            print("[DEBUG] Generation already in progress")
            raise RuntimeError("Generation already in progress.")

        self.is_generating = True
        self.should_stop = False

        try:
            print("[DEBUG] Starting generation process...")
            # Build prompt
            system_prompt = self.system_prompts.get(prompt_type, self.system_prompts['default'])

            # Simple prompt format for better streaming
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nAssistant:"

            print(f"[DEBUG] Full prompt: '{full_prompt}'")

            # Generate response with streaming enabled
            print("[DEBUG] Calling model.generate with streaming...")

            # Collect tokens as they arrive
            collected_tokens = []

            # Use GPT4All's streaming functionality
            with self.model.chat_session():
                for token in self.model.generate(
                    full_prompt,
                    max_tokens=self.default_params['max_tokens'],
                    temp=self.default_params['temp'],
                    top_p=self.default_params['top_p'],
                    repeat_penalty=self.default_params['repeat_penalty'],
                    streaming=True  # Enable streaming
                ):
                    if self.should_stop:
                        break

                    # Send token to callback immediately
                    if callback and token:
                        callback(token)

                    collected_tokens.append(token)

            # Join all collected tokens
            response = ''.join(collected_tokens).strip()

            print(f"[DEBUG] Final streamed response: '{response}'")

            # Update conversation history
            self.conversation_history.append(f"User: {message}")
            self.conversation_history.append(f"Assistant: {response}")

            # Keep history manageable
            if len(self.conversation_history) > self.max_history_length * 2:
                self.conversation_history = self.conversation_history[-self.max_history_length * 2:]

            if not response:
                response = "Sorry, I couldn't generate a response. Try again or reload the model."

            return response

        except Exception as e:
            print(f"[DEBUG] Exception during generation: {e}")
            import traceback
            traceback.print_exc()

            # Send error to callback if provided
            if callback:
                callback(f"\n\nError: {str(e)}")

            return f"Error during generation: {str(e)}"
        finally:
            self.is_generating = False

    def generate_stream(self, prompt: str) -> str:
        """Compatibility wrapper for agent system expecting a streaming API.

        For small models we disable streaming and return a full string response.
        This method simply routes to generate_response with the default prompt.
        """
        # Ensure initialization and model readiness will be handled inside generate_response
        return self.generate_response(prompt, prompt_type='default')

    def set_generation_params(self,
                              max_tokens: Optional[int] = None,
                              temp: Optional[float] = None,
                              top_p: Optional[float] = None,
                              repeat_penalty: Optional[float] = None) -> Dict[str, Any]:
        """Update generation parameters and persist to config."""
        if max_tokens is not None:
            self.default_params['max_tokens'] = int(max_tokens)
        if temp is not None:
            self.default_params['temp'] = float(temp)
        if top_p is not None:
            self.default_params['top_p'] = float(top_p)
        if repeat_penalty is not None:
            self.default_params['repeat_penalty'] = float(repeat_penalty)
        self._save_config()
        return self.default_params.copy()

    def set_model_path(self, model_path: str) -> bool:
        """Set a custom model file path and unload current model."""
        try:
            if not model_path:
                return False
            # Unload current model if loaded
            if self.model is not None:
                try:
                    del self.model
                except Exception:
                    pass
                self.model = None

            self.model_path = model_path
            self.model_name = os.path.basename(model_path)
            self.models_dir = os.path.dirname(model_path) or self.models_dir
            self._save_config()
            return True
        except Exception:
            return False

    def unload_model(self):
        """Unload the current model from memory."""
        if self.model is not None:
            try:
                del self.model
            except Exception:
                pass
            self.model = None

    def stop_generation(self):
        """Stop the current generation"""
        self.should_stop = True
        self.is_generating = False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        if self.model is None:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "name": self.model_name,
            "path": self.model_path,
            "ready": self.is_ready()
        }

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            return GPT4All.list_models()
        except Exception as e:
            print(f"Failed to get available models: {e}")
            return []

    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model"""
        try:
            # Unload current model
            if self.model is not None:
                del self.model
                self.model = None

            # Update model name and path
            self.model_name = model_name
            self.model_path = os.path.join(self.models_dir, model_name)

            # Load new model
            return self.load_model()

        except Exception as e:
            print(f"Failed to switch model: {e}")
            return False
