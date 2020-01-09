# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Client_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Server(object):
    def setupUi(self, Server):
        Server.setObjectName("Server")
        Server.resize(800, 600)
        Server.setStyleSheet("font: 57 9pt \"Source Code Pro Medium\";\n"
"background-color: rgb(200, 162, 165);")
        self.centralwidget = QtWidgets.QWidget(Server)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 171, 31))
        font = QtGui.QFont()
        font.setFamily("Source Code Pro Medium")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(7)
        self.label.setFont(font)
        self.label.setStyleSheet("font: 57 14pt \"Source Code Pro Medium\";")
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(110, 430, 101, 31))
        self.pushButton.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(46, 175, 255);")
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(30, 370, 271, 41))
        self.lineEdit.setObjectName("lineEdit")
        self.formLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(10, 60, 321, 201))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label_2.setAutoFillBackground(False)
        self.label_2.setStyleSheet("font: 11pt \"微软雅黑\";")
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 310, 211, 31))
        self.label_3.setObjectName("label_3")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(400, 120, 351, 391))
        self.textEdit.setObjectName("textEdit")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(560, 40, 51, 51))
        self.label_4.setBaseSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setFamily("Source Code Pro")
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setStyleSheet("font: 14pt \"Source Code Pro\";")
        self.label_4.setObjectName("label_4")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(360, 0, 20, 561))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        Server.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Server)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        Server.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Server)
        self.statusbar.setObjectName("statusbar")
        Server.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(Server)
        self.toolBar.setObjectName("toolBar")
        Server.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        self.retranslateUi(Server)
        QtCore.QMetaObject.connectSlotsByName(Server)

    def retranslateUi(self, Server):
        _translate = QtCore.QCoreApplication.translate
        Server.setWindowTitle(_translate("Server", "客户端界面"))
        self.label.setText(_translate("Server", "Made By Wzy"))
        self.pushButton.setText(_translate("Server", "执行命令"))
        self.label_2.setText(_translate("Server", "可用命令：\n"
"auctions\n"
"list auctionname\n"
"join auctionname\n"
"bid price\n"
"leave\n"
"quit"))
        self.label_3.setText(_translate("Server", "在输入框中输入命令："))
        self.label_4.setText(_translate("Server", "结果"))
        self.toolBar.setWindowTitle(_translate("Server", "toolBar"))
