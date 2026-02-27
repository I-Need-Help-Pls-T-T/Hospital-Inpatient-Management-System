import sys
import subprocess
import time
import threading
from frontend.mainwindow import MainWindow
from PySide6.QtWidgets import QApplication

def run_server():
    try:
        subprocess.run(["python", "backend/main.py"])
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}")

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    time.sleep(2)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
