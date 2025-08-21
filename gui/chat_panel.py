import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import threading
import time
import os
from typing import Optional, Callable
from core.llm_manager import LLMManager
from core.project_generator import ProjectGenerator


class ChatPanel(ttk.Frame):
    """
    Enhanced chat panel with modern UI and project generation capabilities
    """

    def __init__(self, parent, llm_manager: LLMManager, project_generator: ProjectGenerator):
        super().__init__(parent)
        self.llm_manager = llm_manager
        self.project_generator = project_generator
        self.generating = False
        self.current_project = None

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        """Setup the user interface"""
        # Configure grid weights
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Top toolbar
        self.create_toolbar()

        # Chat area
        self.create_chat_area()

        # Steps area
        self.create_steps_area()

        # Bottom input area
        self.create_input_area()

        # Welcome message
        self.add_welcome_message()

    def create_toolbar(self):
        """Create top toolbar with controls"""
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

        # Left side - Project info
        project_frame = ttk.LabelFrame(toolbar, text="Current Project", padding=5)
        project_frame.pack(side='left', fill='x', expand=True)

        self.project_label = ttk.Label(project_frame, text="No project active")
        self.project_label.pack(side='left')

        # Right side - Controls
        controls_frame = ttk.Frame(toolbar)
        controls_frame.pack(side='right')

        ttk.Button(controls_frame, text="🗑️ Clear",
                   command=self.clear_chat).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="💾 Save Chat",
                   command=self.save_chat).pack(side='left', padx=2)
        ttk.Button(controls_frame, text="📁 Load Chat",
                   command=self.load_chat).pack(side='left', padx=2)

    def create_chat_area(self):
        """Create the main chat display area"""
        # Chat container with scrollbar
        chat_container = ttk.Frame(self)
        chat_container.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_columnconfigure(0, weight=1)

        # Chat text widget
        self.chat_text = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#f8f9fa',
            fg='#212529',
            insertbackground='#0078d4',
            selectbackground='#0078d4',
            selectforeground='white',
            padx=10,
            pady=10
        )
        self.chat_text.grid(row=0, column=0, sticky='nsew')

        # Configure text tags for styling
        self.setup_text_tags()

    def create_steps_area(self):
        """Create step-by-step progress area like BASE44/BOLT.NEW"""
        self.steps_container = ttk.LabelFrame(self, text="Build Steps", padding=5)
        self.steps_container.grid(row=1, column=1, sticky='ns', padx=(0, 5), pady=5)

        self.steps = [
            ("create_structure", "Creating project structure"),
            ("gradle_files", "Generating Gradle and settings files"),
            ("app_code", "Generating app source and resources"),
            ("readme", "Creating README"),
            ("sdk_check", "Checking Android SDK/JDK/Gradle"),
            ("gradle_sync", "Syncing Gradle dependencies"),
            ("assemble", "Building APK (assembleDebug)")
        ]

        self.step_vars = {}
        self.step_labels = {}

        for key, label in self.steps:
            var = tk.StringVar(value=f"⏳ {label}")
            self.step_vars[key] = var
            lbl = ttk.Label(self.steps_container, textvariable=var)
            lbl.pack(anchor='w')
            self.step_labels[key] = lbl

    def setup_text_tags(self):
        """Setup text styling tags"""
        # User messages
        self.chat_text.tag_configure("user",
                                     foreground="#0078d4",
                                     font=('Segoe UI', 10, 'bold'))

        # Assistant messages
        self.chat_text.tag_configure("assistant",
                                     foreground="#107c10",
                                     font=('Segoe UI', 10))

        # System messages
        self.chat_text.tag_configure("system",
                                     foreground="#666666",
                                     font=('Segoe UI', 9, 'italic'))

        # Code blocks
        self.chat_text.tag_configure("code",
                                     background="#f1f3f4",
                                     font=('Consolas', 9),
                                     relief='solid',
                                     borderwidth=1)

        # Error messages
        self.chat_text.tag_configure("error",
                                     foreground="#d83b01",
                                     font=('Segoe UI', 10, 'bold'))

        # Success messages
        self.chat_text.tag_configure("success",
                                     foreground="#107c10",
                                     font=('Segoe UI', 10, 'bold'))

    def create_input_area(self):
        """Create the input area at the bottom"""
        input_frame = ttk.Frame(self)
        input_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)

        # Input text widget
        self.input_text = tk.Text(
            input_frame,
            height=4,
            font=('Segoe UI', 10),
            wrap=tk.WORD,
            bg='white',
            fg='#212529',
            insertbackground='#0078d4',
            relief='solid',
            borderwidth=1
        )
        self.input_text.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        # Right side buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1, sticky='ns')

        self.send_button = ttk.Button(
            button_frame,
            text="🚀 Generate",
            command=self.send_message,
            style='Primary.TButton'
        )
        self.send_button.pack(fill='x', pady=2)

        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop",
            command=self.stop_generation,
            state='disabled'
        )
        self.stop_button.pack(fill='x', pady=2)

        # Project generation button
        self.generate_project_button = ttk.Button(
            button_frame,
            text="📱 Generate Project",
            command=self.generate_project,
            style='Success.TButton'
        )
        self.generate_project_button.pack(fill='x', pady=2)

    def setup_bindings(self):
        """Setup keyboard and event bindings"""
        # Enter to send (Shift+Enter for new line)
        self.input_text.bind('<Return>', self.on_return)
        self.input_text.bind('<Shift-Return>', self.on_shift_return)

        # Ctrl+Enter to send
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())

        # Focus on input when clicking in chat area
        self.chat_text.bind('<Button-1>', lambda e: self.input_text.focus())

    def add_welcome_message(self):
        """Add welcome message to chat"""
        welcome_text = """🤖 Welcome to Android App Generator!

I'm your AI assistant that can help you create complete Android applications. 
Here's what I can do:

📱 **Generate Complete Apps**: Describe your app idea and I'll create a full Android Studio project
🏗️ **Smart Architecture**: I'll design the best structure for your app
🎨 **Modern UI**: Generate beautiful Material Design interfaces
📊 **Database Integration**: Add Room database with proper data models
🌐 **API Integration**: Connect to web services and APIs
🔧 **Best Practices**: Follow Android development guidelines

**Quick Examples:**
• "Create a todo list app with add, edit, and delete functionality"
• "Build a weather app that shows current conditions and forecast"
• "Make a calculator app with scientific functions"

Just describe your app idea and I'll start generating! 🚀"""

        self.add_message("system", welcome_text)

    def add_message(self, role: str, content: str, code_blocks: list = None):
        """Add a message to the chat"""
        self.chat_text.configure(state='normal')

        # Add role indicator
        if role == "user":
            self.chat_text.insert(tk.END, "🧑 You: ", "user")
        elif role == "assistant":
            self.chat_text.insert(tk.END, "🤖 Assistant: ", "assistant")
        else:
            self.chat_text.insert(tk.END, "ℹ️ System: ", "system")

        # Add content with code highlighting
        if code_blocks:
            self.insert_content_with_code(content, code_blocks)
        else:
            self.chat_text.insert(tk.END, content + "\n\n", role)

        self.chat_text.configure(state='disabled')
        self.chat_text.see(tk.END)

    def insert_content_with_code(self, content: str, code_blocks: list):
        """Insert content with highlighted code blocks"""
        # Simple code block detection and highlighting
        lines = content.split('\n')
        in_code = False
        code_buffer = []

        for line in lines:
            if line.strip().startswith('```'):
                if in_code:
                    # End code block
                    if code_buffer:
                        code_text = '\n'.join(code_buffer)
                        self.chat_text.insert(tk.END, code_text + "\n", "code")
                    code_buffer = []
                    in_code = False
                else:
                    # Start code block
                    in_code = True
            elif in_code:
                code_buffer.append(line)
            else:
                # Regular text
                if line.strip():
                    self.chat_text.insert(tk.END, line + "\n")

        # Add final newlines
        self.chat_text.insert(tk.END, "\n")

    def on_return(self, event):
        """Handle Enter key press"""
        if not self.generating:
            self.send_message()
        return 'break'

    def on_shift_return(self, event):
        """Handle Shift+Enter for new line"""
        return None  # Allow default behavior

    def send_message(self):
        """Send the current message"""
        if self.generating:
            return

        message = self.input_text.get("1.0", tk.END).strip()
        if not message:
            return

        # Clear input
        self.input_text.delete("1.0", tk.END)

        # Add user message
        self.add_message("user", message)

        # Start generation
        self.start_generation(message)

    def start_generation(self, message: str):
        """Start the generation process"""
        try:
            self.generating = True
            self.send_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.generate_project_button.config(state='disabled')

            # Add thinking indicator
            self.chat_text.configure(state='normal')
            self.chat_text.insert(tk.END, "🤖 Assistant: ", "assistant")
            self.chat_text.insert(tk.END, "Thinking...", "system")
        except Exception as e:
            print(f"Error starting generation: {e}")
            self.generating = False
            self.send_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.generate_project_button.config(state='normal')
        self.chat_text.configure(state='disabled')
        self.chat_text.see(tk.END)

        # Start generation in background
        thread = threading.Thread(target=self._generate_worker, args=(message,), daemon=True)
        thread.start()

    def _generate_worker(self, message: str):
        """Background worker for generation with real-time streaming"""
        try:
            start_time = time.time()

            # Show "Thinking..." indicator
            self.chat_text.configure(state='normal')
            self.chat_text.insert(tk.END, "🤖 Assistant: ", "assistant")
            thinking_start = self.chat_text.index(tk.INSERT)
            self.chat_text.insert(tk.END, "Thinking...", "system")
            self.chat_text.configure(state='disabled')
            self.chat_text.see(tk.END)
            self.chat_text.update()

            # Prepare for streaming response
            response_tokens = []

            def token_callback(token):
                """Callback to handle incoming tokens in real-time"""
                try:
                    if not token:
                        return

                    response_tokens.append(token)

                    # Update UI in main thread
                    def update_ui():
                        try:
                            self.chat_text.configure(state='normal')

                            # Remove "Thinking..." on first token
                            if len(response_tokens) == 1:
                                # Find and remove the "Thinking..." text
                                current_pos = self.chat_text.search("Thinking...", thinking_start)
                                if current_pos:
                                    end_pos = f"{current_pos}+{len('Thinking...')}c"
                                    self.chat_text.delete(current_pos, end_pos)

                            # Add the new token
                            self.chat_text.insert(tk.END, token, "assistant")
                            self.chat_text.configure(state='disabled')
                            self.chat_text.see(tk.END)

                        except Exception as e:
                            print(f"Error updating UI: {e}")

                    # Schedule UI update in main thread
                    self.chat_text.after(0, update_ui)

                except Exception as e:
                    print(f"Error in token callback: {e}")

            # Generate response with streaming callback
            try:
                response = self.llm_manager.generate_response(
                    message,
                    callback=token_callback
                )
                print(f"LLM Response: '{response}'")

            except Exception as e:
                print(f"Error in LLM generation: {e}")
                # Remove "Thinking..." and show error
                def show_error():
                    self.chat_text.configure(state='normal')
                    current_pos = self.chat_text.search("Thinking...", thinking_start)
                    if current_pos:
                        end_pos = f"{current_pos}+{len('Thinking...')}c"
                        self.chat_text.delete(current_pos, end_pos)
                    self.chat_text.insert(tk.END, f"Error: {str(e)}", "error")
                    self.chat_text.configure(state='disabled')
                    self.chat_text.see(tk.END)

                self.chat_text.after(0, show_error)

            # Add final timing info
            def add_timing():
                elapsed = time.time() - start_time
                self.chat_text.configure(state='normal')
                self.chat_text.insert(tk.END, f"\n\n⏱️ Generated in {elapsed:.1f}s\n\n", "system")
                self.chat_text.configure(state='disabled')
                self.chat_text.see(tk.END)

            self.chat_text.after(0, add_timing)

        except Exception as e:
            print(f"Error in generation worker: {e}")
            def show_final_error():
                self.chat_text.configure(state='normal')
                self.chat_text.insert(tk.END, f"\n\nError during generation: {str(e)}\n\n", "error")
                self.chat_text.configure(state='disabled')
                self.chat_text.see(tk.END)

            self.chat_text.after(0, show_final_error)
        finally:
            # Schedule generation finished in main thread
            self.chat_text.after(0, self.generation_finished)

    def stop_generation(self):
        """Stop the current generation"""
        self.llm_manager.stop_generation()
        self.add_message("system", "Generation stopped by user.")
        self.generation_finished()

    def generation_finished(self):
        """Called when generation is finished"""
        self.generating = False
        self.send_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.generate_project_button.config(state='normal')

    def generate_project(self):
        """Generate a complete Android project from chat history"""
        # Allow project generation even if model not loaded
        if not self.llm_manager.is_initialized:
            try:
                self.llm_manager.initialize()
            except Exception:
                pass

        # Get project description from user
        project_name = tk.simpledialog.askstring(
            "Project Name",
            "Enter a name for your Android project:",
            parent=self
        )

        if not project_name:
            return

        # Get output directory
        output_dir = filedialog.askdirectory(
            title="Select output directory for the project"
        )

        if not output_dir:
            return

        # Start project generation
        self.start_project_generation(project_name, output_dir)

    def start_project_generation(self, project_name: str, output_dir: str):
        """Start the project generation process"""
        self.generating = True
        self.send_button.config(state='disabled')
        self.generate_project_button.config(state='disabled')

        self.add_message("system", f"🚀 Starting project generation: {project_name}")

        # Start generation in background
        thread = threading.Thread(
            target=self._project_generation_worker,
            args=(project_name, output_dir),
            daemon=True
        )
        thread.start()

    def _project_generation_worker(self, project_name: str, output_dir: str):
        """Background worker for project generation"""
        try:
            # Get chat history for context
            chat_history = self.get_chat_history()

            # UI step updates helper
            def ui_step_update(step_key: str, message: str, phase: str):
                def _do():
                    # Create dynamic label if unknown step (e.g., file creations)
                    if step_key not in self.step_vars:
                        var = tk.StringVar(value=f"⏳ {message}")
                        lbl = ttk.Label(self.steps_container, textvariable=var)
                        lbl.pack(anchor='w')
                        self.step_vars[step_key] = var
                        self.step_labels[step_key] = lbl

                    if phase == 'start':
                        self.step_vars[step_key].set(f"⏳ {message}")
                    elif phase == 'done':
                        self.step_vars[step_key].set(f"✅ {message}")
                    elif phase == 'error':
                        self.step_vars[step_key].set(f"❌ {message}")
                self.chat_text.after(0, _do)

            # Reset steps to pending
            for key, label in self.steps:
                ui_step_update(key, label, 'start')

            # Generate project with progress callback
            result = self.project_generator.generate_project(
                project_name=project_name,
                description=chat_history,
                output_dir=output_dir,
                progress_callback=ui_step_update
            )

            if result['success']:
                self.add_message("success",
                                 f"✅ Project generated successfully!\n"
                                 f"📁 Location: {result['project_path']}\n"
                                 f"📱 Building APK...")

                # Update current project
                self.current_project = result['project_path']
                self.project_label.config(text=f"Active: {project_name}")

                # After generation, kick off APK build
                self._build_apk_worker(result['project_path'], ui_step_update)

            else:
                self.add_message("error", f"❌ Project generation failed: {result['error']}")

        except Exception as e:
            self.add_message("error", f"❌ Error during project generation: {str(e)}")
        finally:
            self.generation_finished()

    def _build_apk_worker(self, project_path: str, ui_step_update: Callable[[str, str, str], None]):
        """Check/install Android tools and build APK sequentially"""
        def worker():
            try:
                # Lazy import to avoid GUI import cost
                from core.android_builder import AndroidBuilder
                builder = AndroidBuilder()

                ui_step_update('sdk_check', 'Checking Android SDK/JDK/Gradle', 'start')
                builder.ensure_tools()
                ui_step_update('sdk_check', 'Checking Android SDK/JDK/Gradle', 'done')

                ui_step_update('gradle_sync', 'Syncing Gradle dependencies', 'start')
                builder.gradle_sync(project_path)
                ui_step_update('gradle_sync', 'Syncing Gradle dependencies', 'done')

                ui_step_update('assemble', 'Building APK (assembleDebug)', 'start')
                apk_path = builder.assemble_debug(project_path)
                ui_step_update('assemble', 'Building APK (assembleDebug)', 'done')

                self.add_message('success', f"📦 APK ready: {apk_path}")
            except Exception as e:
                ui_step_update('assemble', f"Build failed: {e}", 'error')
                self.add_message('error', f"❌ Build failed: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def get_chat_history(self) -> str:
        """Extract chat history for project generation"""
        # Get all messages from chat
        content = self.chat_text.get("1.0", tk.END)

        # Filter to get user messages and assistant responses
        lines = content.split('\n')
        history = []

        for line in lines:
            if line.strip().startswith('🧑 You:'):
                history.append(line.replace('🧑 You:', 'User:').strip())
            elif line.strip().startswith('🤖 Assistant:'):
                history.append(line.replace('🤖 Assistant:', 'Assistant:').strip())

        return '\n'.join(history)

    def set_prompt(self, prompt: str):
        """Set a prompt in the input field"""
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert("1.0", prompt)
        self.input_text.focus()

    def clear_chat(self):
        """Clear the chat history"""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
            self.chat_text.configure(state='normal')
            self.chat_text.delete("1.0", tk.END)
            self.chat_text.configure(state='disabled')
            self.add_welcome_message()

    def save_chat(self):
        """Save chat history to file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                content = self.chat_text.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", "Chat history saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save chat: {str(e)}")

    def load_chat(self):
        """Load chat history from file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()

                self.chat_text.configure(state='normal')
                self.chat_text.delete("1.0", tk.END)
                self.chat_text.insert("1.0", content)
                self.chat_text.configure(state='disabled')
                self.chat_text.see(tk.END)

                messagebox.showinfo("Success", "Chat history loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load chat: {str(e)}")