# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MeffDialog
                                 A QGIS plugin
 This plugin computes mesh effective size
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2018-11-05
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Mathieu Chailloux
        email                : mathieu@chailloux.org
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

import os.path
import time

from qgis.core import QgsProject, QgsMapLayerProxyModel, QgsVectorLayer, QgsProcessingFeedback
import processing
from processing import QgsProcessingUtils

from ..shared import utils, abstract_model, qgsUtils, qgsTreatments, progress
from ..algs import meff_algs
from . import params, landuse



fragmModel = None

class FragmItem(abstract_model.DictItem):

    NAME_FIELD = "NAME"

    def __init__(self,dict):
        super().__init__(dict,fields=FragmModel.FIELDS)
        self.selectionLayer = None
        self.bufferLayer = None

    # def __init__(self,in_layer,expr,buffer,name):
        # dict = {"in_layer" : in_layer,
                # "expr" : expr,
                # "buffer" : buffer,
                # "name" : name}
        # super().__init__(dict)
        # self.selectionLayer = None
        # self.bufferLayer = None
        
    def applyItem(self):
        pass
        
    def equals(self,other):
        return (self.dict[self.NAME_FIELD] == other.dict[self.NAME_FIELD])
        
    def getSelectionLayer(self):
        if not self.selectionLayer:
            name = self.dict[self.NAME_FIELD]
            self.selectionLayer = QgsProcessingUtils.generateTempFilename(name + ".gpkg")
        return self.selectionLayer
       
    def getBufferLayer(self):
        if not self.bufferLayer:
            name = self.dict[self.NAME_FIELD]
            self.bufferLayer = QgsProcessingUtils.generateTempFilename(name + "_buf.gpkg")
        return self.bufferLayer
        
    # def instantiateSelectionLayer(self):
        # out_path = self.getSelectionLayer()
        # qgsUtils.removeVectorLayer(out_path)
        # in_layer_path = self.dict["in_layer"]
        # in_layer = qgsUtils.loadVectorLayer(in_layer_path)
        # selection_layer = qgsUtils.createLayerFromExisting(in_layer,self.dict["name"])
        # return selection_layer
        
