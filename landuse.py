# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Meff
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

from qgis.core import QgsMapLayerProxyModel
from PyQt5 import QtGui, QtCore, QtWidgets
from .shared import utils, abstract_model, qgsUtils, progress, qgsTreatments
from . import params

landuseModel = None

# Code snippet from https://stackoverflow.com/questions/17748546/pyqt-column-of-checkboxes-in-a-qtableview
class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        '''
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''

        checked = bool(index.data())
        check_box_style_option = QtWidgets.QStyleOptionButton()

        #if (index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        if (index.flags() & QtCore.Qt.ItemIsEditable):
            check_box_style_option.state |= QtWidgets.QStyle.State_Enabled
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        if checked:
            check_box_style_option.state |= QtWidgets.QStyle.State_On
        else:
            check_box_style_option.state |= QtWidgets.QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)

        # this will not run - hasFlag does not exist
        #if not index.model().hasFlag(index, QtCore.Qt.ItemIsEditable):
            #check_box_style_option.state |= QtWidgets.QStyle.State_ReadOnly

        check_box_style_option.state |= QtWidgets.QStyle.State_Enabled

        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.CE_CheckBox, check_box_style_option, painter)

    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
        utils.debug('Check Box editor Event detected : ')
        utils.debug(str(event.type()))
        #if not (index.flags() & QtCore.Qt.ItemIsEditable) > 0:
        if not (index.flags() & QtCore.Qt.ItemIsEditable):
            return False

        utils.debug('Check Box editor Event detected : passed first check')
        # Do not change the checkbox-state
        if event.type() == QtCore.QEvent.MouseButtonPress:
          return False
        if event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() != QtCore.Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() != QtCore.Qt.Key_Space and event.key() != QtCore.Qt.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True

    def setModelData (self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
        utils.debug('SetModelData')
        newValue = not bool(index.data())
        utils.debug('New Value : {0}'.format(newValue))
        model.setData(index, newValue, QtCore.Qt.EditRole)

    def getCheckBoxRect(self, option):
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (option.rect.x() +
                            option.rect.width() / 2 -
                            check_box_rect.width() / 2,
                            option.rect.y() +
                            option.rect.height() / 2 -
                            check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())


class LanduseFieldItem(abstract_model.DictItem):

    def __init__(self,val,isNatural=False):
        dict = {"value" : val, "isNatural" : isNatural}
        super().__init__(dict)
        
        
class LanduseModel(abstract_model.DictModel):

    def __init__(self):
        self.parser_name = "Landuse"
        self.landuseLayer = None
        self.landuseField = None
        fields = ["value","isNatural"]
        self.dataClipFlag = True
        super().__init__(self,fields)
                        
    def mkItemFromDict(self,dict):
        utils.debug("dict : " + str(dict))
        v = dict["value"]
        i = (dict["isNatural"] == "True")
        return LanduseFieldItem(v,i)
        
    def checkLayerSelected(self):
        if not self.landuseLayer:
            utils.user_error("No layer selected")
            
    def checkFieldSelected(self):
        if not self.landuseField:
            utils.user_error("No field selected")
            
    def getClipLayer(self):
        return params.mkOutputFile("landuseClip.gpkg")
            
    def getSelectionLayer(self):
        return params.mkOutputFile("landuseSelection.gpkg")
            
    def getDissolveLayer(self):
        return params.mkOutputFile("landuseSelectionDissolve.gpkg")
        
    def switchDataClipFlag(self,state):
        utils.debug("switchDataClipFlag")
        self.dataClipFlag = not self.dataClipFlag

    def mkSelectionExpr(self):
        expr = ""
        for item in self.items:
            if item.dict["isNatural"]:
                if expr != "":
                    expr += " + "
                field_val = item.dict["value"].replace("'","''")
                expr += "(\"" + self.landuseField + "\" = '" + field_val + "')"
        utils.debug("selectionExpr = " + expr)
        return expr
        
    def applyItems(self):
        progress.progressFeedback.beginSection("Landuse classification")
        params.checkWorkspaceInit()
        self.checkLayerSelected()
        self.checkFieldSelected()
        in_layer = qgsUtils.pathOfLayer(self.landuseLayer)
        territory_layer = params.getTerritoryLayer()
        expr = self.mkSelectionExpr()
        if not expr:
            utils.user_error("No expression selected : TODO select everything")
        selectionResLayer = self.getSelectionLayer()
        dissolveLayer = self.getDissolveLayer()
        if self.dataClipFlag:
            utils.debug("dataClipFlag activated")
            clip_layer = self.getClipLayer()
            qgsTreatments.applyVectorClip(in_layer,territory_layer,clip_layer)
            extractSourceLayer = clip_layer
        else:
            extractSourceLayer = in_layer
        qgsTreatments.extractByExpression(extractSourceLayer,expr,selectionResLayer)
        dissolved = qgsTreatments.dissolveLayer(selectionResLayer,dissolveLayer)
        qgsUtils.loadLayer(dissolved,loadProject=True)
        progress.progressFeedback.endSection()
        
    def toXML(self,indent=" "):
        if not self.landuseLayer:
            utils.warn("No layer selected")
            return ""
        if not self.landuseField:
            utils.warn("No field selected")
            return ""
        layerRelPath = params.normalizePath(qgsUtils.pathOfLayer(self.landuseLayer))
        modelParams = { "layer" : layerRelPath, "field" : self.landuseField }
        xmlStr = super().toXML(indent,modelParams)
        return xmlStr

        
class LanduseConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg):
        self.dlg = dlg
        self.parser_name = "Landuse"
        self.dlg.landuseView.setItemDelegateForColumn(1,CheckBoxDelegate(self.dlg.landuseView))
        landuse_model = LanduseModel()
        super().__init__(landuse_model,self.dlg.landuseView)
        
    def initGui(self):
        self.dlg.landuseLayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.landuseLayer.setFilter(qgsUtils.getVectorFilters())
        
    def connectComponents(self):
        super().connectComponents()
        self.dlg.landuseLayerCombo.layerChanged.connect(self.setLayer)
        self.dlg.landuseLayer.fileChanged.connect(self.loadLayer)
        self.dlg.landuseFieldCombo.fieldChanged.connect(self.loadField)
        self.dlg.landuseRun.clicked.connect(self.model.applyItems)
        self.dlg.dataClipFlag.stateChanged.connect(self.model.switchDataClipFlag)
        
    def setLayer(self,layer):
        utils.debug("setLayer " + str(layer.type))
        self.dlg.landuseFieldCombo.setLayer(layer)
        self.model.landuseLayer = layer
  
    def loadLayer(self,path):
        utils.debug("loadLayer")
        loaded_layer = qgsUtils.loadVectorLayer(path,loadProject=True)
        self.setLayer(loaded_layer)
        self.dlg.landuseLayerCombo.setLayer(loaded_layer)
        
    def loadField(self,fieldname):
        utils.debug("loadField")
        curr_layer = self.dlg.landuseLayerCombo.currentLayer()
        if not curr_layer:
            utils.internal_error("No layer selected in landuse tab")
        fieldVals = qgsUtils.getLayerFieldUniqueValues(curr_layer,fieldname)
        self.model.items = []
        for fieldVal in fieldVals:
            utils.debug("fieldVal : " + str(fieldVal))
            item = LanduseFieldItem(fieldVal,False)
            self.model.addItem(item)
        self.model.landuseField = fieldname
        self.model.layoutChanged.emit()
        

    def fromXMLAttribs(self,attribs):
        attrib_fields = ["layer", "field"]
        utils.checkFields(attrib_fields,attribs.keys())
        abs_layer = params.getOrigPath(attribs["layer"])
        self.loadLayer(abs_layer)
        self.dlg.landuseFieldCombo.setField(attribs["field"])
        
    def fromXMLRoot(self,root):
        self.fromXMLAttribs(root.attrib)
        self.model.items = []
        for parsed_item in root:
            dict = parsed_item.attrib
            item = self.model.mkItemFromDict(dict)
            self.model.addItem(item)
        self.model.layoutChanged.emit()
        
    def toXML(self):
        return self.model.toXML()
    