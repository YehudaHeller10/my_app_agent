import tkinter as tk
from tkinter import ttk, messagebox
import os
import threading
from typing import Optional, Callable
from .chat_panel import ChatPanel
from .project_panel import ProjectPanel
from .settings_panel import SettingsPanel
from core.llm_manager import LLMManager
from core.project_generator import ProjectGenerator


class MainWindow:
    """
    Main application window with modern design and enhanced functionality
    """

    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()

        # Core components - create these BEFORE creating widgets
        self.llm_manager = LLMManager()
        self.project_generator = ProjectGenerator(self.llm_manager)

        # Now create widgets that depend on the core components
        self.create_widgets()
        self.setup_menu()
        self.setup_status_bar()

        # Initialize components
        self.initialize_components()

    def setup_window(self):
        """Configure main window properties"""
        self.root.title("Android App Generator - AI-Powered Development")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # Set window icon if available
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()

        # Configure theme
        try:
            style.theme_use('clam')
        except:
            pass

        # Custom styles
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12))
        style.configure('Status.TLabel', font=('Segoe UI', 9))

        # Button styles
        style.configure('Primary.TButton',
                        background='#0078d4',
                        foreground='white',
                        font=('Segoe UI', 10, 'bold'))
        style.configure('Success.TButton',
                        background='#107c10',
                        foreground='white')
        style.configure('Warning.TButton',
                        background='#d83b01',
                        foreground='white')

        # Notebook style
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10))

    def create_widgets(self):
        """Create and arrange main widgets"""
        # Left sidebar
        self.create_sidebar()

        # Main content area
        self.create_main_content()

    def create_sidebar(self):
        """Create left sidebar with navigation"""
        sidebar = ttk.Frame(self.root, relief='raised', borderwidth=1)
        sidebar.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)
        sidebar.grid_rowconfigure(4, weight=1)  # Push status to bottom

        # Logo/Title
        title_frame = ttk.Frame(sidebar)
        title_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(title_frame, text="🤖", font=('Segoe UI', 24)).pack()
        ttk.Label(title_frame, text="App Generator",
                  style='Title.TLabel').pack()
        ttk.Label(title_frame, text="AI-Powered Android Development",
                  style='Subtitle.TLabel', foreground='#666').pack()

        # Navigation buttons
        nav_frame = ttk.Frame(sidebar)
        nav_frame.pack(fill='x', padx=10, pady=10)

        self.chat_btn = ttk.Button(nav_frame, text="💬 Chat & Generate",
                                   command=self.show_chat_panel, style='Primary.TButton')
        self.chat_btn.pack(fill='x', pady=2)

        self.projects_btn = ttk.Button(nav_frame, text="📁 Projects",
                                       command=self.show_projects_panel)
        self.projects_btn.pack(fill='x', pady=2)

        self.settings_btn = ttk.Button(nav_frame, text="⚙️ Settings",
                                       command=self.show_settings_panel)
        self.settings_btn.pack(fill='x', pady=2)

        # Quick actions
        quick_frame = ttk.LabelFrame(sidebar, text="Quick Actions", padding=10)
        quick_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(quick_frame, text="📱 New Todo App",
                   command=lambda: self.quick_generate("todo")).pack(fill='x', pady=1)
        ttk.Button(quick_frame, text="🌤️ New Weather App",
                   command=lambda: self.quick_generate("weather")).pack(fill='x', pady=1)
        ttk.Button(quick_frame, text="🧮 New Calculator",
                   command=lambda: self.quick_generate("calculator")).pack(fill='x', pady=1)

        # Status section
        status_frame = ttk.LabelFrame(sidebar, text="Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=(10, 0))

        self.model_status = ttk.Label(status_frame, text="🔴 Model: Not Loaded",
                                      style='Status.TLabel')
        self.model_status.pack(anchor='w')

        self.generation_status = ttk.Label(status_frame, text="⚪ Generation: Idle",
                                           style='Status.TLabel')
        self.generation_status.pack(anchor='w')

    def create_main_content(self):
        """Create main content area with notebook"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)

        # Create panels
        self.chat_panel = ChatPanel(self.notebook, self.llm_manager, self.project_generator)
        self.projects_panel = ProjectPanel(self.notebook)
        self.settings_panel = SettingsPanel(self.notebook, self.llm_manager)

        # Add panels to notebook
        self.notebook.add(self.chat_panel, text="💬 Chat & Generate")
        self.notebook.add(self.projects_panel, text="📁 Projects")
        self.notebook.add(self.settings_panel, text="⚙️ Settings")

        # Bind notebook events
        self.notebook.bind('<<NotebookTabChanged>>', self.on_tab_changed)

    def setup_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Project", command=self.new_project)
        file_menu.add_command(label="Open Project", command=self.open_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Model Manager", command=self.open_model_manager)
        tools_menu.add_command(label="Template Editor", command=self.open_template_editor)
        tools_menu.add_separator()
        tools_menu.add_command(label="Batch Generator", command=self.open_batch_generator)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_status_bar(self):
        """Create status bar at bottom"""
        status_bar = ttk.Frame(self.root, relief='sunken', borderwidth=1)
        status_bar.grid(row=1, column=0, columnspan=2, sticky='ew', padx=2, pady=2)

        self.status_label = ttk.Label(status_bar, text="Ready", style='Status.TLabel')
        self.status_label.pack(side='left', padx=5)

        # Create progress bar but don't start it automatically
        self.progress_bar = ttk.Progressbar(status_bar, mode='indeterminate')
        self.progress_bar.pack(side='right', padx=5, pady=2)
        # Don't start the progress bar automatically to avoid tkinter errors

    def initialize_components(self):
        """Initialize core components"""

        def init_worker():
            try:
                self.update_status("Initializing AI model...")
                success = self.llm_manager.initialize()
                if success:
                    self.update_model_status("🟢 Model: Loaded")
                    self.update_status("Ready")
                else:
                    self.update_model_status("🟡 Model: Not Loaded")
                    self.update_status("Ready - Model not loaded. Use Settings to download.")
            except Exception as e:
                self.update_model_status("🔴 Model: Error")
                self.update_status(f"Error: {str(e)}")
                print(f"Initialization error: {e}")
                # Don't show error dialog during startup to avoid blocking the UI

        # Start initialization in background
        init_thread = threading.Thread(target=init_worker, daemon=True)
        init_thread.start()

    def show_chat_panel(self):
        """Switch to chat panel"""
        self.notebook.select(0)

    def show_projects_panel(self):
        """Switch to projects panel"""
        self.notebook.select(1)

    def show_settings_panel(self):
        """Switch to settings panel"""
        self.notebook.select(2)

    def on_tab_changed(self, event):
        """Handle tab change events"""
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)

        if tab_id == 0:  # Chat panel
            self.update_status("Chat & Generate - Describe your app idea")
        elif tab_id == 1:  # Projects panel
            self.update_status("Projects - Manage generated applications")
        elif tab_id == 2:  # Settings panel
            self.update_status("Settings - Configure application preferences")

    def quick_generate(self, app_type: str):
        """Quick generate common app types"""
        templates = {
            "todo": "Create a todo list app with add, edit, delete, and mark as complete functionality. Include a modern Material Design UI with RecyclerView and Room database.",
            "weather": "Build a weather app that shows current weather conditions, 5-day forecast, and location-based weather. Use OpenWeatherMap API and include beautiful weather icons.",
            "calculator": "Create a modern calculator app with basic arithmetic operations, scientific functions, and a clean Material Design interface."
        }

        if app_type in templates:
            self.show_chat_panel()
            self.chat_panel.set_prompt(templates[app_type])
            self.update_status(f"Quick generating {app_type} app...")

    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def update_model_status(self, status: str):
        """Update model status in sidebar"""
        self.model_status.config(text=status)

    def update_generation_status(self, status: str):
        """Update generation status in sidebar"""
        self.generation_status.config(text=status)

    def show_progress(self, show: bool = True):
        """Show/hide progress bar"""
        try:
            if show:
                self.progress_bar.start()
            else:
                self.progress_bar.stop()
        except Exception as e:
            print(f"Progress bar error: {e}")
            # Ignore progress bar errors

    # Menu command handlers
    def new_project(self):
        """Create new project"""
        self.show_chat_panel()
        self.chat_panel.clear_chat()

    def open_project(self):
        """Open existing project"""
        # TODO: Implement project opening
        messagebox.showinfo("Info", "Project opening feature coming soon!")

    def open_model_manager(self):
        """Open model management dialog"""
        # TODO: Implement model manager
        messagebox.showinfo("Info", "Model manager coming soon!")

    def open_template_editor(self):
        """Open template editor"""
        # TODO: Implement template editor
        messagebox.showinfo("Info", "Template editor coming soon!")

    def open_batch_generator(self):
        """Open batch generation dialog"""
        # TODO: Implement batch generator
        messagebox.showinfo("Info", "Batch generator coming soon!")

    def show_documentation(self):
        """Show documentation"""
        # TODO: Open documentation
        messagebox.showinfo("Documentation", "Documentation available at: https://github.com/your-repo/docs")

    def show_about(self):
        """Show about dialog"""
        about_text = """Android App Generator v1.0

A powerful desktop application that uses local AI models 
to generate complete Android applications from natural 
language descriptions.

Features:
• Local AI processing with DeepSeek-Coder
• Multi-agent system for intelligent code generation
• Complete Android Studio project generation
• Modern, intuitive desktop interface

Made with ❤️ for the Android development community"""

        messagebox.showinfo("About", about_text)

    def run(self):
        """Start the application"""
        self.root.mainloop()