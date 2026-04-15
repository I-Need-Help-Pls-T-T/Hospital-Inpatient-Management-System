# frontend/views/mainwindow.py

import csv
from typing import Optional

from PyQt6.QtWidgets import (
    QInputDialog, QLineEdit, QMainWindow, QWidget, QVBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox,
    QMenuBar, QStatusBar, QFileDialog
)
from PyQt6.QtGui import QAction, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer

_HIGHLIGHT_BRUSH = QBrush(QColor(255, 165, 0, 100))

from frontend.workers.api_worker import ApiWorker
from frontend.core.api_client import ApiClient
from frontend.views.dialogs import BaseActionDialog, DynamicFormDialog, SubmitFeedbackDialog

from frontend.utils.config_generator import generate_table_configs
from frontend.utils.exporter import TableExporter

class MainWindow(QMainWindow):
    TABLE_CONFIGS = generate_table_configs()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Database")
        self.resize(1000, 600)

        self.current_table_view = "patients" 
        self.current_api_action = "get_patients"

        self.file_menu = None
        self.custom_menu_bar = None

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self._highlighted_rows: set[int] = set()

        self._setup_ui()
        self._setup_menu()
        self._setup_global_shortcuts()
        
        self.load_table_data(self.current_api_action)

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.table = QTableWidget()
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        self.table.setStyleSheet("""
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)


    def _setup_menu(self):
        self.custom_menu_bar = QMenuBar(self)
        self.setMenuBar(self.custom_menu_bar)

        # --- 1. &FILE (Alt+F) ---
        self.file_menu = self.custom_menu_bar.addMenu("&File") 
        if self.file_menu is not None:
            # Меню бэкапа (Ctrl + B) 
            backup_action = QAction("&Backup Database", self)
            backup_action.setShortcut("Ctrl+B")
            backup_action.triggered.connect(self.action_backup)
            self.file_menu.addAction(backup_action)

            # Экспорт (Ctrl+Shift+E)
            export_csv_action = QAction("Export to...", self)
            export_csv_action.setShortcut("Ctrl+Shift+E")
            export_csv_action.triggered.connect(self.action_export_data)
            self.file_menu.addAction(export_csv_action)
            
            self.file_menu.addSeparator()

            self.theme_action = QAction("Switch to &Dark Theme", self)
            self.theme_action.setShortcut("Ctrl+T")
            self.theme_action.triggered.connect(self.action_toggle_theme)
            self.file_menu.addAction(self.theme_action)

            self.file_menu.addSeparator()

            # Выход (Ctrl+E)
            exit_action = QAction("E&xit", self)
            exit_action.setShortcut("Ctrl+E")
            exit_action.triggered.connect(self.close)
            self.file_menu.addAction(exit_action)

        # --- 2. &OPERATIONS (Alt+O) ---
        operations_menu = self.custom_menu_bar.addMenu("&Operations")
        if operations_menu is not None:
            # Создать (Ctrl+A)
            create_action = QAction("&Add Record...", self)
            create_action.setShortcut("Ctrl+A")
            create_action.triggered.connect(self.action_create)
            operations_menu.addAction(create_action)

            # Просмотр/Обновление таблицы (Ctrl+V)
            view_action = QAction("&View/Refresh Table", self)
            view_action.setShortcut("Ctrl+V")
            view_action.triggered.connect(self.action_refresh)
            operations_menu.addAction(view_action)

            # Обновить запись (Ctrl+U)
            update_action = QAction("&Update Selected...", self)
            update_action.setShortcut("Ctrl+U")
            update_action.triggered.connect(self.action_update)
            operations_menu.addAction(update_action)

            # Удалить (Ctrl+D)
            delete_action = QAction("&Delete Selected", self)
            delete_action.setShortcut("Ctrl+D")
            delete_action.triggered.connect(self.action_delete)
            operations_menu.addAction(delete_action)

            operations_menu.addSeparator()

            # Спец запрос (Ctrl+Q)
            query_action = QAction("Special &Query...", self)
            query_action.setShortcut("Ctrl+Q")
            query_action.triggered.connect(self.action_special_query)
            operations_menu.addAction(query_action)

            # Сохранить результат (Ctrl+S)
            save_action = QAction("&Save Query Result", self)
            save_action.setShortcut("Ctrl+S")
            save_action.triggered.connect(self.action_save_result)
            operations_menu.addAction(save_action)

        # --- 3. &TABLES (Alt+T) ---
        tables_menu = self.custom_menu_bar.addMenu("&Tables")
        if tables_menu is not None:
            tables_config = [
                ("&Patients", "get_patients"),
                ("&Staff", "get_staff"),
                ("Staff &Roles", "get_staff_roles"),
                ("P&ositions", "get_positions"),
                ("&Departments", "get_departments"),
                ("&Rooms", "get_rooms"),
                ("&Wards", "get_wards"),
                ("&Admissions", "get_admissions"),
                ("&Admission Teams", "get_admission_teams"),
                ("&Hospitalizations", "get_hospitalizations"),
                ("&Med Entries", "get_med_entries"),
                ("Medication &Orders", "get_medication_orders"),
                ("Pa&yments", "get_payments")
            ]

            for label, action in tables_config:
                table_action = QAction(label, self)
                table_action.triggered.connect(lambda checked, a=action: self.switch_table(a))
                tables_menu.addAction(table_action)

        # --- 4. &HELP (Alt+H) ---
        help_menu = self.custom_menu_bar.addMenu("&Help")
        if help_menu is not None:
            submit_feedback_action = QAction("&Write Feedback...", self)
            submit_feedback_action.triggered.connect(self.action_submit_feedback)
            help_menu.addAction(submit_feedback_action)

            view_feedback_action = QAction("&View Feedback Table", self)
            view_feedback_action.triggered.connect(lambda: self.switch_table("get_feedback"))
            help_menu.addAction(view_feedback_action)

            help_menu.addSeparator()

            about_action = QAction("&About", self)
            about_action.triggered.connect(self.action_about)
            help_menu.addAction(about_action)

    def _setup_global_shortcuts(self):
        f10_shortcut = QAction(self)
        f10_shortcut.setShortcut(Qt.Key.Key_F10)
    
        def trigger_f10():
                if self.file_menu is not None and self.custom_menu_bar is not None:
                    self.custom_menu_bar.setFocus()
            
                    self.custom_menu_bar.setActiveAction(self.file_menu.menuAction())
            
                    from PyQt6.QtGui import QKeyEvent
                    from PyQt6.QtCore import QEvent
                    from PyQt6.QtWidgets import QApplication
            
                    event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Down, Qt.KeyboardModifier.NoModifier)
                    QApplication.postEvent(self.custom_menu_bar, event)

        f10_shortcut.triggered.connect(trigger_f10)
        self.addAction(f10_shortcut)

        esc_shortcut = QAction(self)
        esc_shortcut.setShortcut(Qt.Key.Key_Escape)
        esc_shortcut.triggered.connect(self.table.setFocus)
        self.addAction(esc_shortcut)

    # ==========================
    # ЛОГИКА ТАБЛИЦЫ
    # ==========================
    def switch_table(self, action_name: str):
        table_name = action_name.replace("get_", "")
        self.current_table_view = table_name
        self.current_api_action = action_name
        self.setWindowTitle(f"Medical Database - {table_name.replace('_', ' ').capitalize()}")
        self.load_table_data(action_name)
        
        self.table.setFocus()

    def action_refresh(self):
        # Ctrl+V: обновляет данные в текущей таблице
        self.load_table_data(self.current_api_action)

    def load_table_data(self, action_name: str):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(300)

        self.status_bar.showMessage(f"Loading {self.current_table_view} data...")
        self.worker = ApiWorker(action_name)
        self.worker.data_fetched.connect(self.populate_table)
        self.worker.error_occurred.connect(self.show_error)
        self.worker.start()

    def populate_table(self, data: list, highlight_text: Optional[str] = None):
        self.status_bar.showMessage(f"Data loaded successfully. Records: {len(data)}")
        self._highlighted_rows = set()

        table = self.table
        table.setSortingEnabled(False)
        table.blockSignals(True)
        table.setUpdatesEnabled(False)

        if not data:
            table.clearContents()
            table.setRowCount(0)
            table.setColumnCount(0)
            table.setUpdatesEnabled(True)
            table.blockSignals(False)
            return

        headers = list(data[0].keys())
        col_count = len(headers)
        row_count = len(data)

        if table.columnCount() != col_count:
            table.setColumnCount(col_count)
            table.setHorizontalHeaderLabels([str(h).capitalize() for h in headers])
        if table.rowCount() != row_count:
            table.setRowCount(row_count)

        hl_lower = highlight_text.lower() if highlight_text else None
        setItem = table.setItem
        QTWItem = QTableWidgetItem

        for row_idx, row_data in enumerate(data):
            is_highlight = bool(
                hl_lower and hl_lower in " ".join(str(v).lower() for v in row_data.values())
            )
            if is_highlight:
                self._highlighted_rows.add(row_idx)

            for col_idx, key in enumerate(headers):
                value = row_data.get(key, "")

                if key == "staff" and isinstance(value, dict):
                    display_text = value.get("full_name") or value.get("name") or "Unknown Staff"
                elif key == "payments":
                    display_text = "Оплачено" if (row_data.get("is_paid") or (isinstance(value, list) and value)) else "Ожидает"
                elif isinstance(value, bool):
                    display_text = "Да" if value else "Нет"
                else:
                    display_text = str(value) if value is not None else ""

                item = QTWItem(display_text)
                if is_highlight:
                    item.setBackground(_HIGHLIGHT_BRUSH)

                setItem(row_idx, col_idx, item)

        table.setUpdatesEnabled(True)
        table.blockSignals(False)
        table.setSortingEnabled(True)

    def _on_selection_changed(self):
        """При выборе строки снимает жёлтую подсветку с этой строки."""
        if not self._highlighted_rows:
            return
        current_row = self.table.currentRow()
        if current_row in self._highlighted_rows:
            self._highlighted_rows.discard(current_row)
            for col in range(self.table.columnCount()):
                item = self.table.item(current_row, col)
                if item:
                    item.setBackground(QBrush())
    
    def show_error(self, error_msg: str):
        self.status_bar.showMessage("Error loading data!")
        QMessageBox.critical(self, "API Error", f"Failed to fetch data:\n{error_msg}")

    # ==========================
    # ОПЕРАЦИИ И ДИАЛОГИ
    # ==========================
    def action_create(self):
        table_key = self.current_table_view.lower()
        fields = self.TABLE_CONFIGS.get(table_key)

        if not fields:
            QMessageBox.warning(self, "Ошибка", f"Конфигурация для таблицы '{table_key}' не найдена!")
            return

        dialog = DynamicFormDialog(f"Добавление: {self.current_table_view}", fields, self)
        
        if dialog.exec():
            data = dialog.get_data()
            
            for field in fields:
                field_name = field['name']
                if not data.get(field_name) and "опц." not in field['label'].lower():
                    QMessageBox.warning(self, "Ошибка валидации", f"Поле '{field['label']}' обязательно!")
                    return

            try:
                ApiClient.create_any(table_key, data)
                
                self.action_refresh()
                self.status_bar.showMessage(f"Запись в {table_key} успешно добавлена!", 5000)
            except Exception as e:
                error_detail = str(e)
                QMessageBox.critical(self, "Ошибка API", f"Не удалось создать запись:\n{error_detail}")
    
    def action_update(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Обновление", "Выберите строку!")
            return

        id_col = -1
        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col)
            if header and header.text() == "id":
                id_col = col
                break
    
        if id_col == -1: return

        id_item = self.table.item(current_row, id_col)
        target_id = id_item.text() if id_item else ""
        table_key = self.current_table_view.lower()
        fields = self.TABLE_CONFIGS.get(table_key)

        if not fields: return

        current_values = {}
        for col_idx in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(col_idx)
            if not header_item: continue
        
            header_text = header_item.text()
            cell_item = self.table.item(current_row, col_idx)
            cell_text = cell_item.text() if cell_item else ""

            for field in fields:
                if field['label'] == header_text:
                    current_values[field['name']] = cell_text

        dialog = DynamicFormDialog(f"Редактирование {table_key} (ID: {target_id})", fields, self)
    
        if hasattr(dialog, 'set_data'):
            dialog.set_data(current_values)
    
        if dialog.inputs:
            first_input = list(dialog.inputs.values())[0]
            first_input.setFocus()
            first_input.selectAll()

        if dialog.exec():
            new_data = dialog.get_data()
            try:
                ApiClient.update_any(table_key, int(target_id), new_data)
                self.action_refresh()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить: {e}")

    def action_delete(self):
        target_id = self._get_selected_row_id()
        if not target_id: return

        password, ok = QInputDialog.getText(self, 'Подтверждение', f'Пароль для удаления #{target_id}:', QLineEdit.EchoMode.Password)
        if ok and password:
            try:
                ApiClient.delete_any(self.current_table_view, int(target_id), password)
                self.action_refresh()
                self.status_bar.showMessage(f"Запись {target_id} удалена", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка удаления", str(e))
    
    def check_unread_feedback(self):
        """Проверяет наличие непрочитанных сообщений при старте (для Админов)"""
        try:
            count = ApiClient.get_unread_feedback_count()
            if count > 0:
                QMessageBox.information(
                    self, 
                    "Новые обращения", 
                    f"У вас есть непрочитанные обращения от пользователей ({count} шт.).\n"
                    "Перейдите в Help -> View Feedback Table для просмотра."
                )
        except Exception as e:
            pass

    def action_submit_feedback(self):
        """Открытие диалога для написания фидбэка"""
        dialog = SubmitFeedbackDialog(current_table=self.current_table_view, parent=self)
        
        if dialog.exec():
            data = dialog.get_data()
            if not data.get("description"):
                QMessageBox.warning(self, "Ошибка", "Сообщение не может быть пустым!")
                return
                
            try:
                ApiClient.submit_feedback(data)
                QMessageBox.information(self, "Успех", "Ваше обращение успешно отправлено. Спасибо!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось отправить обращение:\n{str(e)}")

    def _get_selected_row_id(self) -> str | None:
        """Помощник: возвращает ID выбранной строки или None, если ошибка."""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите строку!")
            return None

        for col in range(self.table.columnCount()):
            header = self.table.horizontalHeaderItem(col)
            if header and header.text().lower() == "id":
                item = self.table.item(current_row, col)
                return item.text() if item else None
        
        QMessageBox.critical(self, "Ошибка", "Колонка ID не найдена в этой таблице!")
        return None

    # ==========================
    # ОСОБЫЕ ЗАПРОСЫ
    # ==========================

    # Конфигурация запросов по таблицам.
    # Чтобы добавить новый запрос — дописать элемент в список нужной таблицы
    # и добавить соответствующий метод _query_<name>.
    SPECIAL_QUERIES = {
        "patients": [
            {"label": "Поиск по имени",    "handler": "_query_patients_by_name"},
            {"label": "Поиск по паспорту", "handler": "_query_patients_by_passport"},
        ]
    }

    def action_special_query(self):
        table_key = self.current_table_view.lower()
        queries = self.SPECIAL_QUERIES.get(table_key)

        if not queries:
            QMessageBox.information(
                self, "Особые запросы",
                f"Для таблицы '{table_key}' особые запросы не настроены."
            )
            return

        from frontend.views.dialogs import SpecialQueryDialog
        dialog = SpecialQueryDialog(table_key, queries, self)
        if dialog.exec():
            handler_name = dialog.selected_handler()
            handler = getattr(self, handler_name, None)
            if handler:
                handler()

    # ==========================
    # ЭКСПОРТ (ОТЧЕТЫ)
    # ==========================
    
    def action_export_data(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Экспорт", "Таблица пуста!")
            return

        filters = "Excel (*.xlsx);;CSV (*.csv);;HTML (*.html);;SQL (*.sql)"
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", f"{self.current_table_view}_report", filters)
        if not path: return

        headers = []
        for i in range(self.table.columnCount()):
            header_item = self.table.horizontalHeaderItem(i)
            headers.append(header_item.text() if header_item is not None else f"Column_{i}")

        rows = []
        for r in range(self.table.rowCount()):
            row_data = []
            for c in range(self.table.columnCount()):
                cell_item = self.table.item(r, c)
                row_data.append(cell_item.text() if cell_item is not None else "")
            rows.append(row_data)
        
        try:
            if path.endswith('.csv'): TableExporter.export_to_csv(path, headers, rows)
            elif path.endswith('.xlsx'): TableExporter.export_to_excel(path, headers, rows, self.current_table_view)
            elif path.endswith('.html'): TableExporter.export_to_html(path, headers, rows, self.current_table_view)
            elif path.endswith('.sql'): TableExporter.export_to_sql(path, headers, rows, self.current_table_view.lower())
            
            QMessageBox.information(self, "Успех", "Данные выгружены!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта:\n{e}")
    
    def action_toggle_theme(self):
        from PyQt6.QtWidgets import QApplication
        import frontend.core.theme_manager as tm
        
        app = QApplication.instance()
        
        global _HIGHLIGHT_BRUSH 
        
        if tm.CURRENT_THEME == "light":
            tm.apply_theme(app, "dark")
            self.theme_action.setText("Switch to &Light Theme")
            self.status_bar.showMessage("Тёмная тема включена", 3000)
            
            _HIGHLIGHT_BRUSH = QBrush(QColor(77, 170, 252, 80))
        else:
            tm.apply_theme(app, "light")
            self.theme_action.setText("Switch to &Dark Theme")
            self.status_bar.showMessage("Светлая тема включена", 3000)
            
            _HIGHLIGHT_BRUSH = QBrush(QColor(255, 165, 0, 100))
            
        viewport = self.table.viewport()
        if viewport is not None:
            viewport.update()

    # ---------- Запросы для таблицы patients ----------

    def _query_patients_by_name(self):
        name_query, ok = QInputDialog.getText(self, "Поиск по имени", "Введите имя пациента:")
        if not ok or not name_query.strip():
            return
        try:
            all_patients = ApiClient.get_all("patients")
            q = name_query.strip().lower()
            matched = sum(1 for p in all_patients if q in str(p.get("full_name", "")).lower())
            self.populate_table(all_patients, highlight_text=name_query.strip())
            self.status_bar.showMessage(f"Поиск по имени '{name_query}': выделено {matched} из {len(all_patients)} записей")
        except Exception as e:
            self.show_error(str(e))

    def _query_patients_by_passport(self):
        passport, ok = QInputDialog.getText(self, "Поиск по паспорту", "Введите номер паспорта:")
        if not ok or not passport.strip():
            return
        try:
            all_patients = ApiClient.get_all("patients")
            q = passport.strip().lower()
            matched = sum(1 for p in all_patients if q in str(p.get("passport", "")).lower())
            self.populate_table(all_patients, highlight_text=passport.strip())
            self.status_bar.showMessage(f"Поиск по паспорту '{passport}': выделено {matched} из {len(all_patients)} записей")
        except Exception as e:
            self.show_error(str(e))
    
    def action_save_result(self):
        QMessageBox.information(self, "Save", "Query result saved.")

    def action_backup(self):
        from frontend.views.dialogs import BackupManagerDialog
        dialog = BackupManagerDialog(self)
        dialog.exec()

        self.table.setFocus()
    
    def action_about(self):
        QMessageBox.about(self, "About", "Версия 2.0")