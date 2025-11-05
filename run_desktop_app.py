#!/usr/bin/env python
"""
Quick launcher script for EPL DWH PyQt6 Desktop Application
Run this script to start the application
"""

import subprocess
import sys
import os

def main():
    """Launch the desktop application"""
    
    print("=" * 60)
    print("EPL Data Warehouse - Desktop Application Launcher")
    print("=" * 60)
    
    # Check if running from correct directory
    if not os.path.exists('src/db.py'):
        print("\n❌ Error: Must run from project root directory")
        print("   Current: {}".format(os.getcwd()))
        print("   Expected: D:\\myPortfolioProject\\EPL_DWH")
        sys.exit(1)
    
    # Check if desktop_app.py exists
    if not os.path.exists('desktop_app.py'):
        print("\n❌ Error: desktop_app.py not found")
        print("   Please ensure you're in the EPL_DWH root directory")
        sys.exit(1)
    
    print("\n✅ Project structure verified")
    print("✅ Starting EPL DWH Desktop Application...\n")
    
    try:
        # Run the desktop app
        subprocess.run([sys.executable, 'desktop_app.py'], check=True)
    except KeyboardInterrupt:
        print("\n\n👋 Application closed by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
