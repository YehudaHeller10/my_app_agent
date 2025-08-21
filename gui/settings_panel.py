import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict, Any
from core.llm_manager import LLMManager


class SettingsPanel(ttk.Frame):
    """
    Settings panel for configuring the application
    """

    def __init__(self, parent, llm_manager: LLMManager):
        super().__init__(parent)
        self.llm_manager = llm_manager
        self.settings_file = "settings.json"
        self.settings = self.load_default_settings()

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the user interface"""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create notebook for different settings categories
        self.create_settings_notebook()

        # Bottom buttons
        self.create_bottom_buttons()

    def create_settings_notebook(self):
        """Create notebook with different settings tabs"""
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

        # Create tabs
        self.create_model_settings_tab()
        self.create_project_settings_tab()
        self.create_ui_settings_tab()
        self.create_advanced_settings_tab()

    def create_model_settings_tab(self):
        """Create model settings tab"""
        model_frame = ttk.Frame(self.notebook)
        self.notebook.add(model_frame, text="🤖 AI Model")

        # Model configuration
        model_config_frame = ttk.LabelFrame(model_frame, text="Model Configuration", padding=10)
        model_config_frame.pack(fill='x', padx=10, pady=5)

        # Model path
        ttk.Label(model_config_frame, text="Model Path:").grid(row=0, column=0, sticky='w', pady=2)
        self.model_path_var = tk.StringVar()
        model_path_entry = ttk.Entry(model_config_frame, textvariable=self.model_path_var, width=50)
        model_path_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(model_config_frame, text="Browse", command=self.browse_model_path).grid(row=0, column=2, pady=2)

        # Model status
        ttk.Label(model_config_frame, text="Status:").grid(row=1, column=0, sticky='w', pady=2)
        self.model_status_label = ttk.Label(model_config_frame, text="Unknown")
        self.model_status_label.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Generation parameters
        gen_params_frame = ttk.LabelFrame(model_frame, text="Generation Parameters", padding=10)
        gen_params_frame.pack(fill='x', padx=10, pady=5)

        # Max tokens
        ttk.Label(gen_params_frame, text="Max Tokens:").grid(row=0, column=0, sticky='w', pady=2)
        self.max_tokens_var = tk.IntVar(value=2048)
        max_tokens_spin = ttk.Spinbox(gen_params_frame, from_=512, to=8192, textvariable=self.max_tokens_var, width=10)
        max_tokens_spin.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Temperature
        ttk.Label(gen_params_frame, text="Temperature:").grid(row=1, column=0, sticky='w', pady=2)
        self.temperature_var = tk.DoubleVar(value=0.1)
        temp_scale = ttk.Scale(gen_params_frame, from_=0.0, to=2.0, variable=self.temperature_var, orient='horizontal')
        temp_scale.grid(row=1, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(gen_params_frame, textvariable=self.temperature_var).grid(row=1, column=2, padx=5, pady=2)

        # Top-p
        ttk.Label(gen_params_frame, text="Top-p:").grid(row=2, column=0, sticky='w', pady=2)
        self.top_p_var = tk.DoubleVar(value=0.95)
        top_p_scale = ttk.Scale(gen_params_frame, from_=0.0, to=1.0, variable=self.top_p_var, orient='horizontal')
        top_p_scale.grid(row=2, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(gen_params_frame, textvariable=self.top_p_var).grid(row=2, column=2, padx=5, pady=2)

        # Repeat penalty
        ttk.Label(gen_params_frame, text="Repeat Penalty:").grid(row=3, column=0, sticky='w', pady=2)
        self.repeat_penalty_var = tk.DoubleVar(value=1.1)
        repeat_penalty_scale = ttk.Scale(gen_params_frame, from_=1.0, to=2.0, variable=self.repeat_penalty_var,
                                         orient='horizontal')
        repeat_penalty_scale.grid(row=3, column=1, sticky='ew', padx=5, pady=2)
        ttk.Label(gen_params_frame, textvariable=self.repeat_penalty_var).grid(row=3, column=2, padx=5, pady=2)

        # Configure grid weights
        model_config_frame.grid_columnconfigure(1, weight=1)
        gen_params_frame.grid_columnconfigure(1, weight=1)

    def create_project_settings_tab(self):
        """Create project settings tab"""
        project_frame = ttk.Frame(self.notebook)
        self.notebook.add(project_frame, text="📱 Project")

        # Project configuration
        project_config_frame = ttk.LabelFrame(project_frame, text="Project Configuration", padding=10)
        project_config_frame.pack(fill='x', padx=10, pady=5)

        # Default output directory
        ttk.Label(project_config_frame, text="Default Output Directory:").grid(row=0, column=0, sticky='w', pady=2)
        self.output_dir_var = tk.StringVar()
        output_dir_entry = ttk.Entry(project_config_frame, textvariable=self.output_dir_var, width=50)
        output_dir_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=2)
        ttk.Button(project_config_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=2, pady=2)

        # Android SDK settings
        android_frame = ttk.LabelFrame(project_frame, text="Android SDK Settings", padding=10)
        android_frame.pack(fill='x', padx=10, pady=5)

        # Min SDK
        ttk.Label(android_frame, text="Minimum SDK:").grid(row=0, column=0, sticky='w', pady=2)
        self.min_sdk_var = tk.IntVar(value=24)
        min_sdk_spin = ttk.Spinbox(android_frame, from_=16, to=34, textvariable=self.min_sdk_var, width=10)
        min_sdk_spin.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Target SDK
        ttk.Label(android_frame, text="Target SDK:").grid(row=1, column=0, sticky='w', pady=2)
        self.target_sdk_var = tk.IntVar(value=34)
        target_sdk_spin = ttk.Spinbox(android_frame, from_=24, to=34, textvariable=self.target_sdk_var, width=10)
        target_sdk_spin.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Compile SDK
        ttk.Label(android_frame, text="Compile SDK:").grid(row=2, column=0, sticky='w', pady=2)
        self.compile_sdk_var = tk.IntVar(value=34)
        compile_sdk_spin = ttk.Spinbox(android_frame, from_=24, to=34, textvariable=self.compile_sdk_var, width=10)
        compile_sdk_spin.grid(row=2, column=1, sticky='w', padx=5, pady=2)

        # Language preference
        ttk.Label(android_frame, text="Language:").grid(row=3, column=0, sticky='w', pady=2)
        self.language_var = tk.StringVar(value="Kotlin")
        language_combo = ttk.Combobox(android_frame, textvariable=self.language_var, values=["Kotlin", "Java"],
                                      state="readonly")
        language_combo.grid(row=3, column=1, sticky='w', padx=5, pady=2)

        # Configure grid weights
        project_config_frame.grid_columnconfigure(1, weight=1)
        android_frame.grid_columnconfigure(1, weight=1)

    def create_ui_settings_tab(self):
        """Create UI settings tab"""
        ui_frame = ttk.Frame(self.notebook)
        self.notebook.add(ui_frame, text="🎨 Interface")

        # Appearance settings
        appearance_frame = ttk.LabelFrame(ui_frame, text="Appearance", padding=10)
        appearance_frame.pack(fill='x', padx=10, pady=5)

        # Theme
        ttk.Label(appearance_frame, text="Theme:").grid(row=0, column=0, sticky='w', pady=2)
        self.theme_var = tk.StringVar(value="System")
        theme_combo = ttk.Combobox(appearance_frame, textvariable=self.theme_var,
                                   values=["System", "Light", "Dark"], state="readonly")
        theme_combo.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Font size
        ttk.Label(appearance_frame, text="Font Size:").grid(row=1, column=0, sticky='w', pady=2)
        self.font_size_var = tk.IntVar(value=10)
        font_size_spin = ttk.Spinbox(appearance_frame, from_=8, to=16, textvariable=self.font_size_var, width=10)
        font_size_spin.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Window settings
        window_frame = ttk.LabelFrame(ui_frame, text="Window", padding=10)
        window_frame.pack(fill='x', padx=10, pady=5)

        # Remember window size
        self.remember_size_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(window_frame, text="Remember window size and position",
                        variable=self.remember_size_var).grid(row=0, column=0, sticky='w', pady=2)

        # Auto-save chat
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(window_frame, text="Auto-save chat history",
                        variable=self.auto_save_var).grid(row=1, column=0, sticky='w', pady=2)

        # Configure grid weights
        appearance_frame.grid_columnconfigure(1, weight=1)

    def create_advanced_settings_tab(self):
        """Create advanced settings tab"""
        advanced_frame = ttk.Frame(self.notebook)
        self.notebook.add(advanced_frame, text="⚙️ Advanced")

        # Performance settings
        performance_frame = ttk.LabelFrame(advanced_frame, text="Performance", padding=10)
        performance_frame.pack(fill='x', padx=10, pady=5)

        # Memory limit
        ttk.Label(performance_frame, text="Memory Limit (MB):").grid(row=0, column=0, sticky='w', pady=2)
        self.memory_limit_var = tk.IntVar(value=2048)
        memory_spin = ttk.Spinbox(performance_frame, from_=512, to=8192, textvariable=self.memory_limit_var, width=10)
        memory_spin.grid(row=0, column=1, sticky='w', padx=5, pady=2)

        # Thread count
        ttk.Label(performance_frame, text="Thread Count:").grid(row=1, column=0, sticky='w', pady=2)
        self.thread_count_var = tk.IntVar(value=4)
        thread_spin = ttk.Spinbox(performance_frame, from_=1, to=16, textvariable=self.thread_count_var, width=10)
        thread_spin.grid(row=1, column=1, sticky='w', padx=5, pady=2)

        # Debug settings
        debug_frame = ttk.LabelFrame(advanced_frame, text="Debug", padding=10)
        debug_frame.pack(fill='x', padx=10, pady=5)

        # Enable logging
        self.enable_logging_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(debug_frame, text="Enable detailed logging",
                        variable=self.enable_logging_var).grid(row=0, column=0, sticky='w', pady=2)

        # Show debug info
        self.show_debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(debug_frame, text="Show debug information",
                        variable=self.show_debug_var).grid(row=1, column=0, sticky='w', pady=2)

        # Configure grid weights
        performance_frame.grid_columnconfigure(1, weight=1)

    def create_bottom_buttons(self):
        """Create bottom buttons"""
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)

        # Left side
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side='left')

        ttk.Button(left_frame, text="🔄 Reset to Defaults",
                   command=self.reset_to_defaults).pack(side='left', padx=2)
        ttk.Button(left_frame, text="📁 Open Settings Folder",
                   command=self.open_settings_folder).pack(side='left', padx=2)

        # Right side
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side='right')

        ttk.Button(right_frame, text="❌ Cancel",
                   command=self.cancel_settings).pack(side='right', padx=2)
        ttk.Button(right_frame, text="✅ Apply",
                   command=self.apply_settings, style='Primary.TButton').pack(side='right', padx=2)

    def load_default_settings(self) -> Dict[str, Any]:
        """Load default settings"""
        return {
            'model': {
                'path': '',
                'max_tokens': 2048,
                'temperature': 0.1,
                'top_p': 0.95,
                'repeat_penalty': 1.1
            },
            'project': {
                'output_directory': os.path.join(os.path.expanduser("~"), "AndroidProjects"),
                'min_sdk': 24,
                'target_sdk': 34,
                'compile_sdk': 34,
                'language': 'Kotlin'
            },
            'ui': {
                'theme': 'System',
                'font_size': 10,
                'remember_size': True,
                'auto_save': True
            },
            'advanced': {
                'memory_limit': 2048,
                'thread_count': 4,
                'enable_logging': False,
                'show_debug': False
            }
        }

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults
                    self.merge_settings(loaded_settings)

            self.update_ui_from_settings()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load settings: {str(e)}")

    def merge_settings(self, loaded_settings: Dict[str, Any]):
        """Merge loaded settings with defaults"""
        for category, settings in loaded_settings.items():
            if category in self.settings:
                self.settings[category].update(settings)

    def update_ui_from_settings(self):
        """Update UI controls from settings"""
        # Model settings
        self.model_path_var.set(self.settings['model']['path'])
        self.max_tokens_var.set(self.settings['model']['max_tokens'])
        self.temperature_var.set(self.settings['model']['temperature'])
        self.top_p_var.set(self.settings['model']['top_p'])
        self.repeat_penalty_var.set(self.settings['model']['repeat_penalty'])

        # Project settings
        self.output_dir_var.set(self.settings['project']['output_directory'])
        self.min_sdk_var.set(self.settings['project']['min_sdk'])
        self.target_sdk_var.set(self.settings['project']['target_sdk'])
        self.compile_sdk_var.set(self.settings['project']['compile_sdk'])
        self.language_var.set(self.settings['project']['language'])

        # UI settings
        self.theme_var.set(self.settings['ui']['theme'])
        self.font_size_var.set(self.settings['ui']['font_size'])
        self.remember_size_var.set(self.settings['ui']['remember_size'])
        self.auto_save_var.set(self.settings['ui']['auto_save'])

        # Advanced settings
        self.memory_limit_var.set(self.settings['advanced']['memory_limit'])
        self.thread_count_var.set(self.settings['advanced']['thread_count'])
        self.enable_logging_var.set(self.settings['advanced']['enable_logging'])
        self.show_debug_var.set(self.settings['advanced']['show_debug'])

        # Update model status
        self.update_model_status()

    def update_model_status(self):
        """Update model status display"""
        if self.llm_manager.is_ready():
            self.model_status_label.config(text="✅ Loaded", foreground="green")
        else:
            self.model_status_label.config(text="❌ Not Loaded", foreground="red")

    def browse_model_path(self):
        """Browse for model file"""
        filename = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("GGUF files", "*.gguf"), ("All files", "*.*")]
        )
        if filename:
            self.model_path_var.set(filename)

    def browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Default Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def reset_to_defaults(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Reset Settings",
                               "Are you sure you want to reset all settings to defaults?"):
            self.settings = self.load_default_settings()
            self.update_ui_from_settings()

    def open_settings_folder(self):
        """Open settings folder in file explorer"""
        settings_dir = os.path.dirname(self.settings_file)
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        try:
            if os.name == 'nt':  # Windows
                os.startfile(settings_dir)
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                subprocess.run(['xdg-open', settings_dir] if os.name == 'posix' else ['open', settings_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings folder: {str(e)}")

    def cancel_settings(self):
        """Cancel settings changes"""
        self.load_settings()  # Reload from file

    def apply_settings(self):
        """Apply settings changes"""
        try:
            # Update settings from UI
            self.settings['model']['path'] = self.model_path_var.get()
            self.settings['model']['max_tokens'] = self.max_tokens_var.get()
            self.settings['model']['temperature'] = self.temperature_var.get()
            self.settings['model']['top_p'] = self.top_p_var.get()
            self.settings['model']['repeat_penalty'] = self.repeat_penalty_var.get()

            self.settings['project']['output_directory'] = self.output_dir_var.get()
            self.settings['project']['min_sdk'] = self.min_sdk_var.get()
            self.settings['project']['target_sdk'] = self.target_sdk_var.get()
            self.settings['project']['compile_sdk'] = self.compile_sdk_var.get()
            self.settings['project']['language'] = self.language_var.get()

            self.settings['ui']['theme'] = self.theme_var.get()
            self.settings['ui']['font_size'] = self.font_size_var.get()
            self.settings['ui']['remember_size'] = self.remember_size_var.get()
            self.settings['ui']['auto_save'] = self.auto_save_var.get()

            self.settings['advanced']['memory_limit'] = self.memory_limit_var.get()
            self.settings['advanced']['thread_count'] = self.thread_count_var.get()
            self.settings['advanced']['enable_logging'] = self.enable_logging_var.get()
            self.settings['advanced']['show_debug'] = self.show_debug_var.get()

            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)

            # Apply to LLM manager
            self.llm_manager.set_generation_params(
                max_tokens=self.settings['model']['max_tokens'],
                temp=self.settings['model']['temperature'],
                top_p=self.settings['model']['top_p'],
                repeat_penalty=self.settings['model']['repeat_penalty']
            )
            # Update model path if provided
            model_path = self.settings['model']['path']
            if model_path:
                if not os.path.exists(model_path):
                    raise FileNotFoundError(f"Model file not found: {model_path}")
                if not self.llm_manager.set_model_path(model_path):
                    raise RuntimeError("Failed to set model path")
                # Try loading model now
                self.llm_manager.initialize()
                if not self.llm_manager.load_model():
                    raise RuntimeError("Failed to load model after applying settings")

            # Refresh status
            self.update_model_status()

            messagebox.showinfo("Success", "Settings applied successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    def get_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        return self.settings.copy()