import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PySide6.QtWidgets import QApplication, QDialog
from frontend.api_client import APIClient
from frontend.main_gui import LoginDialog
from frontend.mainwindow import MainWindow

def main():
    app = QApplication(sys.argv)

    client = APIClient(base_url="http://127.0.0.1:8080")

    login_dialog = LoginDialog(client)

    if login_dialog.exec() == QDialog.Accepted:
        window = MainWindow(api_client=client)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
