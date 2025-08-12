#!/usr/bin/env python3
"""
Startup script for the Specialist Feedback Management Dashboard
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start the Streamlit dashboard"""
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Dashboard file path
    dashboard_path = project_dir / "web" / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"Error: Dashboard file not found at {dashboard_path}")
        sys.exit(1)
    
    print("Starting Specialist Feedback Management Dashboard...")
    print(f"Project directory: {project_dir}")
    print(f"Dashboard will be available at: http://localhost:8501")
    print("Use Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
