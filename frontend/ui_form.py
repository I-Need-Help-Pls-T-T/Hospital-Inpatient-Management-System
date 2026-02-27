# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenu, QMenuBar,
    QSizePolicy, QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.action = QAction(MainWindow)
        self.action.setObjectName(u"action")
        self.action_help = QAction(MainWindow)
        self.action_help.setObjectName(u"action_help")
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        self.action_position = QAction(MainWindow)
        self.action_position.setObjectName(u"action_position")
        self.action_department = QAction(MainWindow)
        self.action_department.setObjectName(u"action_department")
        self.action_room = QAction(MainWindow)
        self.action_room.setObjectName(u"action_room")
        self.action_ward = QAction(MainWindow)
        self.action_ward.setObjectName(u"action_ward")
        self.action_staff_role = QAction(MainWindow)
        self.action_staff_role.setObjectName(u"action_staff_role")
        self.action_patient = QAction(MainWindow)
        self.action_patient.setObjectName(u"action_patient")
        self.action_staff = QAction(MainWindow)
        self.action_staff.setObjectName(u"action_staff")
        self.action_hospitalization = QAction(MainWindow)
        self.action_hospitalization.setObjectName(u"action_hospitalization")
        self.action_med_entry = QAction(MainWindow)
        self.action_med_entry.setObjectName(u"action_med_entry")
        self.action_medication_order = QAction(MainWindow)
        self.action_medication_order.setObjectName(u"action_medication_order")
        self.action_payment = QAction(MainWindow)
        self.action_payment.setObjectName(u"action_payment")
        self.action_patient_admission = QAction(MainWindow)
        self.action_patient_admission.setObjectName(u"action_patient_admission")
        self.action_admission_team = QAction(MainWindow)
        self.action_admission_team.setObjectName(u"action_admission_team")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 17))
        self.menu_file = QMenu(self.menubar)
        self.menu_file.setObjectName(u"menu_file")
        self.menu_directory = QMenu(self.menubar)
        self.menu_directory.setObjectName(u"menu_directory")
        self.menu_main = QMenu(self.menubar)
        self.menu_main.setObjectName(u"menu_main")
        self.menu_help = QMenu(self.menubar)
        self.menu_help.setObjectName(u"menu_help")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menu_file.menuAction())
        self.menubar.addAction(self.menu_directory.menuAction())
        self.menubar.addAction(self.menu_main.menuAction())
        self.menubar.addAction(self.menu_help.menuAction())
        self.menu_file.addAction(self.action_exit)
        self.menu_directory.addAction(self.action_position)
        self.menu_directory.addAction(self.action_department)
        self.menu_directory.addAction(self.action_room)
        self.menu_directory.addAction(self.action_ward)
        self.menu_directory.addAction(self.action_staff_role)
        self.menu_main.addAction(self.action_patient)
        self.menu_main.addAction(self.action_staff)
        self.menu_main.addAction(self.action_hospitalization)
        self.menu_main.addAction(self.action_med_entry)
        self.menu_main.addAction(self.action_medication_order)
        self.menu_main.addAction(self.action_payment)
        self.menu_main.addAction(self.action_patient_admission)
        self.menu_main.addAction(self.action_admission_team)
        self.menu_help.addAction(self.action_help)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.action.setText(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u0439\u043b", None))
        self.action_help.setText(QCoreApplication.translate("MainWindow", u"\u041e \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0435", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"\u0412\u044b\u0445\u043e\u0434", None))
        self.action_position.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u0438", None))
        self.action_department.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0442\u0434\u0435\u043b\u0435\u043d\u0438\u044f", None))
        self.action_room.setText(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043c\u0435\u0449\u0435\u043d\u0438\u044f", None))
        self.action_ward.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0430\u043b\u0430\u0442\u044b", None))
        self.action_staff_role.setText(QCoreApplication.translate("MainWindow", u"\u0414\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u0438 \u043f\u0435\u0440\u043e\u043d\u0430\u043b\u0430", None))
        self.action_patient.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0430\u0446\u0438\u0435\u043d\u0442\u044b", None))
        self.action_staff.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0435\u0440\u0441\u043e\u043d\u0430\u043b", None))
        self.action_hospitalization.setText(QCoreApplication.translate("MainWindow", u"\u0413\u043e\u0441\u043f\u0438\u0442\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u044f", None))
        self.action_med_entry.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043f\u0438\u0441\u044c \u0432 \u0438\u0441\u0442\u043e\u0440\u0438\u0438 \u0431\u043e\u043b\u0435\u0437\u043d\u0438", None))
        self.action_medication_order.setText(QCoreApplication.translate("MainWindow", u"\u041b\u0438\u0441\u0442 \u043d\u0430\u0437\u043d\u0430\u0447\u0435\u043d\u0438\u044f", None))
        self.action_payment.setText(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u043b\u0430\u0442\u0430", None))
        self.action_patient_admission.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0440\u0438\u0435\u043c \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u043e\u0432", None))
        self.action_admission_team.setText(QCoreApplication.translate("MainWindow", u"\u0414\u0435\u0436\u0443\u0440\u043d\u0430\u044f \u0431\u0440\u0438\u0433\u0430\u0434\u0430", None))
        self.menu_file.setTitle(QCoreApplication.translate("MainWindow", u"\u0424\u0430\u0439\u043b", None))
        self.menu_directory.setTitle(QCoreApplication.translate("MainWindow", u"\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u0438", None))
        self.menu_main.setTitle(QCoreApplication.translate("MainWindow", u"\u0412\u0432\u043e\u0434", None))
        self.menu_help.setTitle(QCoreApplication.translate("MainWindow", u"\u041f\u043e\u043c\u043e\u0449\u044c", None))
    # retranslateUi

