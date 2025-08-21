# Android App Generator - Desktop Application

A powerful desktop application that uses local AI models to generate complete Android applications from natural language descriptions.

## 🚀 Features

### Core Capabilities
- **Local AI Processing**: Uses DeepSeek-Coder model for offline code generation
- **Multi-Agent System**: Intelligent agents for planning, coding, reviewing, and debugging
- **Complete Android Projects**: Generates full Android Studio projects with all necessary files
- **Modern GUI**: Beautiful, intuitive desktop interface
- **Real-time Code Generation**: Stream responses with live code preview
- **Project Templates**: Pre-built templates for common app types

### Advanced Features
- **Smart Architecture Design**: Automatic project structure and architecture planning
- **Code Review & Optimization**: Built-in code quality checks and improvements
- **Dependency Management**: Automatic handling of Android dependencies
- **Error Detection & Fixing**: Intelligent debugging and error resolution
- **Project Export**: Export complete projects ready for Android Studio

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (8GB recommended)
- 2GB+ free disk space for models

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd android-app-generator

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The application will automatically download the required AI model on first run.

For build/packaging details, see `BUILDING.md`.

## 📱 Usage

### 1. Launch the Application
Run `python main.py` to start the desktop application.

### 2. Describe Your App
In the chat interface, describe the Android app you want to create. For example:
- "Create a todo list app with add, edit, and delete functionality"
- "Build a weather app that shows current weather and 5-day forecast"
- "Make a simple calculator app with basic arithmetic operations"

### 3. Generate Your App
The AI will:
1. **Plan** the app architecture and features
2. **Design** the user interface and data models
3. **Code** all necessary components (Activities, Fragments, Adapters, etc.)
4. **Review** and optimize the generated code
5. **Export** a complete Android Studio project

### 4. Build and Run
- Open the generated project in Android Studio
- Sync Gradle dependencies
- Build and run on your device or emulator

## 🏗️ Project Structure

```
android-app-generator/
├── main.py                 # Main application entry point
├── app2_agents.py          # Enhanced multi-agent system
├── gui/                    # GUI components
│   ├── main_window.py      # Main application window
│   ├── chat_panel.py       # Chat interface
│   ├── project_panel.py    # Project management
│   └── settings_panel.py   # Application settings
├── core/                   # Core functionality
│   ├── llm_manager.py      # AI model management
│   ├── project_generator.py # Project generation logic
│   ├── android_templates.py # Android project templates
│   └── code_analyzer.py    # Code analysis and optimization
├── templates/              # Project templates
│   ├── basic_app/          # Basic Android app template
│   ├── todo_app/           # Todo list app template
│   └── weather_app/        # Weather app template
├── models/                 # AI models (auto-downloaded)
└── output/                 # Generated projects
```

## 🎯 Supported App Types

### Basic Apps
- **Calculator**: Mathematical operations with modern UI
- **Todo List**: Task management with CRUD operations
- **Notes App**: Text notes with search and categories
- **Timer/Stopwatch**: Time tracking applications

### Data-Driven Apps
- **Weather App**: Current weather and forecasts
- **News Reader**: RSS feed reader with categories
- **Recipe App**: Recipe management with ingredients
- **Expense Tracker**: Financial tracking and reporting

### Social/Communication
- **Chat App**: Simple messaging interface
- **Contact Manager**: Contact list with details
- **Social Feed**: Timeline-based content display
- **Photo Gallery**: Image viewing and management

## 🔧 Configuration

### Model Settings
- **Model Path**: Customize AI model location
- **Context Size**: Adjust memory and response length
- **Generation Parameters**: Temperature, top-p, etc.

### Project Settings
- **Output Directory**: Choose where projects are saved
- **Template Selection**: Default project templates
- **Code Style**: Kotlin/Java preferences
- **Minimum SDK**: Target Android API level

### Performance Settings
- **Memory Management**: Optimize for your system
- **Threading**: Multi-threading for faster generation
- **Caching**: Enable/disable response caching

## 🚀 Advanced Features

### Custom Templates
Create your own project templates:
1. Design your template structure
2. Add template files to `templates/` directory
3. Register template in `android_templates.py`
4. Use via template selector in GUI

### Plugin System
Extend functionality with plugins:
- Custom code generators
- Additional UI components
- Integration with external tools
- Custom project validators

### Batch Processing
Generate multiple apps at once:
- Load app descriptions from file
- Queue multiple generation tasks
- Monitor progress across all projects
- Export all projects simultaneously

## 🐛 Troubleshooting

### Common Issues

**Model Download Fails**
```bash
# Manual download
wget https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q4_K_M.gguf
# Place in models/ directory
```

**Memory Issues**
- Reduce context size in settings
- Close other applications
- Use smaller model variant

**Generation Quality**
- Provide more detailed descriptions
- Use specific feature requests
- Enable code review in settings

### Performance Optimization
- Use SSD for faster model loading
- Increase RAM allocation
- Enable GPU acceleration (if available)
- Optimize context window size

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Format code
black .
isort .

# Type checking
mypy .
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **DeepSeek-Coder**: The AI model powering code generation
- **GPT4All**: Local AI model inference framework
- **Android Community**: For development best practices
- **Open Source Contributors**: For various libraries and tools

## 📞 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Join community discussions
- **Documentation**: Check the wiki for detailed guides
- **Email**: Contact us at support@androidappgenerator.com

---

**Made with ❤️ for the Android development community**