class FragmModel(abstract_model.DictModel):

    PREPARE_INPUT = meff_algs.PrepareFragmentationAlgorithm.INPUT
    PREPARE_CLIP_LAYER = meff_algs.PrepareFragmentationAlgorithm.CLIP_LAYER
    PREPARE_SELECT_EXPR = meff_algs.PrepareFragmentationAlgorithm.SELECT_EXPR
    PREPARE_BUFFER = meff_algs.PrepareFragmentationAlgorithm.BUFFER
    PREPARE_NAME = FragmItem.NAME_FIELD
    PREPARE_OUTPUT = meff_algs.PrepareFragmentationAlgorithm.OUTPUT
    
    FIELDS = [PREPARE_INPUT,PREPARE_CLIP_LAYER,PREPARE_SELECT_EXPR,PREPARE_BUFFER,PREPARE_NAME]
    
    APPLY_LANDUSE = meff_algs.ApplyFragmentationAlgorithm.LANDUSE
    APPLY_FRAGMENTATION = meff_algs.ApplyFragmentationAlgorithm.FRAGMENTATION
    APPLY_CRS = meff_algs.ApplyFragmentationAlgorithm.CRS
    APPLY_OUTPUT = meff_algs.ApplyFragmentationAlgorithm.OUTPUT
    
    def __init__(self,fsModel):
        self.parser_name = "FragmModel"
        self.fsModel = fsModel
        #self.dataClipFlag = False
        #self.clip_layer = None
        super().__init__(self,self.FIELDS)
        
    def mkItemFromDict(self,dict):
        #item = FragmItem(dict["in_layer"],dict["expr"],dict["buffer"],dict["name"])
        if "in_layer" in dict:
            new_dict = { self.PREPARE_INPUT : dict["in_layer"],
                         self.PREPARE_CLIP_LAYER : None,
                         self.PREPARE_SELECT_EXPR : dict["expr"],
                         self.PREPARE_BUFFER : dict["buffer"],
                         self.PREPARE_NAME : dict["name"] }
            return FragmItem(new_dict)
        else:
            if (self.PREPARE_CLIP_LAYER not in dict) or (dict[self.PREPARE_CLIP_LAYER] == "None"):
                dict[self.PREPARE_CLIP_LAYER] = None
            return FragmItem(dict)
        
    def setDataClipLayer(self,layer_path):
        self.clip_layer = layer_path
        
    def getFragmLayer(self):
        return QgsProcessingUtils.generateTempFilename("fragm.gpkg")
        
    def getBuffersMergedLayer(self):
        return QgsProcessingUtils.generateTempFilename("fragmBuffersMerged.shp")
        
    def getLanduseFragmLayer(self):
        return QgsProcessingUtils.generateTempFilename("landuseFragm.gpkg")
        
    def getFinalLayer(self):
        #return self.fsModel.mkOutputFile("landuseFragmSingleGeom.gpkg")
        return self.fsModel.mkOutputFile("landuseFragmSingleGeom.gpkg")
        
    # def applyItemsOld(self,indexes):
        # fragmMsg = "Application of fragmentation data to landuse"
        # progress.progressFeedback.beginSection(fragmMsg)
        # for item in self.items:
            # in_layer_path = self.fsModel.getOrigPath(item.dict["in_layer"])
            # in_layer = qgsUtils.loadVectorLayer(in_layer_path)
            # if self.fsModel.paramsModel.dataClipFlag:
                # territory_layer = self.fsModel.paramsModel.getTerritoryLayer()
                # source_layer = qgsTreatments.applyVectorClip(in_layer,territory_layer,'memory:')
            # else:
                # source_layer = in_layer
            # name = item.dict["name"]
            # selectionPath = item.getSelectionLayer()
            # qgsTreatments.selectGeomByExpression(source_layer,item.dict["expr"],selectionPath,name)
            # bufferPath = item.getBufferLayer()
            # utils.debug("bufferPath = " + str(bufferPath))
            # bufferLayer = qgsTreatments.applyBufferFromExpr(selectionPath,item.dict["buffer"],bufferPath)
            # qgsUtils.loadVectorLayer(bufferLayer,loadProject=True)
        # buf_layers = [item.getBufferLayer() for item in self.items]
        # fragm_path = self.getBuffersMergedLayer()
        # fragm_layer = qgsTreatments.mergeVectorLayers(buf_layers,params.params.crs,fragm_path)
        # if not fragm_layer:
            # assert(False)
        # utils.debug("fragm_layer : " + str(fragm_layer))
        # qgsUtils.loadVectorLayer(fragm_layer,loadProject=True)
        # landuseLayer = self.fsModel.landuseModel.getDissolveLayer()
        # landuseFragmPath = self.getLanduseFragmLayer()
        # qgsUtils.removeVectorLayer(landuseFragmPath)
        # qgsTreatments.applyDifference(landuseLayer,fragm_layer,landuseFragmPath)
        # qgsUtils.loadVectorLayer(landuseFragmPath,loadProject=True)
        # singleGeomPath = self.getFinalLayer()
        # singleGeomLayer = qgsTreatments.multiToSingleGeom(landuseFragmPath,'memory:')
        # qgsUtils.normFids(singleGeomLayer)
        # qgsUtils.writeVectorLayer(singleGeomLayer,singleGeomPath)
        # qgsUtils.loadVectorLayer(singleGeomPath,loadProject=True)
        # progress.progressFeedback.endSection()
        
    def applyItemsWithContext(self,context,feedback,indexes=None):
        fragmMsg = "Application of fragmentation data to landuse"
        progress.progressFeedback.beginSection(fragmMsg)
        #clip_layer = self.fsModel.paramsModel.getTerritoryLayer()
        #clip_layer = self.clip_layer if self.dataClipFlag else None
        prepared_layers = []
        for item in self.items:
            in_layer_path = self.fsModel.getOrigPath(item.dict[self.PREPARE_INPUT])
            clip_layer = item.dict[self.PREPARE_CLIP_LAYER]
            select_expr = item.dict[self.PREPARE_SELECT_EXPR]
            buffer_expr = item.dict[self.PREPARE_BUFFER]
            selectionPath = item.getSelectionLayer()
            name = item.dict[self.PREPARE_NAME]
            parameters = { self.PREPARE_INPUT : in_layer_path,
                           self.PREPARE_CLIP_LAYER : clip_layer,
                           self.PREPARE_SELECT_EXPR : select_expr,
                           self.PREPARE_BUFFER : buffer_expr,
                           self.PREPARE_OUTPUT : selectionPath }
            prepared = qgsTreatments.applyProcessingAlg(
                "Meff","prepareFragm",parameters,
                context=context,feedback=feedback)
            prepared_layers.append(prepared)
        landuseLayer = self.fsModel.landuseModel.getDissolveLayer()
        res_path = self.getFinalLayer()
        qgsUtils.removeVectorLayer(res_path)
        parameters = { self.APPLY_LANDUSE : landuseLayer,
                       self.APPLY_FRAGMENTATION : prepared_layers,
                       self.APPLY_CRS : params.defaultCrs,
                       self.APPLY_OUTPUT : res_path }
        res = qgsTreatments.applyProcessingAlg(
            "Meff","applyFragm",parameters,
            context=context,feedback=feedback)
        qgsUtils.loadVectorLayer(res_path,loadProject=True)
        progress.progressFeedback.endSection()
        return res
            
    def fromXMLRoot(self,root):
        utils.debug("fromXML")
        for item in root:
            utils.debug(str(item))
            dict = item.attrib
            fragmItem = self.mkItemFromDict(dict)
            self.addItem(fragmItem)
        self.layoutChanged.emit()
            
        
        
