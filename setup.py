#!/usr/bin/env python3
"""
Setup script for AI Psychologist application
"""
import os
import subprocess
import sys

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python version {sys.version_info.major}.{sys.version_info.minor} OK")

def create_directories():
    """Create necessary directories"""
    directories = [
        "app/api/endpoints",
        "app/core",
        "app/db",
        "app/models",
        "app/schemas",
        "app/services",
        "app/therapists",
        "app/utils",
        "tests",
        "chroma_db"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ Project directories created")

def create_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")

def install_dependencies():
    """Install required packages"""
    print("Installing dependencies...")
    # Determine the pip path based on operating system
    pip_path = os.path.join("venv", "Scripts", "pip") if sys.platform == "win32" else os.path.join("venv", "bin", "pip")
    
    # Install main requirements
    subprocess.run([pip_path, "install", "-U", "pip"], check=True)
    
    requirements = [
        "fastapi", "uvicorn", "pydantic", "python-multipart",
        "sqlalchemy", "chromadb", "sentence-transformers",
        "openai-whisper", "langchain",
        "pytest", "pytest-asyncio"
    ]
    
    subprocess.run([pip_path, "install"] + requirements, check=True)
    
    # Save requirements to file
    with open("requirements.txt", "w") as f:
        subprocess.run([pip_path, "freeze"], stdout=f, check=True)
    
    print("✓ Dependencies installed and requirements.txt created")

def initialize_database():
    """Initialize SQLite and Vector databases"""
    print("Initializing databases...")
    
    # Make the database init module executable
    init_script = """
import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run the database initialization
from app.db.init_db import init_db

if __name__ == "__main__":
    init_db()
"""
    
    with open("init_db.py", "w") as f:
        f.write(init_script)
    
    # Determine the python path based on operating system
    python_path = os.path.join("venv", "Scripts", "python") if sys.platform == "win32" else os.path.join("venv", "bin", "python")
    
    # Run the initialization script
    subprocess.run([python_path, "init_db.py"], check=True)
    
    print("✓ Databases initialized")

def setup_ollama():
    """Instructions for setting up Ollama"""
    print("\nSetup Instructions for Ollama:")
    print("1. Download and install Ollama from https://ollama.ai/")
    print("2. Once installed, run the following command to pull the Phi-4 model:")
    print("   ollama pull phi4:latest")
    print("\nIf you want to use a different model, update the MODEL_NAME in app/core/config.py")

def main():
    """Main setup function"""
    print("Setting up AI Psychologist application...")
    
    check_python_version()
    create_directories()
    create_virtual_environment()
    install_dependencies()
    initialize_database()
    setup_ollama()
    
    print("\n✓ Setup completed successfully!")
    print("\nTo start the application, run:")
    if sys.platform == "win32":
        print("venv\\Scripts\\python -m app.main")
    else:
        print("venv/bin/python -m app.main")

if __name__ == "__main__":
    main()