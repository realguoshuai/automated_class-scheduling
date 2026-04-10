import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from main import MainWindow
from dialogs import DataManagementDialog

def take_shots():
    try:
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        # Capture main window class view
        window.grab().save("screenshots/main_class_view.png")
        
        # Switch to Teacher view
        window.view_type_selector.setCurrentIndex(1)
        QApplication.processEvents()
        window.grab().save("screenshots/main_teacher_view.png")
        
        # Capture Data Management Dialog
        dialog = DataManagementDialog(window.dm, window)
        dialog.resize(1100, 700)
        dialog.show()
        QApplication.processEvents()
        # Sleep tight to allow rendering
        dialog.grab().save("screenshots/data_management.png")
        dialog.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        window.close()
        app.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    # Wait 1000ms for UI to render then take screenshots
    QTimer.singleShot(1000, take_shots)
    sys.exit(app.exec_())
