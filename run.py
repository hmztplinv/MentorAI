#!/usr/bin/env python3
"""
Run script for AI Psychologist application
"""
import os
import subprocess
import sys
import webbrowser
import time
import threading

def get_python_executable():
    """Get the appropriate python executable based on OS"""
    if sys.platform == "win32":
        return os.path.join("venv", "Scripts", "python")
    else:
        return os.path.join("venv", "bin", "python")

def check_ollama():
    """Check if Ollama is running and has the required model"""
    print("Checking Ollama service...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags")
        
        if response.status_code != 200:
            print("⚠️ Ollama is not running. Please start Ollama first.")
            return False
        
        models = response.json().get("models", [])
        model_names = [model.get("name") for model in models]
        
        if "phi4:latest" not in model_names:
            print("⚠️ Phi model not found in Ollama. Please run 'ollama pull phi' first.")
            return False
        
        print("✓ Ollama is running with Phi model")
        return True
        
    except Exception as e:
        print(f"⚠️ Error checking Ollama: {str(e)}")
        print("Please make sure Ollama is installed and running.")
        return False

def open_browser():
    """Open browser with API docs after a delay"""
    time.sleep(2)  # Wait for server to start
    webbrowser.open("http://localhost:8000/docs")

def run_server():
    """Run the FastAPI server"""
    python_executable = get_python_executable()
    
    # Run the server
    try:
        # Start browser in a separate thread
        threading.Thread(target=open_browser).start()
        
        # Start the server
        subprocess.run([python_executable, "-m", "app.main"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Error starting server: {str(e)}")

def main():
    """Main run function"""
    print("Starting AI Psychologist application...")
    
    # Check if virtual environment exists
    if not os.path.exists("venv"):
        print("Virtual environment not found. Please run setup.py first.")
        sys.exit(1)
    
    # Check if Ollama is running with Phi model
    if not check_ollama():
        user_input = input("Do you want to continue anyway? (y/n): ").lower()
        if user_input != 'y':
            sys.exit(1)
    
    run_server()

if __name__ == "__main__":
    main()