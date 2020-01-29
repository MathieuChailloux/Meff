# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FragScape
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

from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import QgsProcessing, QgsProcessingAlgorithm, QgsProcessingException
from qgis.core import (QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterExpression,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingProvider,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingUtils,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterMatrix,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterCrs,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProperty,
                       QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsProcessingMultiStepFeedback)
from qgis.core import QgsField, QgsFields, QgsFeature, QgsFeatureSink

import processing
import xml.etree.ElementTree as ET

from ..qgis_lib_mc import utils, qgsTreatments, qgsUtils, feedbacks
from ..steps import params
            
NB_DIGITS = 5
            
class FragScapeVectorAlgorithm(QgsProcessingAlgorithm):
    
    def group(self):
        return "Vector"
    
    def groupId(self):
        return "fsVect"
        
    def name(self):
        return self.ALG_NAME
        
    def createInstance(self):
        assert(False)
        
    def displayName(self):
        assert(False)
        
    def shortHelpString(self):
        assert(False)
        
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
            
class PrepareLanduseAlgorithm(FragScapeVectorAlgorithm):

    ALG_NAME = "prepareLanduse"

    INPUT = "INPUT"
    CLIP_LAYER = "CLIP_LAYER"
    SELECT_EXPR = "SELECT_EXPR"
    OUTPUT = "OUTPUT"
        
    def createInstance(self):
        return PrepareLanduseAlgorithm()
        
    def displayName(self):
        return self.tr("1 - Prepare land cover data")
        
    def shortHelpString(self):
        return self.tr("This algorithms prepares land cover data by applying selection (from expression) and dissolving geometries")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Input layer"),
                [QgsProcessing.TypeVectorAnyGeometry]))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CLIP_LAYER,
                description=self.tr("Clip layer"),
                types=[QgsProcessing.TypeVectorPolygon],
                optional=True))
        self.addParameter(
            QgsProcessingParameterExpression(
                self.SELECT_EXPR,
                self.tr("Selection expression"),
                "",
                self.INPUT))
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output layer")))
                
    def processAlgorithm(self,parameters,context,feedback):
        # Dummy function to enable running an alg inside an alg
        # def no_post_process(alg, context, feedback):
            # pass
        input = self.parameterAsVectorLayer(parameters,self.INPUT,context)
        feedback.pushDebugInfo("input = " + str(input))
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        qgsUtils.normalizeEncoding(input)
        feedback.pushDebugInfo("input ok")
        clip_layer = self.parameterAsVectorLayer(parameters,self.CLIP_LAYER,context)
        expr = self.parameterAsExpression(parameters,self.SELECT_EXPR,context)
        if clip_layer is None:
            clipped = input
        else:
            clipped_path = params.mkTmpLayerPath('landuseClipped.gpkg')
            qgsTreatments.applyVectorClip(input,clip_layer,clipped_path,context,feedback)
            clipped = qgsUtils.loadVectorLayer(clipped_path)
            feedback.pushDebugInfo("clipped  = " + str(clipped))
        selected_path = params.mkTmpLayerPath('landuseSelection.gpkg')
        qgsTreatments.selectGeomByExpression(clipped,expr,selected_path,'landuseSelection')
        # selected = qgsUtils.loadVectorLayer(selected_path)
        # selected = qgsTreatments.extractByExpression(
           # clipped,expr,'memory:',
           # context=context,feedback=feedback)
        feedback.pushDebugInfo("selected = " + str(selected_path))
        output = parameters[self.OUTPUT]
        dissolved = qgsTreatments.dissolveLayer(selected_path,output,context=context,feedback=feedback)
        dissolved = None
        return {self.OUTPUT : dissolved}
        
        
