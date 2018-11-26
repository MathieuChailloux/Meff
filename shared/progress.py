# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BioDispersal
                                 A QGIS plugin
 Computes ecological continuities based on environments permeability
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-04-12
        git sha              : $Format:%H$
        copyright            : (C) 2018 by IRSTEA
        email                : mathieu.chailloux@irstea.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import time

from qgis.core import QgsProcessingFeedback

from . import utils
from . import qgsUtils

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal

progressConnector = None
progressFeedback = None

@pyqtSlot(int)
def catchProgress(n):
    utils.debug("Setting progress bar value to '" + str(n) + "'")
    progressConnector.dlg.progressBar.setValue(n)
    
@pyqtSlot()
def catchProgressEnd():
    utils.debug("Progress End")
    progressConnector.dlg.progressBar.setValue(100)
    progressConnector.focusLogTab()

class ProgressConnector(QObject):

    progressSignal = pyqtSignal('int')
    progressEnd = pyqtSignal()

    def __init__(self,dlg):
        self.dlg = dlg
        super(ProgressConnector,self).__init__()
        
    def initGui(self):
        pass
        
    def clear(self):
        self.progressSignal.emit(0)
        
    @pyqtSlot(int)
    def catchProgressVal(self,val):
        self.dlg.progressBar.setValue(val)
        
    def connectComponents(self):
        self.progressSignal.connect(catchProgress)
        self.progressEnd.connect(catchProgressEnd)
        #qgsUtils.progressBarValueChanged.connect(catchClassRemoved)
        
    def focusLogTab(self):
        self.dlg.mTabWidget.setCurrentWidget(self.dlg.logTab)
        self.dlg.txtLog.verticalScrollBar().setValue(self.dlg.txtLog.verticalScrollBar().maximum())
            
class ProgressSection(utils.Section):

    def __init__(self,title,nb_steps):
        super().__init__(title)
        self.curr_step = 0
        if nb_steps <= 0:
            utils.warn("Nothing to do")
        else:
            self.step = 100.0 / nb_steps
        
    def start_section(self):
        super().start_section()
        self.curr_step = 0
        progressConnector.clear()
        
    def next_step(self):
        self.curr_step += self.step
        progressConnector.progressSignal.emit(self.curr_step)
        
    def end_section(self):
        super().end_section()
        progressConnector.progressEnd.emit()
        
class ProgressFeedback(QgsProcessingFeedback):
    
    def __init__(self,dlg):
        self.dlg = dlg
        self.progressBar = dlg.progressBar
        super().__init__()
        
    def pushCommandInfo(self,msg):
        utils.info(msg)
        
    def pushConsoleInfo(self,msg):
        utils.info(msg)
        
    def pushDebugInfo(self,msg):
        utils.debug(msg)
        
    def pushInfo(self,msg):
        utils.info(msg)
        
    def reportError(self,error,fatalError=False):
        utils.internal_error("reportError : " + str(error))
        
    def setProgressText(self,text):
        utils.info("setProgressTest")
        self.dlg.lblProgress.setText(text)
        
    def setProgress(self,value):
        #utils.debug("setProgress " + str(value))
        self.progressBar.setValue(value)
        
    def setPercentage(self,percentage):
        utils.info("setperc")
        #utils.internal_error("percentage : " + str(percentage))
        
    def focusLogTab(self):
        self.dlg.mTabWidget.setCurrentWidget(self.dlg.logTab)
        self.dlg.txtLog.verticalScrollBar().setValue(self.dlg.txtLog.verticalScrollBar().maximum())
        
    def endJob(self):
        self.setProgress(100)
        self.focusLogTab()
        
    def connectComponents(self):
        self.progressChanged.connect(self.setProgress)
    