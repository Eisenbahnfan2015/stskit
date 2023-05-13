# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gleisbelegung.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GleisbelegungWindow(object):
    def setupUi(self, GleisbelegungWindow):
        GleisbelegungWindow.setObjectName("GleisbelegungWindow")
        GleisbelegungWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(GleisbelegungWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.settings_page = QtWidgets.QWidget()
        self.settings_page.setObjectName("settings_page")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.settings_page)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gleise_group = QtWidgets.QGroupBox(self.settings_page)
        self.gleise_group.setObjectName("gleise_group")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.gleise_group)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gleise_label = QtWidgets.QLabel(self.gleise_group)
        self.gleise_label.setObjectName("gleise_label")
        self.verticalLayout.addWidget(self.gleise_label)
        self.gleisView = QtWidgets.QTreeView(self.gleise_group)
        self.gleisView.setAlternatingRowColors(True)
        self.gleisView.setObjectName("gleisView")
        self.verticalLayout.addWidget(self.gleisView)
        self.horizontalLayout_2.addWidget(self.gleise_group)
        self.darstellung_group = QtWidgets.QGroupBox(self.settings_page)
        self.darstellung_group.setObjectName("darstellung_group")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.darstellung_group)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.vorlaufzeit_label = QtWidgets.QLabel(self.darstellung_group)
        self.vorlaufzeit_label.setObjectName("vorlaufzeit_label")
        self.verticalLayout_3.addWidget(self.vorlaufzeit_label)
        self.vorlaufzeit_spin = QtWidgets.QSpinBox(self.darstellung_group)
        self.vorlaufzeit_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.vorlaufzeit_spin.setMinimum(15)
        self.vorlaufzeit_spin.setMaximum(120)
        self.vorlaufzeit_spin.setSingleStep(5)
        self.vorlaufzeit_spin.setProperty("value", 55)
        self.vorlaufzeit_spin.setObjectName("vorlaufzeit_spin")
        self.verticalLayout_3.addWidget(self.vorlaufzeit_spin)
        self.nachlaufzeit_label = QtWidgets.QLabel(self.darstellung_group)
        self.nachlaufzeit_label.setObjectName("nachlaufzeit_label")
        self.verticalLayout_3.addWidget(self.nachlaufzeit_label)
        self.nachlaufzeit_spin = QtWidgets.QSpinBox(self.darstellung_group)
        self.nachlaufzeit_spin.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nachlaufzeit_spin.setMinimum(5)
        self.nachlaufzeit_spin.setMaximum(120)
        self.nachlaufzeit_spin.setSingleStep(5)
        self.nachlaufzeit_spin.setProperty("value", 5)
        self.nachlaufzeit_spin.setObjectName("nachlaufzeit_spin")
        self.verticalLayout_3.addWidget(self.nachlaufzeit_spin)
        self.beschriftung_group = QtWidgets.QGroupBox(self.darstellung_group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.beschriftung_group.sizePolicy().hasHeightForWidth())
        self.beschriftung_group.setSizePolicy(sizePolicy)
        self.beschriftung_group.setObjectName("beschriftung_group")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.beschriftung_group)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.name_button = QtWidgets.QRadioButton(self.beschriftung_group)
        self.name_button.setObjectName("name_button")
        self.verticalLayout_2.addWidget(self.name_button)
        self.nummer_button = QtWidgets.QRadioButton(self.beschriftung_group)
        self.nummer_button.setChecked(True)
        self.nummer_button.setObjectName("nummer_button")
        self.verticalLayout_2.addWidget(self.nummer_button)
        self.verticalLayout_3.addWidget(self.beschriftung_group)
        self.darstellung_stretch = QtWidgets.QWidget(self.darstellung_group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.darstellung_stretch.sizePolicy().hasHeightForWidth())
        self.darstellung_stretch.setSizePolicy(sizePolicy)
        self.darstellung_stretch.setObjectName("darstellung_stretch")
        self.verticalLayout_3.addWidget(self.darstellung_stretch)
        self.horizontalLayout_2.addWidget(self.darstellung_group)
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
        self.horizontalLayout_3.addWidget(self.stackedWidget)
        GleisbelegungWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(GleisbelegungWindow)
        self.toolBar.setIconSize(QtCore.QSize(16, 16))
        self.toolBar.setObjectName("toolBar")
        GleisbelegungWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionSetup = QtWidgets.QAction(GleisbelegungWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/equalizer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/equalizer-dis.png"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.actionSetup.setIcon(icon)
        self.actionSetup.setObjectName("actionSetup")
        self.actionAnzeige = QtWidgets.QAction(GleisbelegungWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/slots.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/slots-dis.png"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.actionAnzeige.setIcon(icon1)
        self.actionAnzeige.setObjectName("actionAnzeige")
        self.actionPlusEins = QtWidgets.QAction(GleisbelegungWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/clock--plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPlusEins.setIcon(icon2)
        self.actionPlusEins.setObjectName("actionPlusEins")
        self.actionMinusEins = QtWidgets.QAction(GleisbelegungWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/clock--minus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionMinusEins.setIcon(icon3)
        self.actionMinusEins.setObjectName("actionMinusEins")
        self.actionFix = QtWidgets.QAction(GleisbelegungWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/clock--pencil.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionFix.setIcon(icon4)
        self.actionFix.setObjectName("actionFix")
        self.actionLoeschen = QtWidgets.QAction(GleisbelegungWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/chain--return.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLoeschen.setIcon(icon5)
        self.actionLoeschen.setObjectName("actionLoeschen")
        self.actionAnkunftAbwarten = QtWidgets.QAction(GleisbelegungWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/chain--arrow-in.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAnkunftAbwarten.setIcon(icon6)
        self.actionAnkunftAbwarten.setObjectName("actionAnkunftAbwarten")
        self.actionAbfahrtAbwarten = QtWidgets.QAction(GleisbelegungWindow)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/chain--arrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbfahrtAbwarten.setIcon(icon7)
        self.actionAbfahrtAbwarten.setObjectName("actionAbfahrtAbwarten")
        self.actionWarnungSetzen = QtWidgets.QAction(GleisbelegungWindow)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/flag.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionWarnungSetzen.setIcon(icon8)
        self.actionWarnungSetzen.setObjectName("actionWarnungSetzen")
        self.actionWarnungIgnorieren = QtWidgets.QAction(GleisbelegungWindow)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(":/flag-green.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionWarnungIgnorieren.setIcon(icon9)
        self.actionWarnungIgnorieren.setObjectName("actionWarnungIgnorieren")
        self.actionWarnungReset = QtWidgets.QAction(GleisbelegungWindow)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(":/flag-white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionWarnungReset.setIcon(icon10)
        self.actionWarnungReset.setObjectName("actionWarnungReset")
        self.actionBelegteGleise = QtWidgets.QAction(GleisbelegungWindow)
        self.actionBelegteGleise.setCheckable(True)
        self.actionBelegteGleise.setChecked(False)
        self.actionBelegteGleise.setEnabled(True)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(":/funnel-small.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon11.addPixmap(QtGui.QPixmap(":/funnel-small-dis"), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.actionBelegteGleise.setIcon(icon11)
        self.actionBelegteGleise.setObjectName("actionBelegteGleise")
        self.toolBar.addAction(self.actionSetup)
        self.toolBar.addAction(self.actionAnzeige)
        self.toolBar.addAction(self.actionBelegteGleise)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionWarnungSetzen)
        self.toolBar.addAction(self.actionWarnungIgnorieren)
        self.toolBar.addAction(self.actionWarnungReset)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPlusEins)
        self.toolBar.addAction(self.actionMinusEins)
        self.toolBar.addAction(self.actionFix)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAnkunftAbwarten)
        self.toolBar.addAction(self.actionAbfahrtAbwarten)
        self.toolBar.addAction(self.actionLoeschen)
        self.gleise_label.setBuddy(self.gleisView)
        self.vorlaufzeit_label.setBuddy(self.vorlaufzeit_spin)
        self.nachlaufzeit_label.setBuddy(self.nachlaufzeit_spin)

        self.retranslateUi(GleisbelegungWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(GleisbelegungWindow)

    def retranslateUi(self, GleisbelegungWindow):
        _translate = QtCore.QCoreApplication.translate
        GleisbelegungWindow.setWindowTitle(_translate("GleisbelegungWindow", "MainWindow"))
        self.gleise_group.setTitle(_translate("GleisbelegungWindow", "Gleise"))
        self.gleise_label.setText(_translate("GleisbelegungWindow", "Aus&wahl"))
        self.darstellung_group.setTitle(_translate("GleisbelegungWindow", "Darstellung"))
        self.vorlaufzeit_label.setText(_translate("GleisbelegungWindow", "V&orlaufzeit"))
        self.vorlaufzeit_spin.setSuffix(_translate("GleisbelegungWindow", " Min."))
        self.nachlaufzeit_label.setText(_translate("GleisbelegungWindow", "N&achlaufzeit"))
        self.nachlaufzeit_spin.setSuffix(_translate("GleisbelegungWindow", " Min."))
        self.beschriftung_group.setTitle(_translate("GleisbelegungWindow", "&Beschriftung"))
        self.name_button.setText(_translate("GleisbelegungWindow", "Zugname (Gattung + Nummer)"))
        self.nummer_button.setText(_translate("GleisbelegungWindow", "Zugnummer"))
        self.zuginfoLabel.setText(_translate("GleisbelegungWindow", "Zuginfo: (keine Auswahl)"))
        self.toolBar.setWindowTitle(_translate("GleisbelegungWindow", "toolBar"))
        self.actionSetup.setText(_translate("GleisbelegungWindow", "Setup"))
        self.actionSetup.setToolTip(_translate("GleisbelegungWindow", "Gleisauswahl (S)"))
        self.actionSetup.setShortcut(_translate("GleisbelegungWindow", "S"))
        self.actionAnzeige.setText(_translate("GleisbelegungWindow", "Grafik"))
        self.actionAnzeige.setToolTip(_translate("GleisbelegungWindow", "Grafik anzeigen (G)"))
        self.actionAnzeige.setShortcut(_translate("GleisbelegungWindow", "G"))
        self.actionPlusEins.setText(_translate("GleisbelegungWindow", "+1"))
        self.actionPlusEins.setToolTip(_translate("GleisbelegungWindow", "Feste Verspätung +1 Minute auf ausgewähltem Slot (+)"))
        self.actionPlusEins.setShortcut(_translate("GleisbelegungWindow", "+"))
        self.actionMinusEins.setText(_translate("GleisbelegungWindow", "-1"))
        self.actionMinusEins.setToolTip(_translate("GleisbelegungWindow", "Feste Verspätung -1 Minute auf ausgewähltem Slot (-)"))
        self.actionMinusEins.setShortcut(_translate("GleisbelegungWindow", "-"))
        self.actionFix.setText(_translate("GleisbelegungWindow", "Fix"))
        self.actionFix.setToolTip(_translate("GleisbelegungWindow", "Feste Verspätung auf ausgewähltem Slot festlegen (V)"))
        self.actionFix.setShortcut(_translate("GleisbelegungWindow", "V"))
        self.actionLoeschen.setText(_translate("GleisbelegungWindow", "Löschen"))
        self.actionLoeschen.setToolTip(_translate("GleisbelegungWindow", "Korrekturen auf ausgewähltem Slot löschen (Del)"))
        self.actionLoeschen.setShortcut(_translate("GleisbelegungWindow", "Del"))
        self.actionAnkunftAbwarten.setText(_translate("GleisbelegungWindow", "Ankunft"))
        self.actionAnkunftAbwarten.setToolTip(_translate("GleisbelegungWindow", "Kreuzung/Ankunft von zweitem gewählten Zug abwarten (K)"))
        self.actionAnkunftAbwarten.setShortcut(_translate("GleisbelegungWindow", "K"))
        self.actionAbfahrtAbwarten.setText(_translate("GleisbelegungWindow", "Abfahrt"))
        self.actionAbfahrtAbwarten.setToolTip(_translate("GleisbelegungWindow", "Überholung/Abfahrt von zweitem gewählten Zug abwarten (F)"))
        self.actionAbfahrtAbwarten.setShortcut(_translate("GleisbelegungWindow", "F"))
        self.actionWarnungSetzen.setText(_translate("GleisbelegungWindow", "Warnung"))
        self.actionWarnungSetzen.setToolTip(_translate("GleisbelegungWindow", "Slot-Warnung setzen (W)"))
        self.actionWarnungSetzen.setShortcut(_translate("GleisbelegungWindow", "W"))
        self.actionWarnungIgnorieren.setText(_translate("GleisbelegungWindow", "Ignorieren"))
        self.actionWarnungIgnorieren.setToolTip(_translate("GleisbelegungWindow", "Slot-Warnung ignorieren (I)"))
        self.actionWarnungIgnorieren.setShortcut(_translate("GleisbelegungWindow", "I"))
        self.actionWarnungReset.setText(_translate("GleisbelegungWindow", "Reset"))
        self.actionWarnungReset.setToolTip(_translate("GleisbelegungWindow", "Slot-Warnung zurücksetzen (R)"))
        self.actionWarnungReset.setShortcut(_translate("GleisbelegungWindow", "R"))
        self.actionBelegteGleise.setText(_translate("GleisbelegungWindow", "Belegte Gleise"))
        self.actionBelegteGleise.setToolTip(_translate("GleisbelegungWindow", "Nur belegte Gleise anzeigen (B)"))
        self.actionBelegteGleise.setShortcut(_translate("GleisbelegungWindow", "B"))