class PrepareFragmentationAlgorithm(FragScapeVectorAlgorithm):

    ALG_NAME = "prepareFragm"

    INPUT = "INPUT"
    CLIP_LAYER = "CLIP_LAYER"
    SELECT_EXPR = "SELECT_EXPR"
    BUFFER = "BUFFER_EXPR"
    NAME = "NAME"
    OUTPUT = "OUTPUT"
        
    def createInstance(self):
        return PrepareFragmentationAlgorithm()
        
    def displayName(self):
        return self.tr("2.1 - Prepare fragmentation data")
        
    def shortHelpString(self):
        return self.tr("This algorithm prepares a fragmentation layer by applying clip, selection and buffer")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                description=self.tr("Input layer"),
                types=[QgsProcessing.TypeVectorLine]))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.CLIP_LAYER,
                description=self.tr("Clip layer"),
                types=[QgsProcessing.TypeVectorPolygon],
                optional=True))
        self.addParameter(
            QgsProcessingParameterExpression(
                self.SELECT_EXPR,
                description=self.tr("Selection expression"),
                parentLayerParameterName=self.INPUT,
                optional=True))
        self.addParameter(
            QgsProcessingParameterExpression(
                self.BUFFER,
                description=self.tr("Buffer expression"),
                parentLayerParameterName=self.INPUT,
                optional=True))
        self.addParameter(
            QgsProcessingParameterString(
                self.NAME,
                description=self.tr("Identifier"),
                optional=True))
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                description=self.tr("Output layer")))
                
    def processAlgorithm(self,parameters,context,feedback):
        # Parameters
        feedback.pushDebugInfo("parameters = " + str(parameters))
        input = self.parameterAsVectorLayer(parameters,self.INPUT,context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        qgsUtils.normalizeEncoding(input)
        clip = self.parameterAsVectorLayer(parameters,self.CLIP_LAYER,context)
        clip_flag = (clip is None)
        select_expr = self.parameterAsExpression(parameters,self.SELECT_EXPR,context)
        feedback.pushDebugInfo("select_expr : " + str(select_expr))
        buffer_expr = self.parameterAsExpression(parameters,self.BUFFER,context)
        name = self.parameterAsString(parameters,self.NAME,context)
        if not name:
            name = 'fragm'
        feedback.pushDebugInfo("buffer_expr : " + str(buffer_expr))
        if buffer_expr == "" and input.geometryType() != QgsWkbTypes.PolygonGeometry:
           feedback.pushDebugInfo("Empty buffer with non-polygon layer")
        output = parameters[self.OUTPUT]
        if clip is None:
            clipped = input
        else:
            clipped_path = params.mkTmpLayerPath(name + 'Clipped.gpkg')
            qgsTreatments.applyVectorClip(input,clip,clipped_path,context,feedback)
            clipped = qgsUtils.loadVectorLayer(clipped_path)
        if select_expr == "":
            selected = clipped
        else:
            selected_path = params.mkTmpLayerPath(name + 'Selected.gpkg')
            qgsTreatments.selectGeomByExpression(clipped,select_expr,selected_path,name)
            selected = selected_path
        if buffer_expr == "":
            buffered = selected
        else:
            buffer_expr_prep = QgsProperty.fromExpression(buffer_expr)
            buffered = qgsTreatments.applyBufferFromExpr(selected,buffer_expr_prep,output,context,feedback)
        if buffered == input:
            buffered = qgsUtils.pathOfLayer(buffered)
        return {self.OUTPUT : buffered}
        

        
class ApplyFragmentationAlgorithm(FragScapeVectorAlgorithm):

    ALG_NAME = "applyFragm"

    LANDUSE = "LANDUSE"
    FRAGMENTATION = "FRAGMENTATION"
    CRS = "CRS"
    OUTPUT = "OUTPUT"
        
    def createInstance(self):
        return ApplyFragmentationAlgorithm()
        
    def displayName(self):
        return self.tr("2.2 - Apply fragmentation")
        
    def shortHelpString(self):
        return self.tr("This algorithm builds a layer of patches from a land cover layer and fragmentation layers. Overlaying geometries are removed and remaining ones are cast to single geometry type.")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.LANDUSE,
                self.tr("Land cover layer"),
                [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.FRAGMENTATION,
                self.tr("Fragmentation layers"),
                QgsProcessing.TypeVectorPolygon))
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                description=self.tr("Output CRS"),
                defaultValue=params.defaultCrs))
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output layer")))
                
    def processAlgorithm(self,parameters,context,feedback):
        # Parameters
        landuse = self.parameterAsVectorLayer(parameters,self.LANDUSE,context)
        if landuse is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.LANDUSE))
        qgsUtils.normalizeEncoding(landuse)
        fragm_layers = self.parameterAsLayerList(parameters,self.FRAGMENTATION,context)
        output = self.parameterAsOutputLayer(parameters,self.OUTPUT,context)
        crs = self.parameterAsCrs(parameters,self.CRS,context)
        # output = parameters[self.OUTPUT]
        # Merge fragmentation layers
        fragm_path = params.mkTmpLayerPath("fragm.gpkg")
        fragm_layer = qgsTreatments.mergeVectorLayers(fragm_layers,crs,fragm_path)
        feedback.pushDebugInfo("fragm_layer = " + str(fragm_layer))
        if fragm_layer is None:
            raise QgsProcessingException("Fragmentation layers merge failed")
        # Apply difference
        diff_path = params.mkTmpLayerPath("diff.gpkg")
        diff_layer = qgsTreatments.applyDifference(
            landuse,fragm_layer,diff_path,
            context=context,feedback=feedback)
        if fragm_layer is None:
            raise QgsProcessingException("Difference landuse/fragmentation failed")
        # Multi to single part
        singleGeomLayer = qgsTreatments.multiToSingleGeom(
            diff_layer,output,
            context=context,feedback=feedback)
        if fragm_layer is None:
            raise QgsProcessingException("Multi to single part failed")
        return {self.OUTPUT : singleGeomLayer}
        
 
