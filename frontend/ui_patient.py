# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'patient.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDateEdit,
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(409, 200)
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(230, 150, 171, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 70, 391, 28))
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.address_label = QLabel(self.widget)
        self.address_label.setObjectName(u"address_label")

        self.horizontalLayout_3.addWidget(self.address_label)

        self.address = QLineEdit(self.widget)
        self.address.setObjectName(u"address")

        self.horizontalLayout_3.addWidget(self.address)

        self.widget1 = QWidget(Dialog)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(10, 110, 391, 31))
        self.horizontalLayout_7 = QHBoxLayout(self.widget1)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.passport_label = QLabel(self.widget1)
        self.passport_label.setObjectName(u"passport_label")

        self.horizontalLayout_4.addWidget(self.passport_label)

        self.passport = QLineEdit(self.widget1)
        self.passport.setObjectName(u"passport")

        self.horizontalLayout_4.addWidget(self.passport)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.gender_label = QLabel(self.widget1)
        self.gender_label.setObjectName(u"gender_label")

        self.horizontalLayout_5.addWidget(self.gender_label)

        self.gender = QComboBox(self.widget1)
        self.gender.addItem("")
        self.gender.addItem("")
        self.gender.setObjectName(u"gender")

        self.horizontalLayout_5.addWidget(self.gender)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.birth_date_label = QLabel(self.widget1)
        self.birth_date_label.setObjectName(u"birth_date_label")

        self.horizontalLayout_6.addWidget(self.birth_date_label)

        self.birth_date = QDateEdit(self.widget1)
        self.birth_date.setObjectName(u"birth_date")

        self.horizontalLayout_6.addWidget(self.birth_date)


        self.horizontalLayout_7.addLayout(self.horizontalLayout_6)

        self.widget2 = QWidget(Dialog)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setGeometry(QRect(10, 150, 158, 28))
        self.horizontalLayout_8 = QHBoxLayout(self.widget2)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.phone_label = QLabel(self.widget2)
        self.phone_label.setObjectName(u"phone_label")

        self.horizontalLayout_8.addWidget(self.phone_label)

        self.phone = QLineEdit(self.widget2)
        self.phone.setObjectName(u"phone")

        self.horizontalLayout_8.addWidget(self.phone)

        self.widget3 = QWidget(Dialog)
        self.widget3.setObjectName(u"widget3")
        self.widget3.setGeometry(QRect(100, 30, 301, 28))
        self.horizontalLayout = QHBoxLayout(self.widget3)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.full_name_label = QLabel(self.widget3)
        self.full_name_label.setObjectName(u"full_name_label")

        self.horizontalLayout.addWidget(self.full_name_label)

        self.full_name = QLineEdit(self.widget3)
        self.full_name.setObjectName(u"full_name")
        self.full_name.setTabletTracking(False)

        self.horizontalLayout.addWidget(self.full_name)

        self.widget4 = QWidget(Dialog)
        self.widget4.setObjectName(u"widget4")
        self.widget4.setGeometry(QRect(11, 31, 71, 28))
        self.horizontalLayout_2 = QHBoxLayout(self.widget4)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.id_label = QLabel(self.widget4)
        self.id_label.setObjectName(u"id_label")

        self.horizontalLayout_2.addWidget(self.id_label)

        self.id = QLineEdit(self.widget4)
        self.id.setObjectName(u"id")

        self.horizontalLayout_2.addWidget(self.id)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f \u043f\u0430\u0446\u0438\u0435\u043d\u0442\u0430", None))
        self.address_label.setText(QCoreApplication.translate("Dialog", u"\u0410\u0434\u0440\u0435\u0441", None))
        self.passport_label.setText(QCoreApplication.translate("Dialog", u"\u2116 \u043f\u0430\u0441\u043f\u043e\u0440\u0442\u0430", None))
        self.passport.setText("")
        self.gender_label.setText(QCoreApplication.translate("Dialog", u"\u041f\u043e\u043b", None))
        self.gender.setItemText(0, QCoreApplication.translate("Dialog", u"\u0416", None))
        self.gender.setItemText(1, QCoreApplication.translate("Dialog", u"\u041c", None))

        self.birth_date_label.setText(QCoreApplication.translate("Dialog", u"\u0414/\u0420", None))
        self.phone_label.setText(QCoreApplication.translate("Dialog", u"\u0422\u0435\u043b.", None))
        self.phone.setText(QCoreApplication.translate("Dialog", u"375447649873", None))
        self.full_name_label.setText(QCoreApplication.translate("Dialog", u"\u0424.\u0418.\u041e.", None))
        self.id_label.setText(QCoreApplication.translate("Dialog", u"\u2116", None))
    # retranslateUi

