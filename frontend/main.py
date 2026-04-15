import sys
from PyQt6.QtWidgets import QApplication, QDialog
from frontend.views.mainwindow import MainWindow
from frontend.views.dialogs import LoginDialog
from frontend.core.theme_manager import apply_theme

def main():
    app = QApplication(sys.argv)
    apply_theme(app)
    
    login_dialog = LoginDialog()
    
    if login_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit()

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()