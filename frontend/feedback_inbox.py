from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QTextEdit, QSplitter, QWidget,
    QComboBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


# Цвет фона строки (тёмный) и цвет текста (светлый, читаемый)
ROW_BG = {
    "Ошибка":      QColor(60, 30, 35),    # тёмно-красный
    "Предложение": QColor(25, 40, 65),    # тёмно-синий
    "Вопрос":      QColor(25, 52, 38),    # тёмно-зелёный
}
# Цвет бейджа (насыщенный) — для метки типа в деталях
BADGE_STYLE = {
    "Ошибка":      "background:#C62828; color:#FFE0E0; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600;",
    "Предложение": "background:#1565C0; color:#D0E8FF; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600;",
    "Вопрос":      "background:#2E7D32; color:#D0FFD8; border-radius:4px; padding:2px 8px; font-size:11px; font-weight:600;",
}
TYPE_ICONS = {"Ошибка": "🔴", "Предложение": "💡", "Вопрос": "❓"}
COLUMNS = ["ID", "Тип", "Тема", "Раздел", "Дата", "Автор (ID)", "Прочитано"]
TEXT_COLOR = QColor(220, 225, 235)   # светлый — читается на тёмном фоне


class FeedbackInboxDialog(QDialog):
    def __init__(self, api_client, feedback_data: list, current_user: dict, parent=None):
        super().__init__(parent)
        self.api = api_client
        self.feedback_data = feedback_data
        self.current_user = current_user
        self.is_admin = current_user.get("access_level", 0) >= 3

        self.setWindowTitle("Входящие обращения" if self.is_admin else "Мои обращения")
        self.setMinimumSize(900, 540)
        self.setModal(True)

        self._build_ui()
        self._apply_styles()
        self._populate_table(self.feedback_data)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ── Верхняя панель ──────────────────────────
        top_bar = QHBoxLayout()
        title_label = QLabel("📬  Входящие обращения" if self.is_admin else "📤  Мои обращения")
        title_label.setObjectName("inbox_title")
        top_bar.addWidget(title_label)
        top_bar.addStretch()

        top_bar.addWidget(QLabel("Показать:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все", "Ошибка", "Предложение", "Вопрос", "Только непрочитанные"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        top_bar.addWidget(self.filter_combo)
        layout.addLayout(top_bar)

        # ── Разделитель: таблица | детали ───────────
        splitter = QSplitter(Qt.Horizontal)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 40)
        self.table.setColumnWidth(1, 115)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(4, 130)
        self.table.setColumnWidth(5, 80)
        self.table.setColumnWidth(6, 90)
        self.table.setObjectName("feedback_table")
        self.table.currentItemChanged.connect(self._on_row_selected)
        splitter.addWidget(self.table)

        # Панель деталей
        detail_widget = QWidget()
        detail_widget.setObjectName("detail_panel")
        detail_layout = QVBoxLayout(detail_widget)
        detail_layout.setContentsMargins(14, 8, 8, 8)
        detail_layout.setSpacing(6)

        # Бейдж типа
        self.detail_badge = QLabel("")
        self.detail_badge.setFixedHeight(24)
        detail_layout.addWidget(self.detail_badge)

        # Тема
        self.detail_subject = QLabel("")
        self.detail_subject.setObjectName("detail_subject")
        self.detail_subject.setWordWrap(True)
        detail_layout.addWidget(self.detail_subject)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #E2E8F0;")
        detail_layout.addWidget(sep)

        desc_lbl = QLabel("Описание:")
        desc_lbl.setObjectName("detail_section_label")
        detail_layout.addWidget(desc_lbl)

        self.detail_desc = QTextEdit()
        self.detail_desc.setReadOnly(True)
        self.detail_desc.setObjectName("detail_desc")
        detail_layout.addWidget(self.detail_desc)

        self.meta_label = QLabel("")
        self.meta_label.setObjectName("meta_label")
        self.meta_label.setWordWrap(True)
        detail_layout.addWidget(self.meta_label)

        if self.is_admin:
            self.mark_read_btn = QPushButton("✓  Отметить как прочитанное")
            self.mark_read_btn.setObjectName("mark_btn")
            self.mark_read_btn.setFixedHeight(36)
            self.mark_read_btn.setEnabled(False)
            self.mark_read_btn.setCursor(Qt.PointingHandCursor)
            self.mark_read_btn.clicked.connect(self._mark_selected_read)
            detail_layout.addWidget(self.mark_read_btn)

        splitter.addWidget(detail_widget)
        splitter.setSizes([540, 340])
        layout.addWidget(splitter)

        # ── Нижняя панель ───────────────────────────
        bottom_bar = QHBoxLayout()
        self.stats_label = QLabel("")
        self.stats_label.setObjectName("stats_label")
        bottom_bar.addWidget(self.stats_label)
        bottom_bar.addStretch()

        close_btn = QPushButton("Закрыть")
        close_btn.setObjectName("close_btn")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        bottom_bar.addWidget(close_btn)
        layout.addLayout(bottom_bar)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: #0F1117;
                color: #E8EAF0;
            }

            QLabel#inbox_title {
                font-size: 15px;
                font-weight: 700;
                color: #E8EAF0;
            }

            QLabel {
                color: #E8EAF0;
            }

            QTableWidget#feedback_table {
                background: #1A1D27;
                border: 1px solid #2E3347;
                border-radius: 8px;
                gridline-color: #2E3347;
                font-size: 12px;
                color: #E8EAF0;
                alternate-background-color: #1E2230;
            }
            QHeaderView::section {
                background: #232634;
                color: #8B90A4;
                font-weight: 600;
                font-size: 11px;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #2E3347;
            }
            QTableWidget#feedback_table::item:selected {
                background: #1E3A5A;
                color: #E8EAF0;
            }
            QTableWidget#feedback_table::item:hover {
                background: #232E42;
            }

            QWidget#detail_panel {
                background: #1A1D27;
                border: 1px solid #2E3347;
                border-radius: 8px;
            }

            QLabel#detail_subject {
                font-size: 13px;
                font-weight: 600;
                color: #E8EAF0;
            }

            QLabel#detail_section_label {
                font-size: 10px;
                font-weight: 600;
                color: #8B90A4;
                letter-spacing: 0.5px;
            }

            QTextEdit#detail_desc {
                background: #232634;
                border: 1px solid #2E3347;
                border-radius: 6px;
                font-size: 12px;
                color: #C8CCDA;
                padding: 6px;
            }

            QLabel#meta_label {
                font-size: 10px;
                color: #8B90A4;
            }

            QPushButton#mark_btn {
                background: #4A9EFF;
                color: #0F1117;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#mark_btn:hover { background: #6AB3FF; }
            QPushButton#mark_btn:disabled {
                background: #232634;
                color: #4A5168;
                border: 1px solid #2E3347;
            }

            QPushButton#close_btn {
                background: #232634;
                color: #8B90A4;
                border: 1px solid #2E3347;
                border-radius: 6px;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton#close_btn:hover {
                background: #2E3347;
                color: #E8EAF0;
            }

            QLabel#stats_label {
                font-size: 11px;
                color: #8B90A4;
            }

            QComboBox {
                background: #232634;
                border: 1px solid #2E3347;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                color: #E8EAF0;
                min-width: 160px;
            }
            QComboBox:focus {
                border: 1px solid #4A9EFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background: #232634;
                border: 1px solid #2E3347;
                color: #E8EAF0;
                selection-background-color: #1E3A5A;
            }

            QScrollBar:vertical {
                background: #1A1D27;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #2E3347;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4A5168;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QSplitter::handle {
                background: #2E3347;
                width: 1px;
            }

            QFrame[frameShape="4"], QFrame[frameShape="5"] {
                color: #2E3347;
            }
        """)

    def _populate_table(self, data: list):
        self.table.setRowCount(0)
        unread_count = 0

        for item in data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 32)

            fb_type = item.get("feedback_type", "")
            is_read = item.get("is_read", True)
            bg = ROW_BG.get(fb_type, QColor(255, 255, 255))

            if not is_read:
                unread_count += 1

            values = [
                str(item.get("id", "")),
                f"{TYPE_ICONS.get(fb_type, '')} {fb_type}",
                item.get("subject", ""),
                item.get("section", "") or "—",
                str(item.get("created_at", ""))[:16].replace("T", " "),
                str(item.get("staff_id", "—")),
                "✓" if is_read else "●",
            ]

            for col, val in enumerate(values):
                cell = QTableWidgetItem(val)
                cell.setForeground(TEXT_COLOR)
                cell.setBackground(bg)

                # Непрочитанные — жирный шрифт + синяя точка в колонке «Прочитано»
                if not is_read:
                    f = cell.font()
                    f.setBold(True)
                    cell.setFont(f)
                if col == 6 and not is_read:
                    cell.setForeground(QColor(74, 158, 255))

                cell.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row, col, cell)

        total = len(data)
        self.stats_label.setText(
            f"Всего: {total}   |   Непрочитанных: {unread_count}"
            if self.is_admin else f"Всего обращений: {total}"
        )

    def _apply_filter(self, filter_text: str):
        if filter_text == "Все":
            filtered = self.feedback_data
        elif filter_text == "Только непрочитанные":
            filtered = [f for f in self.feedback_data if not f.get("is_read", True)]
        else:
            filtered = [f for f in self.feedback_data if f.get("feedback_type") == filter_text]
        self._populate_table(filtered)

    def _on_row_selected(self, current, previous):
        if current is None:
            return
        row = current.row()
        item_id_cell = self.table.item(row, 0)
        if not item_id_cell:
            return
        item_id = int(item_id_cell.text())
        item = next((f for f in self.feedback_data if f.get("id") == item_id), None)
        if not item:
            return

        fb_type = item.get("feedback_type", "")
        badge_style = BADGE_STYLE.get(fb_type, "background:#718096; color:white; border-radius:4px; padding:2px 8px;")
        self.detail_badge.setText(f"{TYPE_ICONS.get(fb_type, '')}  {fb_type}")
        self.detail_badge.setStyleSheet(badge_style)

        self.detail_subject.setText(item.get("subject", ""))
        self.detail_desc.setPlainText(item.get("description", ""))

        date_str = str(item.get("created_at", ""))[:16].replace("T", " ")
        section = item.get("section") or "не указан"
        staff_id = item.get("staff_id", "—")
        read_str = "✓ прочитано" if item.get("is_read") else "● не прочитано"
        self.meta_label.setText(
            f"Дата: {date_str}   ·   Раздел: {section}   ·   Автор ID: {staff_id}   ·   {read_str}"
        )

        if self.is_admin and hasattr(self, 'mark_read_btn'):
            self.mark_read_btn.setEnabled(not item.get("is_read", True))

    def _mark_selected_read(self):
        row = self.table.currentRow()
        if row < 0:
            return
        item_id = int(self.table.item(row, 0).text())
        result = self.api.mark_feedback_read(item_id)
        if result:
            for f in self.feedback_data:
                if f.get("id") == item_id:
                    f["is_read"] = True
                    break
            self._apply_filter(self.filter_combo.currentText())
            if hasattr(self, 'mark_read_btn'):
                self.mark_read_btn.setEnabled(False)
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить статус")
