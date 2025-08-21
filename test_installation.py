#!/usr/bin/env python3
"""
Android App Generator - Installation Test

This script tests that all components are properly installed and working.
Run this script to verify your installation.
"""

import sys
import os
import importlib

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    modules_to_test = [
        'tkinter',
        'gpt4all',
        'json',
        'threading',
        'urllib.request',
        'os',
        'sys'
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All basic imports successful")
        return True

def test_project_modules():
    """Test that our project modules can be imported"""
    print("\nTesting project modules...")
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    project_modules = [
        'core.llm_manager',
        'core.project_generator', 
        'core.android_templates',
        'gui.main_window',
        'gui.chat_panel',
        'gui.project_panel',
        'gui.settings_panel'
    ]
    
    failed_imports = []
    
    for module in project_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import project modules: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All project modules imported successfully")
        return True

def test_directories():
    """Test that required directories exist or can be created"""
    print("\nTesting directory structure...")
    
    required_dirs = [
        'models',
        'config',
        'output', 
        'templates',
        'logs',
        'core',
        'gui'
    ]
    
    failed_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ {directory}/ (exists)")
        else:
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"✅ {directory}/ (created)")
            except Exception as e:
                print(f"❌ {directory}/: {e}")
                failed_dirs.append(directory)
    
    if failed_dirs:
        print(f"\n❌ Failed to create directories: {', '.join(failed_dirs)}")
        return False
    else:
        print("\n✅ All directories ready")
        return True

def test_basic_functionality():
    """Test basic functionality without starting the GUI"""
    print("\nTesting basic functionality...")
    
    try:
        # Test LLM Manager initialization
        from core.llm_manager import LLMManager
        llm_manager = LLMManager()
        print("✅ LLM Manager created")
        
        # Test Project Generator
        from core.project_generator import ProjectGenerator
        project_generator = ProjectGenerator(llm_manager)
        print("✅ Project Generator created")
        
        # Test Android Templates
        from core.android_templates import AndroidTemplates
        templates = AndroidTemplates()
        available_templates = templates.get_available_templates()
        print(f"✅ Android Templates loaded ({len(available_templates)} templates)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Android App Generator - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Project Modules", test_project_modules),
        ("Directory Structure", test_directories),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation is ready.")
        print("\nTo start the application, run:")
        print("  python main.py")
        print("  or")
        print("  python run.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Make sure you're running Python 3.8 or higher")
        print("3. Check that all files are in the correct locations")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)