class MeffAlgUtils:

    NB_DIGITS = 5
    
    INPUT = "INPUT"
    REPORTING = "REPORTING"
    CLASS = "CLASS"
    CRS = "CRS"
    INCLUDE_CBC = "INCLUDE_CBC"
    UNIT = "UNIT"
    OUTPUT = "OUTPUT"
    OUTPUT_VAL = "OUTPUT_VAL"
    
    SUM_AI = "sum_ai"
    SUM_AI_SQ = "sum_ai_sq"
    SUM_AI_SQ_CBC = "sum_ai_sq_cbc"
    DIVISOR = "divisor"

    # Output layer fields
    ID = "fid"
    NB_PATCHES = "nb_patches"
    REPORT_AREA = "report_area"
    INTERSECTING_AREA = "intersecting_area"
    # Main measures
    MESH_SIZE = "effective_mesh_size"
    CBC_MESH_SIZE = "CBC_effective_mesh_size"
    DIVI = "landscape_division"
    SPLITTING_INDEX = "splitting_index"
    # Auxiliary measures
    COHERENCE = "coherence"
    SPLITTING_DENSITY = "splitting_density"
    NET_PRODUCT = "net_product"
    CBC_NET_PRODUCT = "CBC_net_product"
    
    UNIT_DIVISOR = [1, 100, 10000, 1000000]
    
    DEFAULT_CRS = QgsCoordinateReferenceSystem("epsg:2154")
    
    def getUnitOptions(self):
        return [self.tr("m² (square meters)"),
            self.tr("dm² (square decimeters / ares)"),
            self.tr("hm² (square hectometers / hectares)"),
            self.tr("km² (square kilometers)")]
            
    def mkReportFields(self,include_cbc=False):
        report_id_field = QgsField(self.ID, QVariant.Int)
        mesh_size_field = QgsField(self.MESH_SIZE, QVariant.Double)
        nb_patches_field = QgsField(self.NB_PATCHES, QVariant.Int)
        report_area_field = QgsField(self.REPORT_AREA, QVariant.Double)
        intersecting_area_field = QgsField(self.INTERSECTING_AREA, QVariant.Double)
        div_field = QgsField(self.DIVI, QVariant.Double)
        split_index_field = QgsField(self.SPLITTING_INDEX, QVariant.Double)
        coherence_field = QgsField(self.COHERENCE, QVariant.Double)
        split_density_field = QgsField(self.SPLITTING_DENSITY, QVariant.Double)
        net_product_field = QgsField(self.NET_PRODUCT, QVariant.Double)
        if include_cbc:
            cbc_mesh_size_field = QgsField(self.CBC_MESH_SIZE, QVariant.Double)
            cbc_net_product_field = QgsField(self.CBC_NET_PRODUCT, QVariant.Double)
        output_fields = QgsFields()
        output_fields.append(report_id_field)
        if include_cbc:
            output_fields.append(cbc_mesh_size_field)
        output_fields.append(mesh_size_field)
        output_fields.append(nb_patches_field)
        output_fields.append(report_area_field)
        output_fields.append(intersecting_area_field)
        output_fields.append(div_field)
        output_fields.append(split_index_field)
        output_fields.append(coherence_field)
        output_fields.append(split_density_field)
        output_fields.append(net_product_field)
        if include_cbc:
            output_fields.append(cbc_net_product_field)
        return output_fields
                
    def mkResFeat(self,include_cbc):
        if not self.report_layer or self.report_layer.featureCount() == 0:
            raise QgsProcessingException("Invalid reporting layer")
        for f in self.report_layer.getFeatures():
            report_feat = f
        output_fields = self.mkReportFields(include_cbc)
        res_feat = QgsFeature(output_fields)
        res_feat.setGeometry(report_feat.geometry())
        res_feat[self.ID] = report_feat.id()
        return res_feat
        
    def fillResFeat(self,res_feat,res_dict):
        divisor = float(res_dict[self.DIVISOR])
        report_area = float(res_dict[self.REPORT_AREA]) / divisor
        report_area_sq = report_area * report_area
        sum_ai = float(res_dict[self.SUM_AI])  / divisor
        sum_ai_sq = float(res_dict[self.SUM_AI_SQ]) / (divisor * divisor)
        utils.debug("sum_ai = " + str(sum_ai))
        utils.debug("sum_ai_sq = " + str(sum_ai_sq))
        utils.debug("report_area = " + str(report_area))
        utils.debug("report_area_sq = " + str(report_area_sq))
        res_feat[self.NB_PATCHES] = res_dict[self.NB_PATCHES]
        # Metrics
        res_feat[self.NET_PRODUCT] = round(sum_ai_sq,NB_DIGITS)
        res_feat[self.REPORT_AREA] = report_area
        res_feat[self.INTERSECTING_AREA] = sum_ai
        res_feat[self.COHERENCE] = sum_ai_sq / report_area_sq if report_area_sq > 0 else 0
        res_feat[self.SPLITTING_DENSITY] = report_area / sum_ai if sum_ai > 0 else 0
        res_feat[self.MESH_SIZE] = round(sum_ai_sq / report_area, NB_DIGITS)
        res_feat[self.SPLITTING_INDEX] = report_area_sq / sum_ai_sq if sum_ai_sq > 0 else 0
        res_feat[self.DIVI] = 1 - res_feat[self.COHERENCE]
        # CBC Metrics
        if self.SUM_AI_SQ_CBC in res_dict:
            sum_ai_sq_cbc = float(res_dict[self.SUM_AI_SQ_CBC]) / (divisor * divisor)
            res_feat[self.CBC_NET_PRODUCT] = round(sum_ai_sq_cbc,NB_DIGITS)
            res_feat[self.CBC_MESH_SIZE] = round(sum_ai_sq_cbc / report_area,NB_DIGITS)
            
        
    def mkResSink(self,parameters,res_feat,context,include_cbc=False):
        report_fields = self.mkReportFields(include_cbc)
        wkb_type = self.report_layer.wkbType()
        report_crs = self.report_layer.sourceCrs()
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            report_fields,
            wkb_type,
            report_crs)
        sink.addFeature(res_feat)
        return dest_id
        
    def mkOutputs(self,parameters,res_dict,context):
        if self.report_layer:
            nb_feats = self.report_layer.featureCount()
            if nb_feats != 1:
                raise QgsProcessingException("Report layer has "
                    + str(nb_feats) + " features but only 1 was expected")
            include_cbc = self.SUM_AI_SQ_CBC in res_dict
            utils.debug("include_cbc = " + str(include_cbc))
            res_feat = self.mkResFeat(include_cbc)
            self.fillResFeat(res_feat,res_dict)
            dest_id = self.mkResSink(parameters,res_feat,context,include_cbc)
            res_layer = dest_id
            res_val = res_feat[self.CBC_MESH_SIZE] if include_cbc else res_feat[self.MESH_SIZE]
        else:
            res_layer = None
            res_val = round(res_dict[self.SUM_AI_SQ] / res_dict[self.REPORT_AREA], self.NB_DIGITS)
        return (res_layer, res_val)
    
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
        
    def name(self):
        return self.ALG_NAME


