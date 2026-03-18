import sys
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class LoginDialog(QDialog):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.setWindowTitle("HIMS — Авторизация")
        self.setFixedSize(420, 410)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        self.card = QLabel(self)
        self.card.setObjectName("card")
        self.card.setGeometry(16, 16, 388, 378)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 140))
        self.card.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(44, 20, 44, 40)
        layout.setSpacing(0)

        # ── Кнопки управления окном ───────────────────────────────────
        wc_row = QHBoxLayout()
        wc_row.addStretch()

        minimize_btn = QPushButton("—")
        minimize_btn.setObjectName("wc_btn")
        minimize_btn.setFixedSize(26, 26)
        minimize_btn.setCursor(Qt.PointingHandCursor)
        minimize_btn.setToolTip("Свернуть")
        minimize_btn.clicked.connect(self.showMinimized)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("wc_close_btn")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setToolTip("Закрыть")
        close_btn.clicked.connect(self.reject)

        wc_row.addWidget(minimize_btn)
        wc_row.addSpacing(4)
        wc_row.addWidget(close_btn)
        layout.addLayout(wc_row)
        layout.addSpacing(16)

        # ── Заголовок ─────────────────────────────────────────────────
        logo_row = QHBoxLayout()
        cross_label = QLabel("✚")
        cross_label.setObjectName("cross")
        cross_label.setFixedSize(36, 36)
        cross_label.setAlignment(Qt.AlignCenter)
        logo_row.addWidget(cross_label)

        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel("HIMS")
        title.setObjectName("title")
        subtitle = QLabel("Система управления стационаром")
        subtitle.setObjectName("subtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        logo_row.addLayout(title_col)
        logo_row.addStretch()
        layout.addLayout(logo_row)
        layout.addSpacing(28)

        # ── Логин ─────────────────────────────────────────────────────
        login_label = QLabel("Логин")
        login_label.setObjectName("field_label")
        layout.addWidget(login_label)
        layout.addSpacing(4)
        self.login_input = QLineEdit()
        self.login_input.setObjectName("field")
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.login_input)
        layout.addSpacing(14)

        # ── Пароль ────────────────────────────────────────────────────
        pass_label = QLabel("Пароль")
        pass_label.setObjectName("field_label")
        layout.addWidget(pass_label)
        layout.addSpacing(4)
        self.password_input = QLineEdit()
        self.password_input.setObjectName("field")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.returnPressed.connect(self.handle_login)
        layout.addWidget(self.password_input)
        layout.addSpacing(24)

        # ── Кнопка входа ──────────────────────────────────────────────
        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("login_btn")
        self.login_button.setFixedHeight(42)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        # ── Ошибка ────────────────────────────────────────────────────
        self.error_label = QLabel("")
        self.error_label.setObjectName("error_label")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        layout.addSpacing(8)
        layout.addWidget(self.error_label)

        layout.addStretch()
        self.card.setLayout(layout)
        outer.addWidget(self.card)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog { background: transparent; }

            QLabel#card {
                background: #1A1D27;
                border-radius: 16px;
                border: 1px solid #2E3347;
            }
            QPushButton#wc_btn {
                background: #232634;
                color: #8B90A4;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#wc_btn:hover {
                background: #3A4060;
                color: #E8EAF0;
            }
            QPushButton#wc_close_btn {
                background: #232634;
                color: #8B90A4;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton#wc_close_btn:hover {
                background: #C0392B;
                color: white;
            }
            QLabel#cross {
                background: #4A9EFF;
                border-radius: 8px;
                color: #0F1117;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel#title {
                font-size: 22px;
                font-weight: 700;
                color: #E8EAF0;
                letter-spacing: 2px;
                padding-left: 10px;
            }
            QLabel#subtitle {
                font-size: 9px;
                color: #8B90A4;
                padding-left: 10px;
            }
            QLabel#field_label {
                font-size: 11px;
                font-weight: 600;
                color: #8B90A4;
            }
            QLineEdit#field {
                background: #232634;
                border: 1.5px solid #2E3347;
                border-radius: 8px;
                padding: 9px 14px;
                font-size: 13px;
                color: #E8EAF0;
            }
            QLineEdit#field:focus {
                border: 1.5px solid #4A9EFF;
                background: #1E2435;
            }
            QPushButton#login_btn {
                background: #4A9EFF;
                color: #0F1117;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }
            QPushButton#login_btn:hover { background: #6AB3FF; }
            QPushButton#login_btn:pressed { background: #2E7FE0; }
            QLabel#error_label {
                color: #FF6B6B;
                font-size: 11px;
            }
        """)

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text()

        if not login or not password:
            self._show_error("Заполните логин и пароль")
            return

        self.login_button.setText("Вхожу...")
        self.login_button.setEnabled(False)

        if self.api.login(login, password):
            self.accept()
        else:
            self.login_button.setText("Войти")
            self.login_button.setEnabled(True)
            self._show_error("Неверный логин или пароль")
            self.password_input.clear()
            self.password_input.setFocus()

    def _show_error(self, text: str):
        self.error_label.setText(f"⚠  {text}")
        self.error_label.setVisible(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and hasattr(self, '_drag_pos'):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
