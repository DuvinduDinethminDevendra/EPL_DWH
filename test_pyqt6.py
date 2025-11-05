#!/usr/bin/env python3
"""Test PyQt6 installation"""

import sys
print(f"Python: {sys.version}")

try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt6.QtCore import Qt
    print("✅ PyQt6 imports successful")
    
    app = QApplication(sys.argv)
    print("✅ QApplication created")
    
    window = QMainWindow()
    window.setWindowTitle("Test Window")
    window.setGeometry(100, 100, 400, 300)
    
    label = QLabel("PyQt6 Working! ✅")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setCentralWidget(label)
    
    print("✅ Window created")
    window.show()
    print("✅ Window shown - Application starting...")
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