class FragScapeMeffVectorAlgorithm(FragScapeVectorAlgorithm,MeffAlgUtils):
    
    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr("Input layer"),
                [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.REPORTING,
                self.tr("Reporting layer"),
                [QgsProcessing.TypeVectorPolygon]))
        self.addParameter(
            QgsProcessingParameterCrs(
                self.CRS,
                description=self.tr("Output CRS"),
                defaultValue=params.defaultCrs))
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INCLUDE_CBC,
                self.tr("Include Cross-boundary connection metrics")))
        self.addParameter(
            QgsProcessingParameterEnum(
                self.UNIT,
                description=self.tr("Report areas unit"),
                options=self.getUnitOptions()))
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr("Output layer")))
                
    def prepareInputs(self,parameters,context,feedback):
        input = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        report_layer = self.parameterAsVectorLayer(parameters,self.REPORTING,context)
        if input is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))
        reporting = self.parameterAsVectorLayer(parameters,self.REPORTING,context)
        if reporting is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.REPORTING))
        self.report_layer = reporting
        self.crs = self.parameterAsCrs(parameters,self.CRS,context)
        unit = self.parameterAsEnum(parameters,self.UNIT,context)
        self.include_cbc = self.parameterAsBool(parameters,self.INCLUDE_CBC,context)
        self.unit_divisor = self.UNIT_DIVISOR[unit]
        return (input, reporting)


