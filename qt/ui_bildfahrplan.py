# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bildfahrplan.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BildfahrplanWindow(object):
    def setupUi(self, BildfahrplanWindow):
        BildfahrplanWindow.setObjectName("BildfahrplanWindow")
        BildfahrplanWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(BildfahrplanWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.settings_page = QtWidgets.QWidget()
        self.settings_page.setObjectName("settings_page")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.settings_page)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.settings_layout = QtWidgets.QVBoxLayout()
        self.settings_layout.setObjectName("settings_layout")
        self.vordefiniert_label = QtWidgets.QLabel(self.settings_page)
        self.vordefiniert_label.setObjectName("vordefiniert_label")
        self.settings_layout.addWidget(self.vordefiniert_label)
        self.vordefiniert_combo = QtWidgets.QComboBox(self.settings_page)
        self.vordefiniert_combo.setObjectName("vordefiniert_combo")
        self.settings_layout.addWidget(self.vordefiniert_combo)
        self.von_label = QtWidgets.QLabel(self.settings_page)
        self.von_label.setObjectName("von_label")
        self.settings_layout.addWidget(self.von_label)
        self.von_combo = QtWidgets.QComboBox(self.settings_page)
        self.von_combo.setObjectName("von_combo")
        self.settings_layout.addWidget(self.von_combo)
        self.via_label = QtWidgets.QLabel(self.settings_page)
        self.via_label.setObjectName("via_label")
        self.settings_layout.addWidget(self.via_label)
        self.via_combo = QtWidgets.QComboBox(self.settings_page)
        self.via_combo.setObjectName("via_combo")
        self.settings_layout.addWidget(self.via_combo)
        self.nach_label = QtWidgets.QLabel(self.settings_page)
        self.nach_label.setObjectName("nach_label")
        self.settings_layout.addWidget(self.nach_label)
        self.nach_combo = QtWidgets.QComboBox(self.settings_page)
        self.nach_combo.setObjectName("nach_combo")
        self.settings_layout.addWidget(self.nach_combo)
        self.strecke_label = QtWidgets.QLabel(self.settings_page)
        self.strecke_label.setObjectName("strecke_label")
        self.settings_layout.addWidget(self.strecke_label)
        self.strecke_list = QtWidgets.QListWidget(self.settings_page)
        self.strecke_list.setObjectName("strecke_list")
        self.settings_layout.addWidget(self.strecke_list)
        self.display_button = QtWidgets.QToolButton(self.settings_page)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.display_button.sizePolicy().hasHeightForWidth())
        self.display_button.setSizePolicy(sizePolicy)
        self.display_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.display_button.setObjectName("display_button")
        self.settings_layout.addWidget(self.display_button)
        self.horizontalLayout_2.addLayout(self.settings_layout)
        self.stackedWidget.addWidget(self.settings_page)
        self.display_page = QtWidgets.QWidget()
        self.display_page.setObjectName("display_page")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.display_page)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.displaySplitter = QtWidgets.QSplitter(self.display_page)
        self.displaySplitter.setOrientation(QtCore.Qt.Vertical)
        self.displaySplitter.setObjectName("displaySplitter")
        self.grafikWidget = QtWidgets.QWidget(self.displaySplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grafikWidget.sizePolicy().hasHeightForWidth())
        self.grafikWidget.setSizePolicy(sizePolicy)
        self.grafikWidget.setObjectName("grafikWidget")
        self.zuginfoLabel = QtWidgets.QLabel(self.displaySplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.zuginfoLabel.sizePolicy().hasHeightForWidth())
        self.zuginfoLabel.setSizePolicy(sizePolicy)
        self.zuginfoLabel.setMaximumSize(QtCore.QSize(16777215, 50))
        self.zuginfoLabel.setBaseSize(QtCore.QSize(0, 0))
        self.zuginfoLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.zuginfoLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.zuginfoLabel.setTextFormat(QtCore.Qt.AutoText)
        self.zuginfoLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.zuginfoLabel.setObjectName("zuginfoLabel")
        self.horizontalLayout.addWidget(self.displaySplitter)
        self.stackedWidget.addWidget(self.display_page)
        self.verticalLayout.addWidget(self.stackedWidget)
        BildfahrplanWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(BildfahrplanWindow)
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QtCore.QSize(16, 16))
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        BildfahrplanWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSetup = QtWidgets.QAction(BildfahrplanWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/equalizer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSetup.setIcon(icon)
        self.actionSetup.setObjectName("actionSetup")
        self.actionAnzeige = QtWidgets.QAction(BildfahrplanWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/chart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAnzeige.setIcon(icon1)
        self.actionAnzeige.setObjectName("actionAnzeige")
        self.actionPlusEins = QtWidgets.QAction(BildfahrplanWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/hourglass--plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPlusEins.setIcon(icon2)
        self.actionPlusEins.setObjectName("actionPlusEins")
        self.actionMinusEins = QtWidgets.QAction(BildfahrplanWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/hourglass--minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMinusEins.setIcon(icon3)
        self.actionMinusEins.setObjectName("actionMinusEins")
        self.actionFix = QtWidgets.QAction(BildfahrplanWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/hourglass--pencil.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFix.setIcon(icon4)
        self.actionFix.setObjectName("actionFix")
        self.actionLoeschen = QtWidgets.QAction(BildfahrplanWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/eraser.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoeschen.setIcon(icon5)
        self.actionLoeschen.setObjectName("actionLoeschen")
        self.actionAnkunftAbwarten = QtWidgets.QAction(BildfahrplanWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/train.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAnkunftAbwarten.setIcon(icon6)
        self.actionAnkunftAbwarten.setObjectName("actionAnkunftAbwarten")
        self.actionAbfahrtAbwarten = QtWidgets.QAction(BildfahrplanWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/train--arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbfahrtAbwarten.setIcon(icon7)
        self.actionAbfahrtAbwarten.setObjectName("actionAbfahrtAbwarten")
        self.toolBar.addAction(self.actionSetup)
        self.toolBar.addAction(self.actionAnzeige)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAnkunftAbwarten)
        self.toolBar.addAction(self.actionAbfahrtAbwarten)
        self.toolBar.addAction(self.actionPlusEins)
        self.toolBar.addAction(self.actionMinusEins)
        self.toolBar.addAction(self.actionFix)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionLoeschen)
        self.vordefiniert_label.setBuddy(self.vordefiniert_combo)
        self.von_label.setBuddy(self.von_combo)
        self.via_label.setBuddy(self.via_combo)
        self.nach_label.setBuddy(self.nach_combo)
        self.strecke_label.setBuddy(self.strecke_list)

        self.retranslateUi(BildfahrplanWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(BildfahrplanWindow)

    def retranslateUi(self, BildfahrplanWindow):
        _translate = QtCore.QCoreApplication.translate
        BildfahrplanWindow.setWindowTitle(_translate("BildfahrplanWindow", "Bildfahrplan"))
        self.vordefiniert_label.setText(_translate("BildfahrplanWindow", "Vordefinierte &Strecke"))
        self.von_label.setText(_translate("BildfahrplanWindow", "&Von"))
        self.via_label.setText(_translate("BildfahrplanWindow", "V&ia"))
        self.nach_label.setText(_translate("BildfahrplanWindow", "&Nach"))
        self.strecke_label.setText(_translate("BildfahrplanWindow", "S&trecke"))
        self.display_button.setText(_translate("BildfahrplanWindow", "Anzeigen"))
        self.zuginfoLabel.setText(_translate("BildfahrplanWindow", "Zuginfo: (keine Auswahl)"))
        self.toolBar.setWindowTitle(_translate("BildfahrplanWindow", "Tool Bar"))
        self.actionSetup.setText(_translate("BildfahrplanWindow", "Setup"))
        self.actionSetup.setToolTip(_translate("BildfahrplanWindow", "Streckendefinition (S)"))
        self.actionSetup.setShortcut(_translate("BildfahrplanWindow", "S"))
        self.actionAnzeige.setText(_translate("BildfahrplanWindow", "Grafik"))
        self.actionAnzeige.setToolTip(_translate("BildfahrplanWindow", "Grafik anzeigen (G)"))
        self.actionAnzeige.setShortcut(_translate("BildfahrplanWindow", "G"))
        self.actionPlusEins.setText(_translate("BildfahrplanWindow", "+1"))
        self.actionPlusEins.setToolTip(_translate("BildfahrplanWindow", "Feste Verspätung +1 Minute auf ausgewähltem Segment (+)"))
        self.actionPlusEins.setShortcut(_translate("BildfahrplanWindow", "+"))
        self.actionMinusEins.setText(_translate("BildfahrplanWindow", "-1"))
        self.actionMinusEins.setToolTip(_translate("BildfahrplanWindow", "Feste Verspätung -1 Minute auf ausgewähltem Segment (-)"))
        self.actionMinusEins.setShortcut(_translate("BildfahrplanWindow", "-"))
        self.actionFix.setText(_translate("BildfahrplanWindow", "Fix"))
        self.actionFix.setToolTip(_translate("BildfahrplanWindow", "Feste Verspätung auf ausgewähltem Segment festlegen (V)"))
        self.actionFix.setShortcut(_translate("BildfahrplanWindow", "V"))
        self.actionLoeschen.setText(_translate("BildfahrplanWindow", "Löschen"))
        self.actionLoeschen.setToolTip(_translate("BildfahrplanWindow", "Korrekturen auf ausgewähltem Segment löschen (Del)"))
        self.actionLoeschen.setShortcut(_translate("BildfahrplanWindow", "Del"))
        self.actionAnkunftAbwarten.setText(_translate("BildfahrplanWindow", "Ankunft"))
        self.actionAnkunftAbwarten.setToolTip(_translate("BildfahrplanWindow", "Kreuzung/Ankunft von zweitem gewählten Zug abwarten (K)"))
        self.actionAnkunftAbwarten.setShortcut(_translate("BildfahrplanWindow", "K"))
        self.actionAbfahrtAbwarten.setText(_translate("BildfahrplanWindow", "Abfahrt"))
        self.actionAbfahrtAbwarten.setToolTip(_translate("BildfahrplanWindow", "Überholung/Abfahrt von zweitem gewählten Zug abwarten (F)"))
        self.actionAbfahrtAbwarten.setShortcut(_translate("BildfahrplanWindow", "F"))

