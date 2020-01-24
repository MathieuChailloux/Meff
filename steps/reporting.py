# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FragScape
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

from qgis.core import QgsMapLayerProxyModel, QgsField, QgsFeature, QgsProcessingFeedback, QgsVectorLayerCache
from qgis.gui import QgsFileWidget, QgsAttributeTableModel, QgsAttributeTableView, QgsAttributeTableFilterModel
from qgis.utils import iface
from PyQt5.QtCore import QVariant
from processing import QgsProcessingUtils

from ..qgis_lib_mc import utils, abstract_model, qgsUtils, feedbacks, qgsTreatments
from ..algs import FragScape_algs_provider
from ..algs.FragScape_algs import (
    MeffAlgUtils,
    MeffVectorGlobal as MeffGlobalV,
    MeffVectorReport as MeffReportV )
from ..algs.FragScape_raster_algs import (
    MeffRaster as MeffR,
    MeffRasterReport,
    MeffRasterCBC as MeffRCBC )
from . import params, fragm

class ReportingModel(abstract_model.DictModel):

    # Configuration slots
    INPUT = "input_layer"
    SELECT_EXPR = "select_expr"
    REPORTING = "reporting_layer"
    METHOD = "method"
    INCLUDE_CBC = "include_cbc"
    UNIT = "unit"
    OUTPUT = "output"
    
    CUT_METHOD = 0
    CBC_METHOD = 1

    def __init__(self,fsModel):
        self.parser_name = "Reporting"
        self.fsModel = fsModel
        self.input_layer = None
        self.select_expr = None
        self.reporting_layer = None
        # self.method = self.CUT_METHOD
        self.includeCBC = False
        self.unit = 0
        self.out_layer = None
        self.init_fields = []
        self.fields = self.init_fields
        super().__init__(self,self.fields)
                
    def getInputLayer(self):
        utils.debug("input_layer = " + str(self.input_layer))
        if not self.input_layer:
            self.input_layer = self.fsModel.fragmModel.getFinalLayer()
        return self.input_layer
                
    def setOutLayer(self,layer_path):
        self.out_layer = layer_path
        
    def getOutLayer(self):
        if self.out_layer:
            return self.fsModel.getOrigPath(self.out_layer)
        elif self.includeCBC:
            return self.fsModel.mkOutputFile("reportingResultsCBC.gpkg")
        else:
            return self.fsModel.mkOutputFile("reportingResults.gpkg")
        
    # def mkIntersectionLayer(self):
        # pass
        
    # def getIntersectionLayerPath(self):
        # return self.fsModel.mkOutputFile("reportingIntersection.gpkg")
        
    def getReportingResultsLayerPath(self):
        return self.fsModel.mkOutputFile("reportingResults.gpkg")
                
    def runReportingWithContext(self,context,feedback):
        reportingMsg = "Reporting layer computation"
        feedback.pushDebugInfo("unit = " + str(self.unit))
        feedbacks.progressFeedback.beginSection(reportingMsg)
        input_layer = self.getInputLayer()
        selected = input_layer
        crs = self.fsModel.paramsModel.crs
        results_path = self.getOutLayer()
        feedback.pushDebugInfo("CBC mode = " + str(self.includeCBC))
        feedback.pushDebugInfo("results_path = " + str(results_path))
        global_results_path = self.fsModel.mkOutputFile("reportingResultsGlobal.gpkg")
        qgsUtils.removeVectorLayer(results_path)
        qgsUtils.removeVectorLayer(global_results_path)
        if self.fsModel.modeIsVector():
            parameters1 = { MeffReportV.INPUT : selected,
                           # MeffReportV.SELECT_EXPR : self.select_expr,
                           MeffReportV.REPORTING : self.reporting_layer,
                           MeffReportV.CRS : crs,
                           MeffReportV.INCLUDE_CBC : self.includeCBC,
                           MeffReportV.UNIT : self.unit,
                           MeffReportV.OUTPUT : results_path }
            res1 = qgsTreatments.applyProcessingAlg('FragScape',
                MeffReportV.ALG_NAME,parameters1,
                context=context,feedback=feedback,onlyOutput=False)
            parameters2 = { MeffGlobalV.INPUT : selected,
                           # MeffGlobalV.SELECT_EXPR : self.select_expr,
                           MeffGlobalV.REPORTING : self.reporting_layer,
                           MeffGlobalV.CRS : crs,
                           MeffGlobalV.INCLUDE_CBC : self.includeCBC,
                           MeffGlobalV.UNIT : self.unit,
                           MeffGlobalV.OUTPUT : global_results_path }
            res2 = qgsTreatments.applyProcessingAlg('FragScape',
                MeffGlobalV.ALG_NAME,parameters2,
                context=context,feedback=feedback,onlyOutput=False)
            res_layer = res1[MeffReportV.OUTPUT]
            res_val = res2[MeffReportV.OUTPUT_VAL]
        else:
            parameters = { MeffAlgUtils.INPUT : selected,
                MeffAlgUtils.CLASS : 1,
                MeffAlgUtils.REPORTING : self.reporting_layer,
                MeffAlgUtils.UNIT : self.unit,
                MeffAlgUtils.OUTPUT : global_results_path }
            # res = qgsTreatments.applyProcessingAlg('FragScape',
                # MeffRasterReport.ALG_NAME,parameters,
                # context=context,feedback=feedback,onlyOutput=False)
            # res_layer = res[MeffAlgUtils.OUTPUT]
            if self.includeCBC:
                dissolved_path = params.mkTmpLayerPath('reporting_dissolved.gpkg')
                qgsTreatments.dissolveLayer(self.reporting_layer,dissolved_path,context,feedback)
                parameters[MeffAlgUtils.OUTPUT] = results_path
                parameters[MeffAlgUtils.REPORTING] = dissolved_path
                res = qgsTreatments.applyProcessingAlg('FragScape',
                    MeffRCBC.ALG_NAME,parameters,
                    context=context,feedback=feedback,onlyOutput=False)
                res_layer = res[MeffAlgUtils.OUTPUT]
                res_val = res[MeffAlgUtils.OUTPUT_VAL]
            elif self.reporting_layer:
                parameters[MeffAlgUtils.OUTPUT] = results_path
                res1 = qgsTreatments.applyProcessingAlg('FragScape',
                    MeffRasterReport.ALG_NAME,parameters,
                    context=context,feedback=feedback,onlyOutput=False)
                res_layer = res1[MeffAlgUtils.OUTPUT]
                dissolved_path = params.mkTmpLayerPath('reporting_dissolved.gpkg')
                qgsTreatments.dissolveLayer(self.reporting_layer,dissolved_path,context,feedback)
                parameters[MeffAlgUtils.REPORTING] = dissolved_path
                parameters[MeffAlgUtils.OUTPUT] = global_results_path
                res2 = qgsTreatments.applyProcessingAlg('FragScape',
                    MeffR.ALG_NAME,parameters,
                    context=context,feedback=feedback,onlyOutput=False)
                res_val = res2[MeffAlgUtils.OUTPUT_VAL]
            else:
                res = qgsTreatments.applyProcessingAlg('FragScape',
                    MeffR.ALG_NAME,parameters,
                    context=context,feedback=feedback,onlyOutput=False)
                res_layer = res[MeffAlgUtils.OUTPUT]
                res_val = res[MeffAlgUtils.OUTPUT_VAL]
        feedbacks.progressFeedback.endSection()
        return (res_layer,res_val)
                
    def toXML(self,indent=" "):
        modelParams = {}
        if self.input_layer:
            inputRelPath = self.fsModel.normalizePath(self.input_layer)
            modelParams[self.INPUT] = inputRelPath
        modelParams[self.INCLUDE_CBC] = self.includeCBC
        if self.unit:
            modelParams[self.UNIT] = self.unit
        if self.reporting_layer:
            layerRelPath = self.fsModel.normalizePath(self.reporting_layer)
            modelParams[self.REPORTING] = layerRelPath
        if self.out_layer:
            modelParams[self.OUTPUT] = self.fsModel.normalizePath(self.out_layer)
        xmlStr = super().toXML(indent,modelParams)
        return xmlStr
        
    def fromXMLAttribs(self,attribs):
        if self.INPUT in attribs:
            self.input_layer = self.fsModel.getOrigPath(attribs[self.INPUT])
        if self.REPORTING in attribs:
            self.reporting_layer = self.fsModel.getOrigPath(attribs[self.REPORTING])
        if self.METHOD in attribs:
            method = int(attribs[self.METHOD])
            self.includeCBC = (method > 0)
        if self.INCLUDE_CBC in attribs:
            self.includeCBC = bool(attribs[self.INCLUDE_CBC])
        if self.UNIT in attribs:
            self.unit = int(attribs[self.UNIT])
        if self.OUTPUT in attribs:
            out_layer = self.fsModel.getOrigPath(attribs[self.OUTPUT])
            self.setOutLayer(out_layer)
        
    def fromXMLRoot(self,root):
        self.fromXMLAttribs(root.attrib)
        