class MeffVectorGlobal(FragScapeMeffVectorAlgorithm):

    ALG_NAME = "meffVectorGlobal"
    
    # OUTPUT_GLOBAL_MEFF = "GLOBAL_MEFF"
        
    def createInstance(self):
        return MeffVectorGlobal()
        
    def displayName(self):
        return self.tr("Vector Effective Mesh Size (Global)")
        
    def shortHelpString(self):
        return self.tr("Computes effective mesh size from patch layer and boundary of reporting layer (features are dissolved if needed)")
                
    def processAlgorithm(self,parameters,context,feedback):
        feedback.pushDebugInfo("Start " + str(self.name()))
        # Parameters
        source, boundary = self.prepareInputs(parameters, context, feedback)
        # CRS reprojection
        source_crs = source.crs().authid()
        boundary_crs = boundary.crs().authid()
        feedback.pushDebugInfo("source_crs = " + str(source_crs))
        feedback.pushDebugInfo("boundary_crs = " + str(boundary_crs))
        feedback.pushDebugInfo("crs = " + str(self.crs.authid()))
        if source_crs != self.crs.authid():
            source_path = params.mkTmpLayerPath('res_source_reproject.gpkg')
            qgsTreatments.applyReprojectLayer(source,self.crs,source_path,context,feedback)
            source = qgsUtils.loadVectorLayer(source_path)
        if boundary_crs != self.crs.authid():
            boundary_path = params.mkTmpLayerPath('res_boundary_reproject.gpkg')
            qgsTreatments.applyReprojectLayer(boundary,self.crs,boundary_path,context,feedback)
            boundary = qgsUtils.loadVectorLayer(boundary_path)
        # Clip by boundary
        intersected_path = params.mkTmpLayerPath('res_source_intersected.gpkg')
        qgsTreatments.selectIntersection(source,boundary,context,feedback)
        qgsTreatments.saveSelectedFeatures(source,intersected_path,context,feedback)
        selected_path = intersected_path
        source = qgsUtils.loadVectorLayer(selected_path)
        # Dissolve
        if boundary.featureCount() > 1:
            dissolved_path = params.mkTmpLayerPath('res_boundary_dissolved.gpkg')
            qgsTreatments.dissolveLayer(boundary,dissolved_path,context,feedback)
            boundary = qgsUtils.loadVectorLayer(dissolved_path)
            self.report_layer = boundary
        # Algorithm
        # progress step
        nb_feats = source.featureCount()
        feedback.pushDebugInfo("nb_feats = " + str(nb_feats))
        if nb_feats == 0:
            utils.warn("Empty input layer : " + qgsUtils.pathOfLayer(source))
            progress_step = 100.0
            #raise QgsProcessingException("Empty layer : " + qgsUtils.pathOfLayer(source))
        else:
            progress_step = 100.0 / nb_feats
        curr_step = 0
        # Reporting area
        for report_feat in boundary.getFeatures():
            report_geom = report_feat.geometry()
        report_area = report_geom.area()
        sum_ai = 0
        feedback.pushDebugInfo("report_area = " + str(report_area))
        if report_area == 0:
            raise QgsProcessingException("Empty reporting area")
        else:
            feedback.pushDebugInfo("ok")
        net_product = 0
        cbc_net_product = 0
        intersecting_area = 0
        for f in source.getFeatures():
            f_geom = f.geometry()
            f_area = f_geom.area()
            sum_ai += f_area
            intersection = f_geom.intersection(report_geom)
            intersection_area = intersection.area()
            intersecting_area += intersection_area
            net_product += intersection_area * intersection_area
            cbc_net_product += f_area * intersection_area
            # Progress update
            curr_step += 1
            feedback.setProgress(int(curr_step * progress_step))
        report_area_sq = report_area * report_area
        # Outputs
        res_dict = { self.REPORT_AREA : report_area,
            self.SUM_AI : sum_ai,
            self.SUM_AI_SQ : net_product,
            self.NB_PATCHES : nb_feats,
            self.DIVISOR : self.unit_divisor,
        }
        if self.include_cbc:
            res_dict[self.SUM_AI_SQ_CBC] = cbc_net_product
        res_layer, res_val = self.mkOutputs(parameters,res_dict,context)
        return {self.OUTPUT: res_layer, self.OUTPUT_VAL : res_val}

   

