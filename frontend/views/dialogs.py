# frontend/views/dialogs.py

from PyQt6.QtWidgets import (
    QDialog, QLabel, QMessageBox, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox, 
    QComboBox, QDateEdit, QTextEdit
)
from PyQt6.QtCore import QDate, Qt

from frontend.core.api_client import ApiClient

class BaseActionDialog(QDialog):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(300, 150)
        layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)
        self.input_1 = QLineEdit()
        self.input_2 = QLineEdit()
        self.form_layout.addRow("Поле 1:", self.input_1)
        self.form_layout.addRow("Поле 2:", self.input_2)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

class PatientDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Patient")
        self.setModal(True)
        self.resize(380, 260)

        layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        self.input_full_name = QLineEdit()

        self.input_birth_date = QDateEdit()
        self.input_birth_date.setCalendarPopup(True)
        self.input_birth_date.setDisplayFormat("yyyy-MM-dd")
        self.input_birth_date.setDate(QDate.currentDate().addYears(-30))

        self.input_gender = QComboBox()
        self.input_gender.addItems(["", "Мужской", "Женский"]) 

        self.input_address = QLineEdit()

        self.input_passport = QLineEdit()

        self.input_phone = QLineEdit()

        self.form_layout.addRow("Full Name*:", self.input_full_name)
        self.form_layout.addRow("Birth Date*:", self.input_birth_date)
        self.form_layout.addRow("Passport*:", self.input_passport)
        self.form_layout.addRow("Gender:", self.input_gender)
        self.form_layout.addRow("Address:", self.input_address)
        self.form_layout.addRow("Phone:", self.input_phone)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        """Собирает данные формы в словарь для FastAPI."""
        data = {
            "full_name": self.input_full_name.text().strip(),
            "birth_date": self.input_birth_date.date().toString("yyyy-MM-dd")
        }
        
        gender = self.input_gender.currentText()
        if gender: data["gender"] = gender
            
        address = self.input_address.text().strip()
        if address: data["address"] = address
            
        passport = self.input_passport.text().strip()
        if passport: data["passport"] = passport
            
        phone = self.input_phone.text().strip()
        if phone: data["phone"] = phone
            
        return data

class DynamicFormDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.inputs = {}
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        for field in fields:
            field_type = field.get('type', 'text')
            
            if field_type == 'enum' or field_type == 'boolean':
                widget = QComboBox()
                widget.addItems([""])
                if field_type == 'boolean':
                    widget.addItems(["True", "False"])
                else:
                    widget.addItems(field.get('choices', []))
            elif field_type == 'date':
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("yyyy-MM-dd")
                widget.setDate(QDate.currentDate())
            else:
                widget = QLineEdit()
                if field_type == 'password':
                    widget.setEchoMode(QLineEdit.EchoMode.Password)
            
            form_layout.addRow(field['label'], widget)
            self.inputs[field['name']] = widget

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        result = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText()
                if value == "":
                    continue
                if value == "True": value = True
                elif value == "False": value = False
            elif isinstance(widget, QDateEdit):
                value = widget.date().toString("yyyy-MM-dd")
            else:
                value = widget.text().strip()
                if not value: 
                    continue

            if name.endswith("_id") and isinstance(value, str) and value.isdigit():
                result[name] = int(value)
            else:
                result[name] = value
                
        return result
    
    def set_data(self, data: dict):
        for field_name, value in data.items():
            if field_name in self.inputs:
                self.inputs[field_name].setText(str(value) if value is not None else "")

from PyQt6.QtWidgets import QListWidget, QPushButton, QHBoxLayout

class BackupManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление резервными копиями")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton("Создать бэкап")
        self.btn_restore = QPushButton("Восстановить")
        self.btn_close = QPushButton("Закрыть")
        
        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_restore)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        self.btn_create.clicked.connect(self.handle_create)
        self.btn_restore.clicked.connect(self.handle_restore)
        self.btn_close.clicked.connect(self.reject)
        
        self.refresh_list()

        self.list_widget.setFocus()

    def refresh_list(self):
        self.list_widget.clear()
        try:
            backups = ApiClient.get_backups()
            self.list_widget.addItems(backups)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список: {e}")

    def handle_create(self):
        try:
            ApiClient.create_backup()
            QMessageBox.information(self, "Успех", "Резервная копия создана.")
            self.refresh_list()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания: {e}")

    def handle_restore(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите файл из списка!")
            return
            
        filename = selected.text()
        confirm = QMessageBox.question(self, "Подтверждение", 
                                     f"Восстановить базу из файла {filename}?\nТекущие данные будут перезаписаны!")
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                ApiClient.restore_backup(filename)
                QMessageBox.information(self, "Успех", "База данных успешно восстановлена.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка восстановления: {e}")

class SpecialQueryDialog(QDialog):
    """
    Диалог выбора особого запроса для текущей таблицы.
    Показывает список доступных запросов и возвращает выбранный handler.
    """
    def __init__(self, table_name: str, queries: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Особые запросы — {table_name.replace('_', ' ').capitalize()}")
        self.setModal(True)
        self.setMinimumWidth(300)
        self._queries = queries
        self._selected_idx = 0

        layout = QVBoxLayout(self)

        from PyQt6.QtWidgets import QLabel, QListWidget, QListWidgetItem
        layout.addWidget(QLabel("Выберите запрос:"))

        self._list = QListWidget()
        for q in queries:
            self._list.addItem(q["label"])
        self._list.setCurrentRow(0)
        self._list.itemDoubleClicked.connect(self._on_double_click)
        layout.addWidget(self._list)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        self._selected_idx = self._list.currentRow()
        self.accept()

    def _on_double_click(self):
        self._selected_idx = self._list.currentRow()
        self.accept()

    def selected_handler(self) -> str:
        return self._queries[self._selected_idx]["handler"]

class SubmitFeedbackDialog(QDialog):
    def __init__(self, current_table: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Написать в поддержку / Фидбэк")
        self.setModal(True)
        self.resize(400, 350)

        layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.input_subject = QLineEdit()
        self.input_subject.setPlaceholderText("Краткая суть проблемы...")

        self.input_type = QComboBox()
        self.input_type.addItems(["Ошибка", "Предложение", "Вопрос", "Другое"])
        
        self.input_table = QLineEdit(current_table)
        self.input_table.setReadOnly(True)
        self.input_table.setStyleSheet("background-color: #f0f0f0; color: #555;")
        
        self.input_message = QTextEdit()
        self.input_message.setPlaceholderText("Опишите проблему или предложение детально...")

        self.form_layout.addRow("Тема*:", self.input_subject)
        self.form_layout.addRow("Тип:", self.input_type)
        self.form_layout.addRow("Раздел (Таблица):", self.input_table)
        self.form_layout.addRow("Сообщение*:", self.input_message)
        layout.addLayout(self.form_layout)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def get_data(self) -> dict:
        """
        Возвращает словарь, который на 100% соответствует схеме FeedbackCreate.
        """
        subject = self.input_subject.text().strip()
        if not subject:
            subject = "Без темы"

        return {
            "subject": subject,
            "description": self.input_message.toPlainText().strip(),
            "feedback_type": self.input_type.currentText(),
            "section": self.input_table.text()
        }
    
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(350, 220)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        self.title_label = QLabel("АВТОРИЗАЦИЯ")
        self.title_label.setObjectName("HeaderLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.form_layout = QFormLayout()
        self.form_layout.setSpacing(10)

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Введите логин...")
        
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль...")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.form_layout.addRow("Логин:", self.input_username)
        self.form_layout.addRow("Пароль:", self.input_password)
        layout.addLayout(self.form_layout)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_login = QPushButton("Войти")
        self.btn_login.setObjectName("PrimaryButton")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_login)
        layout.addLayout(btn_layout)

        # Подключения
        self.btn_login.clicked.connect(self.attempt_login)
        self.btn_cancel.clicked.connect(self.reject)
        self.input_password.returnPressed.connect(self.attempt_login)
        self.input_username.returnPressed.connect(lambda: self.input_password.setFocus())

    def attempt_login(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните оба поля!")
            return

        try:
            ApiClient.login(username, password)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка авторизации", str(e))
            self.input_password.clear()
            self.input_password.setFocus()