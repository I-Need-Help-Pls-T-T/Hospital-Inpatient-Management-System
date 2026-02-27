import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidget, QTableWidgetItem
from PySide6.QtCore import QTimer
from ui_form import Ui_MainWindow
from api_client import APIClient
import threading
import subprocess
import time

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("HIMS - Cистема управления стационарным лечением в больнице")
        self.showMaximized()

        self.api = APIClient()
        self.check_server_connection()
        self.setup_connections()

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(30000)

    def check_server_connection(self):
        if self.api.check_connection():
            self.statusBar().showMessage("Подключено к серверу", 5000)
        else:
            self.statusBar().showMessage("Нет соединения с сервером", 5000)
            reply = QMessageBox.question(self, "Сервер не запущен", "Сервер не отвечает. Запустить сервер?",
                                                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.start_server()

    def start_server(self):
        try:
            python_path = sys.executable
            self.server_process = subprocess.Popen(
                [
                    python_path, "-m", "uvicorn",
                    "backend.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            time.sleep(3)
            self.check_server_connection()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить сервер: {e}")

    def update_status(self):
        if hasattr(self, 'api'):
            if self.api.check_connection():
                self.statusBar().showMessage("Статус: онлайн", 2000)
            else:
                self.statusBar().showMessage("Статус: офлайн", 2000)

    def setup_connections(self):

        # --- Меню "Файл" ---
        self.ui.action_exit.triggered.connect(self.close)

        # --- Меню "Справочники" ---
        self.ui.action_position.triggered.connect(self.open_position)
        self.ui.action_department.triggered.connect(self.open_departments)
        self.ui.action_room.triggered.connect(self.open_rooms)
        self.ui.action_ward.triggered.connect(self.open_wards)
        self.ui.action_staff_role.triggered.connect(self.open_staff_roles)

        # --- Меню "Ввод" ---
        self.ui.action_patient.triggered.connect(self.open_patients)
        self.ui.action_staff.triggered.connect(self.open_staff)
        self.ui.action_hospitalization.triggered.connect(self.open_hospitalization)
        self.ui.action_med_entry.triggered.connect(self.open_med_entry)
        self.ui.action_medication_order.triggered.connect(self.open_medication_order)
        self.ui.action_payment.triggered.connect(self.open_payment)
        self.ui.action_patient_admission.triggered.connect(self.open_patient_admission)
        self.ui.action_admission_team.triggered.connect(self.open_admission_team)

        # --- Меню "Помощь" ---
        self.ui.action_help.triggered.connect(self.show_about)

    # --- Методы "Справочники" ---

    def open_position(self):
         QMessageBox.information(self, "Справочник", "Должности")

    def open_departments(self):
        QMessageBox.information(self, "Справочник", "Отделения")

    def open_rooms(self):
         QMessageBox.information(self, "Справочник", "Помещения")

    def open_wards(self):
        QMessageBox.information(self, "Справочник", "Палаты")

    def open_staff_roles(self):
        QMessageBox.information(self, "Справочник", "Должности персонала")

    # --- Методы "Ввод" ---

    def open_patients(self):
        if not self.api.check_connection():
            QMessageBox.warning(self, "Ошибка", "Нет соединения с сервером")
            return

        patients = self.api.get_patients()
        if patients:
            dialog = QMainWindow(self)
            dialog.setWindowTitle("Список пациентов")
            dialog.resize(800, 400)

            table = QTableWidget(len(patients), 5, dialog)
            table.setHorizontalHeaderLabels(["ID", "ФИО", "Дата рождения", "Пол", "Телефон"])

            for i, patient in enumerate(patients):
                table.setItem(i, 0, QTableWidgetItem(str(patient['id'])))
                table.setItem(i, 1, QTableWidgetItem(patient['full_name']))
                table.setItem(i, 2, QTableWidgetItem(patient['birth_date']))
                table.setItem(i, 3, QTableWidgetItem(patient['gender']))
                table.setItem(i, 4, QTableWidgetItem(patient.get('phone', '')))

            table.resizeColumnsToContents()
            dialog.setCentralWidget(table)
            dialog.show()
        else:
            QMessageBox.information(self, "Информация", "Нет данных о пациентах")

    def open_staff(self):
        QMessageBox.information(self, "Ввод", "Персонал")

    def open_hospitalization(self):
        QMessageBox.information(self, "Ввод", "Госпитализация")

    def open_med_entry(self):
        QMessageBox.information(self, "Ввод", "Запись в истории болезни")

    def open_medication_order(self):
        QMessageBox.information(self, "Ввод", "Лист назначения")

    def open_payment(self):
        QMessageBox.information(self, "Ввод", "Оплата")

    def open_patient_admission(self):
        QMessageBox.information(self, "Ввод", "Прием пациентов")

    def open_admission_team(self):
        QMessageBox.information(self, "Ввод", "Дежурная бригада")

    # --- Методы "Помощь" ---

    def show_about(self):
        QMessageBox.about(self, "О программе",
            "HIMS v1.0\nГоспитальная информационная система\n\nРазработано с помощью PySide6")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