class MeffVectorReport(FragScapeMeffVectorAlgorithm):

    ALG_NAME = "meffVectorReport"
        
    def createInstance(self):
        return MeffVectorReport()
        
    def displayName(self):
        return self.tr("Vector Effective Mesh Size (Reporting)")
        
    def shortHelpString(self):
        return self.tr("Computes effective mesh size from patch layer for each feature of reporting layer.")
                
    def processAlgorithm(self,parameters,context,feedback):
        source, reporting = self.prepareInputs(parameters, context, feedback)
        output = parameters[self.OUTPUT]
        # Algorithm
        # progress step
        nb_feats = reporting.featureCount()
        feedback.pushDebugInfo("nb_feats = " + str(nb_feats))
        if nb_feats == 0:
            raise QgsProcessingException("Empty layer")
        curr_step = 0
        # gna gna
        multi_feedback = feedbacks.ProgressMultiStepFeedback(nb_feats, feedback)
        report_layers = []
        for count, report_feat in enumerate(reporting.getFeatures()):
            multi_feedback.setCurrentStep(count)
            report_id = report_feat.id()
            reporting.selectByIds([report_id])
            select_path = params.mkTmpLayerPath("reportingSelection" + str(report_feat.id()) + ".gpkg")
            qgsTreatments.saveSelectedFeatures(reporting,select_path,context,multi_feedback)
            report_computed_path = params.mkTmpLayerPath("reportingComputed" + str(report_feat.id()) + ".gpkg")
            parameters = { MeffVectorGlobal.INPUT : source,
                           MeffVectorGlobal.REPORTING : select_path,
                           MeffVectorGlobal.CRS : self.crs,
                           MeffVectorGlobal.INCLUDE_CBC : self.include_cbc,
                           MeffVectorGlobal.UNIT : parameters[self.UNIT],
                           MeffVectorGlobal.OUTPUT : report_computed_path }
            qgsTreatments.applyProcessingAlg('FragScape',
                                             MeffVectorGlobal.ALG_NAME,
                                             parameters,context,multi_feedback)
            report_layers.append(report_computed_path)
        qgsTreatments.mergeVectorLayers(report_layers,self.crs,output)
        return {self.OUTPUT: output}

