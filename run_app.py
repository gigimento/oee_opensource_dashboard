#!/usr/bin/env python3
"""
SMT Line 003 Production Intelligence Dashboard
Streamlit App Launcher
"""

import subprocess
import os
import sys
import webbrowser
import time

def main():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print()
    print("=" * 60)
    print("   STATIC//VOID - SMT Line 003 Production Intelligence")
    print("=" * 60)
    print()
    print("Starting Streamlit app...")
    print("Dashboard will open at: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the server.")
    print()
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
    
    # Run Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
    except FileNotFoundError:
        print("\nError: Streamlit is not installed.")
        print("Install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
