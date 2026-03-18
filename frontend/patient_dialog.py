from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QFrame, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QDate
from api_client import APIClient


class PatientDialog(QDialog):
    """
    Диалог добавления / редактирования пациента.
    Поле «№ пациента» (ID) видно только пользователям с уровнем доступа 3.
    """

    def __init__(self, api_client: APIClient, parent=None,
                 patient_data=None, access_level: int = 0):
        super().__init__(parent)
        self.api = api_client
        self.patient_data = patient_data
        self.access_level = access_level
        self.is_edit = patient_data is not None

        self.setWindowTitle("Редактирование пациента" if self.is_edit else "Регистрация пациента")
        self.setMinimumWidth(520)
        self.setModal(True)
        # Убираем системную рамку — используем только кастомный заголовок
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self._build_ui()
        self._apply_styles()

        if self.is_edit:
            self._load_data()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Шапка
        header = QWidget()
        header.setObjectName("dlg_header")
        header.setFixedHeight(56)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 16, 0)

        icon = QLabel("🏥")
        icon.setFixedSize(28, 28)
        icon.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(icon)

        title_lbl = QLabel("Редактирование пациента" if self.is_edit else "Регистрация пациента")
        title_lbl.setObjectName("dlg_title")
        h_layout.addWidget(title_lbl)
        h_layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("header_close")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        h_layout.addWidget(close_btn)
        root.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("dlg_sep")
        root.addWidget(sep)

        # Тело
        body = QWidget()
        body.setObjectName("dlg_body")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 20, 24, 8)
        body_layout.setSpacing(16)

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(12)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)

        row = 0

        # ID — только уровень 3, только при редактировании
        if self.access_level >= 3 and self.is_edit:
            grid.addWidget(self._label("№ пациента"), row, 0)
            self.id_field = QLineEdit()
            self.id_field.setObjectName("field_readonly")
            self.id_field.setReadOnly(True)
            self.id_field.setPlaceholderText("—")
            grid.addWidget(self.id_field, row, 1, 1, 3)
            row += 1
        else:
            self.id_field = None

        # ФИО
        grid.addWidget(self._label("ФИО *"), row, 0)
        self.full_name_field = QLineEdit()
        self.full_name_field.setObjectName("field")
        self.full_name_field.setPlaceholderText("Иванов Иван Иванович")
        grid.addWidget(self.full_name_field, row, 1, 1, 3)
        row += 1

        # Дата рождения + Пол
        grid.addWidget(self._label("Дата рождения"), row, 0)
        self.birth_date_field = QDateEdit()
        self.birth_date_field.setObjectName("field")
        self.birth_date_field.setCalendarPopup(True)
        self.birth_date_field.setDisplayFormat("dd.MM.yyyy")
        self.birth_date_field.setDate(QDate.currentDate().addYears(-30))
        grid.addWidget(self.birth_date_field, row, 1)

        grid.addWidget(self._label("Пол"), row, 2)
        self.gender_field = QComboBox()
        self.gender_field.setObjectName("field")
        self.gender_field.addItems(["Женский", "Мужской"])
        grid.addWidget(self.gender_field, row, 3)
        row += 1

        # Адрес
        grid.addWidget(self._label("Адрес"), row, 0)
        self.address_field = QLineEdit()
        self.address_field.setObjectName("field")
        self.address_field.setPlaceholderText("г. Минск, ул. Ленина, д. 1, кв. 1")
        grid.addWidget(self.address_field, row, 1, 1, 3)
        row += 1

        # Паспорт + Телефон
        grid.addWidget(self._label("Паспорт"), row, 0)
        self.passport_field = QLineEdit()
        self.passport_field.setObjectName("field")
        self.passport_field.setPlaceholderText("KH1234567")
        self.passport_field.setMaxLength(9)
        grid.addWidget(self.passport_field, row, 1)

        grid.addWidget(self._label("Телефон"), row, 2)
        self.phone_field = QLineEdit()
        self.phone_field.setObjectName("field")
        self.phone_field.setPlaceholderText("375441234567")
        self.phone_field.setMaxLength(12)
        grid.addWidget(self.phone_field, row, 3)

        body_layout.addLayout(grid)

        hint = QLabel("* — обязательные поля")
        hint.setObjectName("hint_label")
        body_layout.addWidget(hint)
        root.addWidget(body)

        # Нижняя панель
        footer_sep = QFrame()
        footer_sep.setFrameShape(QFrame.HLine)
        footer_sep.setObjectName("dlg_sep")
        root.addWidget(footer_sep)

        footer = QWidget()
        footer.setObjectName("dlg_footer")
        footer.setFixedHeight(60)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(24, 0, 24, 0)
        f_layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setObjectName("btn_cancel")
        cancel_btn.setFixedSize(110, 36)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        f_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Сохранить" if self.is_edit else "Зарегистрировать")
        save_btn.setObjectName("btn_save")
        save_btn.setFixedSize(150, 36)
        save_btn.setDefault(True)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        f_layout.addWidget(save_btn)

        root.addWidget(footer)

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("form_label")
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return lbl

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: #1A1D27;
                border: 1px solid #2E3347;
                border-radius: 10px;
            }
            QWidget#dlg_header {
                background: #141720;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QLabel#dlg_title {
                font-size: 14px;
                font-weight: 700;
                color: #E8EAF0;
                padding-left: 8px;
            }
            QPushButton#header_close {
                background: transparent;
                color: #8B90A4;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#header_close:hover {
                background: #7B1D1D;
                color: #FF6B6B;
            }
            QFrame#dlg_sep {
                color: #2E3347;
                max-height: 1px;
            }
            QWidget#dlg_body { background: #1A1D27; }
            QWidget#dlg_footer {
                background: #141720;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QLabel#form_label {
                color: #8B90A4;
                font-size: 11px;
                font-weight: 600;
                min-width: 90px;
            }
            QLabel#hint_label {
                color: #4A5168;
                font-size: 10px;
            }
            QLineEdit#field, QComboBox#field, QDateEdit#field {
                background: #232634;
                border: 1.5px solid #2E3347;
                border-radius: 6px;
                padding: 6px 10px;
                color: #E8EAF0;
                font-size: 12px;
                min-height: 28px;
            }
            QLineEdit#field:focus, QDateEdit#field:focus {
                border: 1.5px solid #4A9EFF;
                background: #1E2435;
            }
            QLineEdit#field_readonly {
                background: #141720;
                border: 1.5px solid #232634;
                border-radius: 6px;
                padding: 6px 10px;
                color: #4A9EFF;
                font-size: 12px;
                font-weight: 700;
                min-height: 28px;
            }
            QComboBox#field::drop-down { border: none; width: 20px; }
            QComboBox#field QAbstractItemView {
                background: #232634;
                border: 1px solid #2E3347;
                color: #E8EAF0;
                selection-background-color: #1E3A5A;
            }
            QDateEdit#field::drop-down { border: none; width: 20px; }
            QCalendarWidget { background: #232634; color: #E8EAF0; }
            QPushButton#btn_cancel {
                background: #232634;
                color: #8B90A4;
                border: 1px solid #2E3347;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton#btn_cancel:hover {
                background: #2E3347;
                color: #E8EAF0;
            }
            QPushButton#btn_save {
                background: #4A9EFF;
                color: #0F1117;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#btn_save:hover { background: #6AB3FF; }
            QPushButton#btn_save:pressed { background: #2E7FE0; }
        """)

    def _load_data(self):
        """Заполнение формы данными при редактировании"""
        if self.id_field:
            self.id_field.setText(str(self.patient_data.get('id', '')))

        self.full_name_field.setText(self.patient_data.get('full_name', ''))

        birth_date = self.patient_data.get('birth_date')
        if birth_date:
            parts = birth_date.split('-')
            if len(parts) == 3:
                self.birth_date_field.setDate(
                    QDate(int(parts[0]), int(parts[1]), int(parts[2]))
                )

        gender = self.patient_data.get('gender', '')
        self.gender_field.setCurrentText(
            'Мужской' if gender in ('male', 'Мужской') else 'Женский'
        )

        self.address_field.setText(self.patient_data.get('address', ''))
        self.passport_field.setText(self.patient_data.get('passport', ''))
        self.phone_field.setText(self.patient_data.get('phone', ''))

    def get_patient_data(self) -> dict:
        """Сбор данных из формы"""
        qdate = self.birth_date_field.date()
        data = {
            'full_name':  self.full_name_field.text().strip(),
            'birth_date': f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}",
            'gender':     self.gender_field.currentText(),
            'address':    self.address_field.text().strip(),
            'passport':   self.passport_field.text().strip(),
            'phone':      self.phone_field.text().strip(),
        }
        if self.id_field and self.id_field.text():
            data['id'] = int(self.id_field.text())
        return data

    def validate(self) -> list:
        """Валидация формы, возвращает список ошибок"""
        errors = []

        full_name = self.full_name_field.text().strip()
        if not full_name:
            errors.append("ФИО обязательно для заполнения")
        elif len(full_name.split()) < 2:
            errors.append("Введите Фамилию и Имя (минимум 2 слова)")

        passport = self.passport_field.text().strip()
        if passport and not (
            len(passport) == 9
            and passport[:2].isalpha()
            and passport[2:].isdigit()
        ):
            errors.append("Паспорт: 2 буквы + 7 цифр (например, KH1234567)")

        phone = self.phone_field.text().strip()
        if phone and not (phone.isdigit() and len(phone) == 12):
            errors.append("Телефон: 12 цифр (например, 375441234567)")

        return errors

    def accept(self):
        """Переопределяем accept с валидацией"""
        errors = self.validate()
        if errors:
            QMessageBox.warning(self, "Ошибка ввода", "\n".join(errors))
            return
        super().accept()
