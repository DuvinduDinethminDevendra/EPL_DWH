"""
PyQt6 Installation Helper
Run this script to install all required packages for the desktop application
"""

import subprocess
import sys

def run_command(command, description):
    """Run a command and report status"""
    print(f"\n{description}...", end=" ", flush=True)
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print("✅")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌\n{e.stderr}")
        return False

def main():
    print("=" * 60)
    print("EPL DWH - PyQt6 Setup Installer")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 9):
        print(f"\n❌ Python 3.9+ required, you have {sys.version}")
        sys.exit(1)
    
    print(f"\n✅ Python {sys.version.split()[0]} detected")
    
    # Install main packages
    packages = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install PyQt6>=6.6.0", "Installing PyQt6"),
        ("pip install PyQt6-Charts>=6.6.0", "Installing PyQt6-Charts"),
        ("pip install -r requirements.txt", "Installing project dependencies"),
    ]
    
    failed = []
    for command, description in packages:
        if not run_command(command, description):
            failed.append(description)
    
    # Summary
    print("\n" + "=" * 60)
    if failed:
        print("❌ Installation incomplete. Failed steps:")
        for item in failed:
            print(f"  - {item}")
        print("\nPlease fix errors and run again.")
        sys.exit(1)
    else:
        print("✅ All packages installed successfully!")
        print("\nTo start the desktop app:")
        print("  1. Ensure MySQL is running: docker-compose up -d")
        print("  2. Run: python desktop_app.py")
        print("  3. Or run: .\\run_desktop_app.bat (Windows)")
        print("=" * 60)

if __name__ == "__main__":
    main()
