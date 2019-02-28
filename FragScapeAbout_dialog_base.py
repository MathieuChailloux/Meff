# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'FragScapeAbout_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FragScapeAbout(object):
    def setupUi(self, FragScapeAbout):
        FragScapeAbout.setObjectName("FragScapeAbout")
        FragScapeAbout.resize(707, 524)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FragScapeAbout.sizePolicy().hasHeightForWidth())
        FragScapeAbout.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(FragScapeAbout)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(FragScapeAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMaximumSize(QtCore.QSize(68, 68))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/plugins/FragScape/icons/logoIrstea.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(FragScapeAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMaximumSize(QtCore.QSize(136, 68))
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap(":/plugins/FragScape/icons/logoTetis.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(FragScapeAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setMaximumSize(QtCore.QSize(105, 68))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap(":/plugins/FragScape/icons/logoCRTVB.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(FragScapeAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setMaximumSize(QtCore.QSize(53, 68))
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/plugins/FragScape/icons/logoMTES.png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 3, 1, 1)
        self.label = QtWidgets.QLabel(FragScapeAbout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 4)

        self.retranslateUi(FragScapeAbout)
        QtCore.QMetaObject.connectSlotsByName(FragScapeAbout)

    def retranslateUi(self, FragScapeAbout):
        _translate = QtCore.QCoreApplication.translate
        FragScapeAbout.setWindowTitle(_translate("FragScapeAbout", "FragScape - About"))
        self.label.setText(_translate("FragScapeAbout", "<html><head/><body><p><br/></p><p>FragScape is a QGIS 3 plugin (GNU GPLv3 licence) computing fragmentation metrics  such as effective mesh size (Jaeger, 2000; Moser and al., 2007). It defines a 4 step procedure from raw data to reporting layer with metrics.</p><p>FragScape has been developped by research unit UMR TETIS in 2019. This project has been funded by French ministry of ecology for the ecological network resource center.</p><p><span style=\" font-style:italic;\">Designer / Developper</span> : Mathieu Chailloux (IRSTEA / TETIS)</p><p><span style=\" font-style:italic;\">Project initiator</span> s: Jennifer Amsallem (IRSTEA / TETIS), Jean-Pierre Chéry (AgroParisTech /  TETIS)</p><p><span style=\" font-style:italic;\">Links</span> :</p><p>- FragScape homepage : <a href=\"http://www.umr-tetis.fr/index.php/fr/production/donnees-et-plateformes/plateformes/426-fragscape\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.umr-tetis.fr/index.php/fr/production/donnees-et-plateformes/plateformes/426-fragscape</span></a></p><p>- FragScape Github repository : <a href=\"https://github.com/MathieuChailloux/FragScape\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/MathieuChailloux/FragScape</span></a></p><p>- FragScape bug tracker : <a href=\"https://github.com/MathieuChailloux/FragScape/issues\"><span style=\" text-decoration: underline; color:#0000ff;\">https://github.com/MathieuChailloux/FragScape/issues</span></a></p><p>- French ecological network resource center : <a href=\"http://www.trameverteetbleue.fr/\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.trameverteetbleue.fr/</span></a></p><p>- UMR TETIS research unit website : <a href=\"http://www.umr-tetis.fr/index.php/fr/\"><span style=\" text-decoration: underline; color:#0000ff;\">http://www.umr-tetis.fr/index.php/fr/</span></a><br/></p></body></html>"))

