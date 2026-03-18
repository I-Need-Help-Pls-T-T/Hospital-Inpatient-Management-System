from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QMessageBox, QFormLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class FeedbackDialog(QDialog):
    """
    Диалог обратной связи / сообщения об ошибке (SCRUM-45).
    Поля: Тема, Тип (Ошибка/Предложение/Вопрос), Описание.
    Автоматически передаёт текущий раздел приложения.
    """

    def __init__(self, api_client, current_section: str = "", parent=None):
        super().__init__(parent)
        self.api = api_client
        self.current_section = current_section

        self.setWindowTitle("Сообщить об ошибке / Обратная связь")
        self.setMinimumWidth(480)
        self.setModal(True)

        self._build_ui()
        self._apply_dark_styles()

    def _apply_dark_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: #1A1D27;
                color: #E8EAF0;
            }
            QLabel {
                color: #E8EAF0;
            }
            QFrame[frameShape="4"], QFrame[frameShape="5"] {
                color: #2E3347;
            }
            QFormLayout QLabel {
                color: #8B90A4;
                font-size: 11px;
                font-weight: 600;
            }
            QLineEdit, QTextEdit {
                background: #232634;
                border: 1.5px solid #2E3347;
                border-radius: 6px;
                padding: 6px 10px;
                color: #E8EAF0;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1.5px solid #4A9EFF;
                background: #1E2435;
            }
            QComboBox {
                background: #232634;
                border: 1.5px solid #2E3347;
                border-radius: 6px;
                padding: 5px 10px;
                color: #E8EAF0;
                font-size: 12px;
            }
            QComboBox:focus {
                border: 1.5px solid #4A9EFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background: #232634;
                border: 1px solid #2E3347;
                color: #E8EAF0;
                selection-background-color: #2E3347;
            }
            QPushButton {
                background: #232634;
                color: #8B90A4;
                border: 1px solid #2E3347;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2E3347;
                color: #E8EAF0;
            }
        """)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        title = QLabel("Обратная связь")
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Форма
        form = QFormLayout()
        form.setSpacing(10)

        # Тип обращения
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Ошибка", "Предложение", "Вопрос"])
        form.addRow("Тип:", self.type_combo)

        # Тема
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Кратко опишите проблему...")
        self.subject_edit.setMaxLength(255)
        form.addRow("Тема:*", self.subject_edit)

        # Раздел (автозаполнение, только чтение)
        self.section_label = QLabel(self.current_section or "—")
        self.section_label.setStyleSheet("color: #8B90A4;")
        form.addRow("Раздел:", self.section_label)

        # Описание
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Подробно опишите проблему или предложение...")
        self.description_edit.setMinimumHeight(120)
        form.addRow("Описание:*", self.description_edit)

        layout.addLayout(form)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)

        send_btn = QPushButton("Отправить")
        send_btn.setFixedWidth(110)
        send_btn.setDefault(True)
        send_btn.setStyleSheet(
            "QPushButton { background-color: #4A9EFF; color: #0F1117; border-radius: 6px; padding: 6px; font-weight: 700; }"
            "QPushButton:hover { background-color: #6AB3FF; }"
            "QPushButton:pressed { background-color: #2E7FE0; }"
        )
        send_btn.clicked.connect(self._on_send)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(send_btn)
        layout.addLayout(btn_layout)

    def _on_send(self):
        subject = self.subject_edit.text().strip()
        description = self.description_edit.toPlainText().strip()

        if not subject:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, укажите тему обращения.")
            self.subject_edit.setFocus()
            return

        if not description:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, добавьте описание.")
            self.description_edit.setFocus()
            return

        payload = {
            "subject": subject,
            "description": description,
            "feedback_type": self.type_combo.currentText(),
            "section": self.current_section or None,
        }

        result = self.api._make_request("POST", "/api/feedback/", json_data=payload)

        if result:
            QMessageBox.information(
                self, "Отправлено",
                "Ваше сообщение отправлено.\nСпасибо за обратную связь!"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, "Ошибка",
                "Не удалось отправить сообщение. Проверьте соединение с сервером."
            )