# class ReportingConnector(abstract_model.AbstractConnector):
class ReportingConnector:

    
    def __init__(self,dlg,reportingModel):
        self.dlg = dlg
        self.parser_name = "Reporting"
        self.model = reportingModel
        #self.model = reportingModel
        #reportingModel = ReportingModel()
        # super().__init__(reportingModel,self.dlg.resultsView)
        
    def initGui(self):
        self.dlg.resultsInputLayer.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.dlg.resultsReportingLayer.setStorageMode(QgsFileWidget.GetFile)
        self.dlg.resultsReportingLayer.setFilter(qgsUtils.getVectorFilters())
        self.dlg.resultsOutLayer.setStorageMode(QgsFileWidget.SaveFile)
        self.dlg.resultsOutLayer.setFilter(qgsUtils.getVectorFilters())
        #self.attrView = QgsAttributeTableView(self.dlg)
        #self.dlg.gridLayout_9.removeWidget(self.dlg.resultsView)
       # self.dlg.gridLayout_9.addWidget(self.attrView)
        #self.dlg.resultsView.hide()
        #self.dlg.gridLayout_9.removeWidget(self.dlg.resultsView)
        
    def connectComponents(self):
        # super().connectComponents()
        #self.dlg.reportingLayerCombo.layerChanged.connect(self.setLayer)
        self.dlg.resultsInputLayer.layerChanged.connect(self.setInputLayer)
        # self.dlg.resultsSelection.fieldChanged.connect(self.setSelectExpr)
        self.dlg.resultsReportingLayer.fileChanged.connect(self.setReportingLayer)
        # self.dlg.resultsCutMode.currentIndexChanged.connect(self.setMethod)
        self.dlg.resultsCBC.stateChanged.connect(self.setIncludeCBC)
        self.dlg.resultsUnit.currentIndexChanged.connect(self.setUnit)
        self.dlg.resultsOutLayer.fileChanged.connect(self.model.setOutLayer)
        self.dlg.resultsRun.clicked.connect(self.runReporting)
        
    def runReporting(self):
        (res_layer, res_val) = self.model.runReportingWithContext(self.dlg.context,self.dlg.feedback)
        utils.debug("res_layer = " + str(res_layer))
        utils.debug("res_val = " + str(res_val))
        # out_path = res1[MeffAlgUtils.OUTPUT]
        # out_global_meff = res2[MeffAlgUtils.OUTPUT_VAL]
        # UI update
        self.dlg.resultsGlobalRes.setText(str(res_val))
        if res_layer:
            self.loaded_layer = qgsUtils.loadLayer(res_layer,loadProject=True)
        # self.layer_cache = QgsVectorLayerCache(self.loaded_layer,24)
        # self.attribute_model = QgsAttributeTableModel(self.layer_cache)
        # self.attribute_model.loadLayer()
        # self.dlg.resultsView.setModel(self.attribute_model)
        # self.dlg.resultsView.show()
        
    def unloadResults(self):
        self.dlg.resultsGlobalRes.setText(str(0))
        self.loaded_layer = None
        # self.layer_cache = None
        # self.attribute_model = None
        #self.model.items = []
        # self.dlg.resultsView.setModel(None)
        
        
    # def setLayer(self,layer):
        # utils.debug("setLayer " + str(layer.type))
        # self.dlg.reportingLayerCombo.setLayer(layer)
        # self.model.reporting_layer = qgsUtils.pathOfLayer(layer)
    
    # def setMethod(self,idx):
        # if idx == 0:
            # self.model.method = ReportingModel.CUT_METHOD
        # elif idx == 1:
            # self.model.method = ReportingModel.CBC_METHOD
        # else:
            # utils.internal_error("Unexpected index for reporting method : " + str(idx))
            
    def setIncludeCBC(self,state):
        boolVal = state > 0
        self.model.includeCBC = boolVal
            
    def setUnit(self,idx):
        utils.debug("setUnit " + str(idx))
        self.model.unit = idx
    
    def setInputLayer(self,layer):
        utils.debug("setInputLayer to " + str(layer))
        self.unloadResults()
        if layer:
            # self.dlg.resultsSelection.setLayer(layer)
            self.model.input_layer = qgsUtils.pathOfLayer(layer)
        
    def setSelectExpr(self,expr):
        self.model.select_expr = expr
        
    def setReportingLayer(self,path):
        utils.debug("setReportingLayer")
        #loaded_layer = qgsUtils.loadVectorLayer(path,loadProject=True)
        #self.dlg.reportingLayerCombo.setLayer(loaded_layer)
        #self.dlg.resultsSelection.setLayer(loaded_layer)
        self.model.reporting_layer = path
        #self.setLayer(loaded_layer)
        
    def updateUI(self):
        abs_input_layer = self.model.getInputLayer()
        if abs_input_layer and os.path.isfile(abs_input_layer):
            loaded_layer = qgsUtils.loadLayer(abs_input_layer,loadProject=True)
            self.dlg.resultsInputLayer.setLayer(loaded_layer)
        else:
            utils.warn("Could not find results input layer : " + str(abs_input_layer))
        # if self.model.select_expr:
            # self.dlg.resultsSelection.setExpression(self.model.select_expr)
        if self.model.reporting_layer:
            #qgsUtils.loadVectorLayer(self.model.reporting_layer,loadProject=True)
            self.dlg.resultsReportingLayer.setFilePath(self.model.reporting_layer)
        if self.model.includeCBC:
            self.dlg.resultsCBC.setChecked(True)
        if self.model.unit:
            self.dlg.resultsUnit.setCurrentIndex(int(self.model.unit))
        if self.model.out_layer:
            self.dlg.resultsOutLayer.setFilePath(self.model.out_layer)

    def fromXMLRoot(self,root):
        self.model.fromXMLRoot(root)
        self.updateUI()
        
    def toXML(self,indent=" "):
        return self.model.toXML()
        