class FragmConnector(abstract_model.AbstractConnector):

    def __init__(self,dlg,fragmModel):
        self.parser_name = "FragmConnector"
        self.dlg = dlg
        #fragmModel = FragmModel()
        self.onlySelection = False
        self.dataClipFlag = False
        self.clip_layer = None
        super().__init__(fragmModel,self.dlg.fragmView,
                        self.dlg.fragmAdd,self.dlg.fragmRemove,
                        self.dlg.fragmRun)

    def initGui(self):
        self.dlg.fragmInputLayerCombo.setFilters(QgsMapLayerProxyModel.VectorLayer)
        
    def connectComponents(self):
        super().connectComponents()
        #self.dlg.fragmInLayer.fileChanged.connect(self.setInLayer)
        self.dlg.fragmInputLayerCombo.layerChanged.connect(self.setInLayerFromCombo)
        self.layerComboDlg = qgsUtils.LayerComboDialog(self.dlg,
                                                       self.dlg.fragmInputLayerCombo,
                                                       self.dlg.fragmInputLayer)
        self.dlg.fragmClipDataFlag.stateChanged.connect(self.switchDataClipFlag)
        self.dlg.fragmClipLayer.fileChanged.connect(self.model.setDataClipLayer)
        
    def applyItems(self):
        super().applyItems()
        res_path = self.model.getFinalLayer()
        res_layer = qgsUtils.loadVectorLayer(res_path)
        self.dlg.resultsInputLayer.setLayer(res_layer)
        
    def setInLayerFromCombo(self,layer):
        self.dlg.fragmExpr.setLayer(layer)
        self.dlg.fragmBuffer.setLayer(layer)
    
    def switchDataClipFlag(self,state):
        utils.debug("switchDataClipFlag")
        self.dataClipFlag = not self.dataClipFlag
        self.dlg.fragmClipLayer.setEnabled(self.dataClipFlag)
    
    # def setInLayer(self,path):
        # utils.debug("setInLayer " + str(path))
        # layer = qgsUtils.loadVectorLayer(path,loadProject=True)
        # utils.debug("layer = " + str(layer))
        # self.dlg.fragmInputLayerCombo.setLayer(layer)
        
    def mkItem(self):
        in_layer = self.dlg.fragmInputLayerCombo.currentLayer()
        if not in_layer:
            utils.user_error("No layer selected")
        in_layer_path = self.model.fsModel.normalizePath(qgsUtils.pathOfLayer(in_layer))
        clip_layer = self.clip_layer if self.dataClipFlag else None
        expr = self.dlg.fragmExpr.expression()
        buffer = self.dlg.fragmBuffer.expression()
        if not buffer:
            utils.user_error("Empty buffer")
        name = self.dlg.fragmName.text()
        if not name:
            utils.user_error("Empty name")
        dict = { FragmModel.PREPARE_INPUT : in_layer_path,
                 FragmModel.PREPARE_CLIP_LAYER : clip_layer,
                 FragmModel.PREPARE_SELECT_EXPR : expr,
                 FragmModel.PREPARE_BUFFER : buffer,
                 FragmModel.PREPARE_NAME : name }
        #item = FragmItem(in_layer_path,expr,buffer,name)
        item = FragmItem(dict)
        return item
        
        