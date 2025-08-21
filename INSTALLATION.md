# Android App Generator - Installation Guide

## Quick Start

### Prerequisites
- Python 3.8 or higher
- 4GB+ RAM (8GB recommended)
- 2GB+ free disk space for models

### Installation Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd android-app-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   
   **Windows:**
   ```bash
   run.bat
   ```
   
   **Linux/macOS:**
   ```bash
   ./run.sh
   ```
   
   **Manual:**
   ```bash
   python main.py
   ```

4. **Test installation (optional)**
   ```bash
   python test_installation.py
   ```

## Detailed Installation

### Step 1: Install Python

Download and install Python 3.8 or higher from [python.org](https://python.org)

**Windows:**
- Download the installer from python.org
- Run the installer and check "Add Python to PATH"
- Verify installation: `python --version`

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**macOS:**
```bash
brew install python3
```

### Step 2: Install Dependencies

The application requires several Python packages:

```bash
pip install gpt4all==2.0.2
pip install tkinter-tooltip==2.0.0
pip install Pillow==10.0.1
pip install requests==2.31.0
pip install tqdm==4.66.1
pip install colorama==0.4.6
pip install psutil==5.9.6
```

Or install all at once:
```bash
pip install -r requirements.txt
```

### Step 3: Download AI Model

The application will automatically download the required AI model on first run. 
The model file is approximately 1.3GB and will be stored in the `models/` directory.

**Manual download (if automatic fails):**
```bash
wget https://huggingface.co/TheBloke/deepseek-coder-1.3b-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q4_K_M.gguf
mkdir -p models
mv deepseek-coder-1.3b-instruct.Q4_K_M.gguf models/
```

### Step 4: Run the Application

**Option 1: Use provided scripts**
- Windows: Double-click `run.bat`
- Linux/macOS: Run `./run.sh`

**Option 2: Manual execution**
```bash
python main.py
```

**Option 3: Use launcher script**
```bash
python run.py
```

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install -r requirements.txt
```

**2. "Python not found"**
- Make sure Python is installed and in your PATH
- Try using `python3` instead of `python`

**3. "Permission denied" (Linux/macOS)**
```bash
chmod +x run.sh
```

**4. Model download fails**
- Check your internet connection
- Try manual download (see Step 3 above)
- Check available disk space

**5. GUI doesn't start**
- Make sure tkinter is installed
- On Linux: `sudo apt install python3-tk`
- On macOS: `brew install python-tk`

### System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Windows 10 / macOS 10.14 / Ubuntu 18.04

**Recommended:**
- Python 3.9+
- 8GB RAM
- 5GB free disk space
- SSD storage
- Modern operating system

### Performance Optimization

**For better performance:**
1. Use SSD storage for faster model loading
2. Close other applications while using
3. Increase virtual memory (Windows)
4. Use a machine with more RAM

**For slower machines:**
1. Reduce context size in settings
2. Use smaller model variants
3. Disable unnecessary features
4. Close other applications

## Verification

Run the test script to verify your installation:

```bash
python test_installation.py
```

This will check:
- ✅ All required modules
- ✅ Project structure
- ✅ Basic functionality
- ✅ Directory permissions

## Next Steps

After successful installation:

1. **First Run**: The application will download the AI model (may take several minutes)
2. **Configure Settings**: Go to Settings tab to customize the application
3. **Create Your First App**: Use the Chat tab to describe your Android app idea
4. **Generate Projects**: Click "Generate Project" to create complete Android Studio projects

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run the test script: `python test_installation.py`
3. Check the logs in the `logs/` directory
4. Create an issue on the project repository

## Uninstallation

To remove the application:

1. Delete the project directory
2. Remove downloaded models (optional):
   ```bash
   rm -rf models/
   ```
3. Uninstall Python packages (optional):
   ```bash
   pip uninstall gpt4all tkinter-tooltip Pillow requests tqdm colorama psutil
   ```

---

**Happy Android Development! 🚀**