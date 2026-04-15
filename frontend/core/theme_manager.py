# frontend/core/theme_manager.py

WIREFRAME_STYLE = """
/* Общий фон и шрифт */
QWidget {
    background-color: #ffffff;
    color: #000000;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt; 
}

/* Специфичные классы */
QLabel#HeaderLabel {
    font-size: 16pt;
    font-weight: bold;
    color: #0078d7;
    margin-bottom: 10px;
}

/* Строгие рамки для таблиц */
QTableWidget {
    border: 2px solid #000000;
    gridline-color: #444444;
    background-color: #fafafa;
    alternate-background-color: #f0f0f0;
}
QTableWidget:focus { border: 2px solid #0078d7; }
QHeaderView::section {
    background-color: #e0e0e0;
    color: #000000;
    border: 1px solid #000000;
    font-weight: bold;
    padding: 4px;
}

/* Меню */
QMenuBar { background-color: #f0f0f0; border-bottom: 2px solid #000000; }
QMenuBar::item { padding: 6px 10px; }
QMenuBar::item:selected { background-color: #cccccc; }
QMenu { background-color: #ffffff; border: 2px solid #000000; }
QMenu::item { padding: 6px 40px 6px 20px; }
QMenu::item:selected { background-color: #dddddd; color: #000; }

/* Поля ввода */
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    border: 1px solid #000000;
    background-color: #ffffff;
    padding: 5px 8px;
    min-height: 24px;
    selection-background-color: #cccccc;
    selection-color: #000000;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 2px solid #0078d7;
    background-color: #f4f8ff;
}

/* Кнопки */
QPushButton {
    background-color: #e0e0e0;
    border: 1px solid #000000;
    border-radius: 3px;
    padding: 6px 15px;
    font-weight: bold;
    min-height: 24px;
}
QPushButton:hover { background-color: #d0d0d0; }
QPushButton:pressed { background-color: #aaaaaa; }
QPushButton:focus { border: 2px solid #0078d7; background-color: #e8f0fe; }

/* Главная кнопка (Например, логин) */
QPushButton#PrimaryButton {
    background-color: #0078d7;
    color: #ffffff;
    border: 1px solid #005a9e;
}
QPushButton#PrimaryButton:hover { background-color: #005a9e; }
QPushButton#PrimaryButton:pressed { background-color: #004578; }
"""

DARK_WIREFRAME_STYLE = """
/* Общий фон и шрифт (Тёмная тема) */
QWidget {
    background-color: #1e1e1e;
    color: #dfdfdf;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11pt; 
}

/* Специфичные классы */
QLabel#HeaderLabel {
    font-size: 16pt;
    font-weight: bold;
    color: #4daafc;
    margin-bottom: 10px;
}

/* Строгие рамки для таблиц */
QTableWidget {
    border: 2px solid #555555;
    gridline-color: #444444;
    background-color: #2b2b2b;
    alternate-background-color: #333333;
}
QTableWidget:focus { border: 2px solid #4daafc; }
QHeaderView::section {
    background-color: #333333;
    color: #dfdfdf;
    border: 1px solid #555555;
    font-weight: bold;
    padding: 4px;
}

/* Меню */
QMenuBar { background-color: #2b2b2b; border-bottom: 2px solid #555555; }
QMenuBar::item { padding: 6px 10px; }
QMenuBar::item:selected { background-color: #444444; }
QMenu { background-color: #2b2b2b; border: 2px solid #555555; }
QMenu::item { padding: 6px 40px 6px 20px; }
QMenu::item:selected { background-color: #444444; color: #fff; }

/* Поля ввода */
QLineEdit, QComboBox, QDateEdit, QTextEdit {
    border: 1px solid #555555;
    background-color: #2b2b2b;
    color: #dfdfdf;
    padding: 5px 8px;
    min-height: 24px;
    selection-background-color: #555555;
    selection-color: #ffffff;
}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
    border: 2px solid #4daafc;
    background-color: #333333;
}

/* Кнопки */
QPushButton {
    background-color: #333333;
    color: #dfdfdf;
    border: 1px solid #555555;
    border-radius: 3px;
    padding: 6px 15px;
    font-weight: bold;
    min-height: 24px;
}
QPushButton:hover { background-color: #444444; }
QPushButton:pressed { background-color: #222222; }
QPushButton:focus { border: 2px solid #4daafc; background-color: #3a3a3a; }

/* Главная кнопка */
QPushButton#PrimaryButton {
    background-color: #005a9e;
    color: #ffffff;
    border: 1px solid #004578;
}
QPushButton#PrimaryButton:hover { background-color: #0078d7; }
QPushButton#PrimaryButton:pressed { background-color: #004578; }
"""

CURRENT_THEME = "light"

def apply_theme(app, theme: str = "light"):
    global CURRENT_THEME
    CURRENT_THEME = theme
    if theme == "dark":
        app.setStyleSheet(DARK_WIREFRAME_STYLE)
    else:
        app.setStyleSheet(WIREFRAME_STYLE)