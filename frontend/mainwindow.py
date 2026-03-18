import sys
import os
import subprocess
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

root_dir = os.path.dirname(current_dir)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from PySide6.QtWidgets import (QApplication, QMainWindow, QMessageBox,
                            QTableWidget, QTableWidgetItem, QVBoxLayout,
                            QWidget, QHeaderView, QInputDialog, QDialog,
                            QAbstractItemView)
from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from ui_form import Ui_MainWindow
from frontend.patient_dialog import PatientDialog
from frontend.feedback_dialog import FeedbackDialog

class MainWindow(QMainWindow):
    def __init__(self, api_client, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.current_section = "patients"
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("HIMS - Система управления стационарным лечением")
        self.showMaximized()

        self.setup_table_ui()

        self.setup_connections()

        # Применяем права доступа — скрываем недоступные элементы меню
        self._access_level = 0
        self.apply_access_level()

        # Стартовый экран (пациенты)
        self.open_patients()

        # Уведомление об непрочитанных обращениях (только для администратора)
        self._check_unread_feedback()

    def setup_table_ui(self):
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.table.verticalHeader().setVisible(False)

        self.setCentralWidget(self.central_widget)

    def perform_auto_login(self):
        """Авторизация под админом"""
        if self.api.check_connection():
            if self.api.login("admin", "admin"):
                self.statusBar().showMessage("Авторизован: Администратор", 5000)
            else:
                self.statusBar().showMessage("Ошибка входа! Проверьте данные в БД", 5000)

    def check_server_connection(self):
        if self.api.check_connection():
            self.statusBar().showMessage("Сервер онлайн", 5000)
        else:
            self.statusBar().showMessage("Нет связи с сервером", 5000)
            reply = QMessageBox.question(self, "Ошибка", "Сервер не отвечает. Запустить его?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.start_server()

    def start_server(self):
        try:
            venv_python = os.path.join(root_dir, ".qtcreator", "Python_3_12_9venv", "Scripts", "python.exe")
            env = os.environ.copy()
            env["PYTHONPATH"] = root_dir

            subprocess.Popen(
                [venv_python, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
                cwd=root_dir, env=env
            )
            time.sleep(3)
            self.update_status()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить сервер: {e}")

    def update_status(self):
        status = "онлайн" if self.api.check_connection() else "офлайн"
        self.statusBar().showMessage(f"Статус сервера: {status}", 2000)

    # ──────────────────────────────────────────────────────────────────
    #  SCRUM-56: Управление правами доступа в UI
    # ──────────────────────────────────────────────────────────────────

    # Минимальный уровень для ПРОСМОТРА раздела
    SECTION_MIN_LEVEL = {
        # Справочники — уровень 2+
        "positions":         2,
        "departments":       2,
        "rooms":             2,
        "wards":             2,
        "staff_roles":       2,
        # Ввод — уровень 1+
        "admissions":        1,
        "hospitalizations":  1,
        "patients":          1,
        "staff":             1,
        # Ввод — более строгие (врачебные/админские)
        "admission_teams":   2,
        "med_entries":       2,
        "medication_orders": 2,
        "payments":          3,
        # Система
        "system":            3,
    }

    # Минимальный уровень для ИЗМЕНЕНИЯ (добавить/редактировать)
    SECTION_EDIT_LEVEL = {
        # Справочники — только уровень 3
        "positions":         3,
        "departments":       3,
        "rooms":             3,
        "wards":             3,
        "staff_roles":       3,
        # Ввод — уровень 2 (кроме спец. разделов)
        "admission_teams":   2,
        "admissions":        2,
        "hospitalizations":  2,
        "med_entries":       2,
        "medication_orders": 2,
        "patients":          2,
        # Ввод — только уровень 3
        "payments":          3,
        "staff":             3,
    }

    #
    def apply_access_level(self):
        user_info = self.api.get_current_user_info()
        level = user_info.get("access_level", 0) if user_info else 0
        self._access_level = level

        ui = self.ui

        # ── Меню «Справочники» ───────────────────────────────────────
        # Видны только с уровня 2 (уровень 1 — меню скрыто целиком)
        for action in [ui.action_position, ui.action_department,
                       ui.action_room, ui.action_ward, ui.action_staff_role]:
            action.setVisible(level >= 2)
        ui.menu_directory.menuAction().setVisible(level >= 2)

        # ── Меню «Ввод» ──────────────────────────────────────────────
        # Уровень 1+: Базовые таблицы (Пациенты, Госпитализации и т.д.)
        for action in [ui.action_patient, ui.action_staff,
                       ui.action_hospitalization, ui.action_patient_admission]:
            action.setVisible(level >= 1)

        # Уровень 2+: Специфический ввод (Мед. записи, бригады)
        for action in [ui.action_med_entry, ui.action_medication_order,
                       ui.action_admission_team]:
            action.setVisible(level >= 2)

        # Уровень 3: Оплаты
        ui.action_payment.setVisible(level >= 3)

        # ── Меню «Операции» ──────────────────────────────────────────
        # Просмотр ID и Поиск — всем, у кого есть хоть какой-то доступ
        ui.action_get_by_id.setVisible(level >= 1)
        ui.action_search.setVisible(level >= 1)

        # Добавление/редактирование — только с уровня 2
        ui.action_add_record.setVisible(level >= 2)
        ui.action_refresh_data.setVisible(level >= 2)

        # Удаление и Бэкапы — строго уровень 3
        ui.action_delete_record.setVisible(level >= 3)
        ui.action_create_backup.setVisible(level >= 3)

        # Обратная связь
        if hasattr(ui, 'action_report_bug'):
            ui.action_report_bug.setVisible(level >= 1)
        if hasattr(ui, 'action_view_feedback'):
            ui.action_view_feedback.setVisible(level >= 3)

        # Обновляем статусную строку
        role_names = {0: "Грузчик/Персонал (без доступа)", 1: "Сотрудник (просмотр)",
                      2: "Врач (редактирование)", 3: "Администратор"}
        role_name = role_names.get(level, "Неизвестно")
        name = user_info.get("full_name", "Пользователь") if user_info else ""
        self.statusBar().showMessage(f"Авторизован: {name} | Роль: {role_name}", 8000)

    def can_edit_current_section(self) -> bool:
        """Проверяет, может ли текущий пользователь редактировать открытый раздел."""
        required = self.SECTION_EDIT_LEVEL.get(self.current_section, 3)
        return self._access_level >= required

    def can_view_current_section(self) -> bool:
        """Проверяет, может ли текущий пользователь просматривать открытый раздел."""
        required = self.SECTION_MIN_LEVEL.get(self.current_section, 1)
        return self._access_level >= required

    def _update_operations_for_section(self):
        """
        Динамически обновляет доступность кнопок «Операции» при смене раздела.
        Вызывается каждый раз при открытии любого раздела через _open_section.

        Логика:
          - Добавить / Редактировать: видны только если can_edit_current_section()
          - Удалить: только уровень 3 (глобальное правило)
          - Подсказка в статусной строке — режим «только чтение» или «редактирование»
        """
        can_edit = self.can_edit_current_section()
        level    = self._access_level
        ui       = self.ui

        # Кнопки добавления и редактирования — зависят от раздела
        ui.action_add_record.setEnabled(can_edit)
        ui.action_refresh_data.setEnabled(can_edit)   # «Редактировать выбранное»

        # Удаление — только level 3, жёсткое правило
        ui.action_delete_record.setEnabled(level >= 3)

        if can_edit:
            ui.action_add_record.setToolTip("Добавить запись")
            ui.action_refresh_data.setToolTip("Редактировать выбранную запись")
        else:
            edit_required = self.SECTION_EDIT_LEVEL.get(self.current_section, 3)
            tip = f"Для редактирования этого раздела нужен уровень доступа {edit_required}"
            ui.action_add_record.setToolTip(tip)
            ui.action_refresh_data.setToolTip(tip)

        # Индикатор режима в статусной строке
        section_titles = {
            "patients": "Пациенты", "staff": "Персонал",
            "hospitalizations": "Госпитализации", "admissions": "Приёмы",
            "admission_teams": "Бригады", "med_entries": "История болезни",
            "medication_orders": "Назначения", "payments": "Оплаты",
            "positions": "Должности", "departments": "Отделения",
            "rooms": "Помещения", "wards": "Палаты", "staff_roles": "Роли",
        }
        section_name = section_titles.get(self.current_section, self.current_section)
        role_name = {0: "Нет доступа", 1: "Сотрудник", 2: "Врач", 3: "Администратор"}.get(level, "?")

        if can_edit:
            mode = "✏ редактирование"
        else:
            mode = "👁 только просмотр"

        self.statusBar().showMessage(
            f"{section_name}   |   {role_name}   |   {mode}", 6000
        )

    def setup_connections(self):
        """Привязка всех action из UI к методам класса"""
        self.ui.action_exit.triggered.connect(self.close)

        # Справочники
        self.ui.action_position.triggered.connect(self.open_position)
        self.ui.action_department.triggered.connect(self.open_departments)
        self.ui.action_room.triggered.connect(self.open_rooms)
        self.ui.action_ward.triggered.connect(self.open_wards)
        self.ui.action_staff_role.triggered.connect(self.open_staff_roles)

        # Ввод
        self.ui.action_patient.triggered.connect(self.open_patients)
        self.ui.action_staff.triggered.connect(self.open_staff)
        self.ui.action_hospitalization.triggered.connect(self.open_hospitalization)
        self.ui.action_med_entry.triggered.connect(self.open_med_entries)
        self.ui.action_medication_order.triggered.connect(self.open_medication_orders)
        self.ui.action_payment.triggered.connect(self.open_payments)
        self.ui.action_patient_admission.triggered.connect(self.open_admissions)
        self.ui.action_admission_team.triggered.connect(self.open_admission_teams)

        # Операции
        self.ui.action_get_by_id.triggered.connect(self.handle_get_by_id)
        self.ui.action_search.triggered.connect(self.handle_search)
        self.ui.action_add_record.triggered.connect(self.handle_add_record)
        self.ui.action_delete_record.triggered.connect(self.handle_delete)
        self.ui.action_refresh_data.triggered.connect(self.handle_edit_selected)
        self.ui.action_create_backup.triggered.connect(self.run_backup_tool)

        if hasattr(self.ui, 'action_list_backups'):
            self.ui.action_list_backups.triggered.connect(self.show_backups_dialog)

        # Обратная связь
        if hasattr(self.ui, 'action_report_bug'):
            self.ui.action_report_bug.triggered.connect(self.show_feedback_dialog)
        if hasattr(self.ui, 'action_view_feedback'):
            self.ui.action_view_feedback.triggered.connect(self.open_feedback_inbox)

        # Помощь
        self.ui.action_help.triggered.connect(self.show_about)

        # Действия - двойной клик для редактирования
        self.table.doubleClicked.connect(self.handle_edit_record)

    # Колонки, скрытые от пользователей с уровнем < 3
    SENSITIVE_COLUMNS = {"login", "password", "password_hash", "hashed_password"}

    def display_data(self, data, title):
        """Универсальная отрисовка таблиц с растягиванием на весь экран"""
        if not data:
            self.statusBar().showMessage(f"Данные '{title}' не найдены", 5000)
            self.table.setRowCount(0)
            return

        headers = [k for k, v in data[0].items() if not isinstance(v, (dict, list))]

        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(data))

        header = self.table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        # Скрываем чувствительные колонки для не-администраторов
        for col_idx, col_name in enumerate(headers):
            if col_name in self.SENSITIVE_COLUMNS and self._access_level < 3:
                self.table.setColumnHidden(col_idx, True)
            else:
                self.table.setColumnHidden(col_idx, False)

        # Очищаем сохраненные оригинальные цвета при загрузке новых данных
        if hasattr(self, "original_colors"):
            delattr(self, "original_colors")

        for row_idx, row_data in enumerate(data):
            for col_idx, key in enumerate(headers):
                val = row_data.get(key, "")
                display_val = str(val) if val is not None else ""

                item = QTableWidgetItem(display_val)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)

        self.statusBar().showMessage(f"Отображено: {title} ({len(data)} зап.)")

        if self._access_level < 2:
                # Полностью запрещаем любые попытки редактирования через GUI для 1 уровня
                self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            # Разрешаем запуск редактирования (по двойному клику или кнопке) для 2 и 3 уровней
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

    def _open_section(self, section_key: str, fetch_fn, title: str, min_level: int = None):
        """Универсальный открыватель раздела с проверкой прав."""
        required = min_level if min_level is not None else self.SECTION_MIN_LEVEL.get(section_key, 1)
        if self._access_level < required:
            QMessageBox.warning(
                self, "Доступ ограничен",
                f"Для просмотра раздела «{title}» требуется уровень доступа {required}.\n"
                f"Ваш уровень: {self._access_level}."
            )
            return
        self.current_section = section_key
        self.display_data(fetch_fn(), title)
        self._update_operations_for_section()

    def open_position(self):
        self._open_section("positions", self.api.get_positions, "Должности")

    def open_departments(self):
        self._open_section("departments", self.api.get_departments, "Отделения")

    def open_rooms(self):
        self._open_section("rooms", self.api.get_rooms, "Помещения")

    def open_wards(self):
        self._open_section("wards", self.api.get_wards, "Палаты")

    def open_staff_roles(self):
        self._open_section("staff_roles", self.api.get_staff_roles, "Роли персонала")

    def open_patients(self):
        self._open_section("patients", self.api.get_patients, "Пациенты")

    def open_staff(self):
        self._open_section("staff", self.api.get_staff, "Персонал")

    def open_hospitalization(self):
        self._open_section("hospitalizations", self.api.get_hospitalizations, "Госпитализации")

    def open_med_entries(self):
        self._open_section("med_entries", self.api.get_med_entries, "История болезни")

    def open_medication_orders(self):
        self._open_section("medication_orders", self.api.get_medication_orders, "Листы назначений")

    def open_payments(self):
        self._open_section("payments", self.api.get_payments, "Оплаты")

    def open_admissions(self):
        self._open_section("admissions", self.api.get_admissions, "Приемы пациентов")

    def open_admission_teams(self):
        self._open_section("admission_teams", self.api.get_admission_teams, "Дежурные бригады")

    def _check_unread_feedback(self):
        """Показывает уведомление если есть непрочитанные обращения (только администратор)"""
        try:
            count = self.api.get_unread_feedback_count()
            if count > 0:
                reply = QMessageBox.information(
                    self, "Новые обращения",
                    f"У вас {count} непрочитанных обращений от пользователей.\n"
                    "Открыть раздел «Обращения»?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.open_feedback_inbox()
        except Exception:
            pass

    def open_feedback_inbox(self):
        """Открыть раздел просмотра обращений (администратор — все, остальные — свои)"""
        current_user = self.api.get_current_user_info()
        if not current_user:
            QMessageBox.warning(self, "Ошибка", "Не удалось получить данные пользователя")
            return

        data = self.api.get_feedback()
        if data is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить обращения")
            return

        from frontend.feedback_inbox import FeedbackInboxDialog
        dialog = FeedbackInboxDialog(self.api, data, current_user, parent=self)
        dialog.exec()

    def show_feedback_dialog(self):
        """Открыть диалог обратной связи / сообщения об ошибке (SCRUM-45)"""
        dialog = FeedbackDialog(self.api, current_section=self.current_section, parent=self)
        dialog.exec()

    def show_about(self):
        QMessageBox.about(self, "О программе", "HIMS v1.0\nСистема управления больницей")

    # Обработчики операций
    def handle_get_by_id(self):
        """Поиск по ID — подсвечивает найденную строку и прокручивает к ней"""
        id_val, ok = QInputDialog.getInt(self, "Поиск по ID", f"Введите ID ({self.current_section}):")
        if not ok:
            return

        # Ищем строку в уже загруженной таблице
        found_row = None
        for row in range(self.table.rowCount()):
            for col in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(col)
                if header and header.text().lower() in ('id', '№', 'номер'):
                    item = self.table.item(row, col)
                    if item and item.text() == str(id_val):
                        found_row = row
                    break
            if found_row is not None:
                break

        if found_row is None:
            self.statusBar().showMessage(f"Запись с ID {id_val} не найдена в разделе «{self.current_section}»", 5000)
            return

        # Сохраняем оригинальные цвета (если ещё не сохранены)
        if not hasattr(self, 'original_colors'):
            self.original_colors = {}
            for r in range(self.table.rowCount()):
                for c in range(self.table.columnCount()):
                    it = self.table.item(r, c)
                    if it:
                        self.original_colors[(r, c)] = it.background()

        # Сбрасываем предыдущую подсветку
        for (r, c), color in self.original_colors.items():
            it = self.table.item(r, c)
            if it:
                it.setBackground(color)

        # Подсвечиваем найденную строку
        highlight_color = QColor(255, 255, 0, 150)
        for col in range(self.table.columnCount()):
            it = self.table.item(found_row, col)
            if it:
                it.setBackground(highlight_color)

        # Прокручиваем и выделяем
        self.table.scrollToItem(self.table.item(found_row, 0), QAbstractItemView.PositionAtCenter)
        self.table.selectRow(found_row)

        self.statusBar().showMessage(
            f"Найдена запись ID {id_val}. Нажмите на любую ячейку для сброса выделения.", 6000
        )

        # Подключаем сброс подсветки по клику
        try:
            self.table.clicked.disconnect(self.clear_highlight)
        except:
            pass
        self.table.clicked.connect(self.clear_highlight)

    def handle_search(self):
        """Поиск с выделением найденных строк цветом"""
        query, ok = QInputDialog.getText(self, "Поиск", "Введите поисковый запрос:")
        if ok and query:
            # Получаем все данные через API
            all_data = self.api._make_request("GET", f"/api/{self.current_section}/")

            if not all_data:
                self.statusBar().showMessage(f"Нет данных для поиска в разделе {self.current_section}", 5000)
                return

            # Сохраняем оригинальные цвета всех ячеек перед поиском
            if not hasattr(self, 'original_colors'):
                self.original_colors = {}

                for row in range(self.table.rowCount()):
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            # Сохраняем оригинальный цвет фона
                            self.original_colors[(row, col)] = item.background()

            # Сбрасываем все ячейки к оригинальным цветам
            for (row, col), color in self.original_colors.items():
                item = self.table.item(row, col)
                if item:
                    item.setBackground(color)

            # Ищем совпадения
            found_rows = []
            query_lower = query.lower()

            for row_idx, row_data in enumerate(all_data):
                # Проверяем все значения строки на наличие запроса
                row_values = ' '.join(str(v).lower() for v in row_data.values() if v is not None)

                if query_lower in row_values:
                    found_rows.append(row_idx)

            if found_rows:
                # Выделяем найденные строки ярко-желтым цветом
                highlight_color = QColor(255, 255, 0, 150)  # Более яркий желтый

                for row_idx in found_rows:
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row_idx, col)
                        if item:
                            item.setBackground(highlight_color)

                # Прокручиваем к первому найденному результату
                first_found = found_rows[0]
                self.table.scrollToItem(self.table.item(first_found, 0), QAbstractItemView.PositionAtCenter)
                self.table.selectRow(first_found)  # Выделяем первую найденную строку (голубым цветом выделения)

                # Показываем статистику
                self.statusBar().showMessage(
                    f"Найдено совпадений: {len(found_rows)}. "
                    f"Выделено желтым цветом. Нажмите на любую ячейку для сброса выделения.",
                    5000
                )

                # Подключаем обработчик для сброса выделения при клике
                try:
                    self.table.clicked.disconnect(self.clear_highlight)
                except:
                    pass
                self.table.clicked.connect(self.clear_highlight)
            else:
                self.statusBar().showMessage(f"Совпадений по запросу '{query}' не найдено", 5000)

    def clear_highlight(self):
        """Сбрасывает выделение цветом при клике на таблицу и возвращает оригинальные цвета"""
        # Возвращаем оригинальные цвета всем ячейкам
        if hasattr(self, 'original_colors'):
            for (row, col), color in self.original_colors.items():
                item = self.table.item(row, col)
                if item:
                    item.setBackground(color)

        # Отключаем обработчик
        try:
            self.table.clicked.disconnect(self.clear_highlight)
        except:
            pass

        self.statusBar().showMessage("Выделение сброшено", 2000)


    def handle_add_record(self):
        """Обработка добавления записи в зависимости от текущего раздела"""
        if not self.can_edit_current_section():
            QMessageBox.warning(self, "Доступ ограничен",
                f"У вас недостаточно прав для добавления записей в раздел «{self.current_section}».")
            return
        if self.current_section == "patients":
            self.add_patient()
        else:
            QMessageBox.information(self, "Инфо",
                f"Добавление для раздела '{self.current_section}' пока не реализовано")

    def add_patient(self):
        """Открытие диалога для добавления нового пациента"""
        dialog = PatientDialog(self.api, self, access_level=self._access_level)

        if dialog.exec() == QDialog.Accepted:
            try:
                patient_data = dialog.get_patient_data()
                result = self.api.create_patient(patient_data)

                if result:
                    QMessageBox.information(
                        self, "Успех",
                        f"Пациент {patient_data['full_name']} успешно добавлен!"
                    )
                    self.open_patients()
                else:
                    QMessageBox.critical(
                        self, "Ошибка",
                        "Не удалось добавить пациента. Проверьте данные и попробуйте снова."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка",
                    f"Произошла ошибка при добавлении пациента: {str(e)}"
                )

    def handle_edit_record(self, index):
        """Редактирование записи по двойному клику"""
        if not self.can_edit_current_section():
            self.statusBar().showMessage(
                f"Раздел «{self.current_section}»: только просмотр (недостаточно прав)", 4000)
            return

        # 2. Специфическая проверка для 2-го уровня (Врачи)
        if self._access_level == 2:
            if self.current_section in ["staff", "payments"]:
                QMessageBox.warning(
                    self, "Доступ ограничен",
                    f"Редактирование раздела «{self.current_section}» доступно только администратору."
                )
                return

        # 3. Логика открытия диалогов
        if self.current_section == "patients":
            row = index.row()
            # Поиск ID в колонках
            patient_id = None
            for col in range(self.table.columnCount()):
                header = self.table.horizontalHeaderItem(col)
                if header and header.text().lower() in ['id', '№', 'номер']:
                    patient_id = int(self.table.item(row, col).text())
                    break

            if patient_id is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось найти ID пациента")
                return

            try:
                patient = self.api.get_by_id("patients", patient_id)
                if patient:
                    dialog = PatientDialog(self.api, self, patient_data=patient, access_level=self._access_level)
                    dialog.setWindowTitle("Редактирование пациента")
                    if dialog.exec() == QDialog.Accepted:
                        patient_data = dialog.get_patient_data()
                        if self.api.update_patient(patient_id, patient_data):
                            QMessageBox.information(self, "Успех", "Данные обновлены!")
                            self.open_patients()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании: {e}")
        else:
            QMessageBox.information(
                self, "Инфо",
                f"Редактирование для раздела '{self.current_section}' будет добавлено в следующем обновлении."
            )

    def handle_delete(self):
        """Удаление выделенной строки (только для пользователей с уровнем доступа 3)"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления")
            return

        item_id = None
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col)
            if header and header.text().lower() in ['id', '№', 'номер']:
                item_id = self.table.item(current_row, col).text()
                break

        if item_id is None:
            QMessageBox.critical(self, "Ошибка", "Не удалось найти ID записи")
            return

        # Проверяем уровень доступа текущего пользователя
        current_user = self.api.get_current_user_info()
        if not current_user:
            QMessageBox.critical(self, "Ошибка", "Не удалось получить данные текущего пользователя")
            return

        if current_user.get("access_level", 0) < 3:
            QMessageBox.critical(
                self, "Доступ запрещён",
                "Удаление записей доступно только администратору (уровень доступа 3)."
            )
            return

        # Запрашиваем подтверждение удаления
        confirm = QMessageBox.question(
            self, "Подтверждение удаления",
            f"Вы уверены, что хотите удалить запись ID {item_id} из раздела «{self.current_section}»?\n"
            "Это действие необратимо.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        # Запрашиваем пароль текущего аккаунта
        password, ok = QInputDialog.getText(
            self, "Подтверждение пароля",
            "Введите пароль вашего аккаунта для подтверждения удаления:",
            QLineEdit.Password
        )
        if not ok or not password:
            self.statusBar().showMessage("Удаление отменено", 3000)
            return

        # Проверяем пароль через сервер
        login = current_user.get("login", "")
        if not self.api.verify_password(login, password):
            QMessageBox.critical(self, "Ошибка", "Неверный пароль. Удаление отменено.")
            return

        # Выполняем удаление
        endpoint = f"/api/{self.current_section}/{item_id}"
        success = self.api._make_request("DELETE", endpoint)
        if success is not None:
            QMessageBox.information(self, "Успех", "Запись успешно удалена")
            self.refresh_current_view()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось удалить запись. Проверьте сервер.")

    def refresh_current_view(self):
        """Обновляет таблицу для текущего активного раздела"""
        section_map = {
            "patients":          (self.open_patients,        "Пациенты"),
            "staff":             (self.open_staff,           "Персонал"),
            "hospitalizations":  (self.open_hospitalization, "Госпитализации"),
            "med_entries":       (self.open_med_entries,     "История болезни"),
            "medication_orders": (self.open_medication_orders, "Листы назначений"),
            "payments":          (self.open_payments,        "Оплаты"),
            "admissions":        (self.open_admissions,      "Приемы пациентов"),
            "admission_teams":   (self.open_admission_teams, "Дежурные бригады"),
            "departments":       (self.open_departments,     "Отделения"),
            "positions":         (self.open_position,        "Должности"),
            "rooms":             (self.open_rooms,           "Помещения"),
            "wards":             (self.open_wards,           "Палаты"),
            "staff_roles":       (self.open_staff_roles,     "Роли персонала"),
        }
        entry = section_map.get(self.current_section)
        if entry:
            entry[0]()
        else:
            self.statusBar().showMessage(f"Раздел '{self.current_section}' не поддерживает обновление", 3000)

    def handle_edit_selected(self):
        """Редактирование выделенной строки — аналог двойного клика (для кнопки «Обновить»)"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования")
            return
        index = self.table.model().index(current_row, 0)
        self.handle_edit_record(index)

    def edit_current_patient(self):
        """Устаревший метод, оставлен для совместимости"""
        self.handle_edit_selected()

    def run_backup_tool(self):
        """Вызов функции бэкапа из API"""
        if self._access_level < 3:
            QMessageBox.warning(self, "Доступ ограничен", "Создание резервных копий доступно только администратору.")
            return
        try:
            result = self.api.create_backup()
            if result:
                QMessageBox.information(self, "Бэкап", f"Резервная копия создана:\n{result.get('filename', '')}")
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать бэкап")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_backups_dialog(self):
        """Показывает список бэкапов и позволяет выбрать один"""
        if self._access_level < 3:
            QMessageBox.warning(self, "Доступ ограничен", "Управление резервными копиями доступно только администратору.")
            return
        backups = self.api.get_backups_list()

        if not backups:
            QMessageBox.information(self, "Бэкапы", "Список бэкапов пуст или недоступен.")
            return

        items = []
        for b in backups:
            size_mb = round(b['size'] / (1024 * 1024), 2)
            items.append(f"{b['filename']} ({size_mb} MB)")

        item, ok = QInputDialog.getItem(self, "Доступные бэкапы",
                                        "Выберите файл для восстановления:",
                                        items, 0, False)

        if ok and item:
            filename = item.split(" (")[0]
            self.confirm_restore(filename)

    def confirm_restore(self, filename):
        """Подтверждение и выполнение восстановления"""
        reply = QMessageBox.warning(
            self, "Внимание",
            f"Вы действительно хотите восстановить базу из файла {filename}?\n"
            "ВНИМАНИЕ: Все текущие данные будут удалены и заменены данными из бэкапа!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                result = self.api.restore_backup(filename)

                if result:
                    # После восстановления БД токен становится невалидным — переавторизуемся
                    import time
                    time.sleep(1)  # Даём серверу завершить восстановление
                    relogged = self.api.relogin()
                    if not relogged:
                        QMessageBox.warning(
                            self, "Внимание",
                            "База восстановлена, но не удалось переавторизоваться автоматически.\n"
                            "Перезапустите приложение."
                        )
                        return

                    QMessageBox.information(
                        self, "Успех",
                        f"База данных успешно восстановлена из файла:\n{filename}"
                    )
                    self.refresh_current_view()
                else:
                    QMessageBox.critical(
                        self, "Ошибка",
                        "Сервер не смог выполнить восстановление. Проверьте логи сервера."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при связи с сервером: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
