# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FragScape
                                 A QGIS plugin
 Computes effective mesh size
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

import math
import scipy
import numpy as np

try:
    from osgeo import gdal
except ImportError:
    import gdal

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingUtils,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingOutputNumber,
                       QgsProcessingOutputRasterLayer,
                       QgsProcessingParameterFeatureSource)      

from ..qgis_lib_mc import qgsUtils, qgsTreatments                    
                       
def tr(string):
    return QCoreApplication.translate('Processing', string) 

class MeffRaster(QgsProcessingAlgorithm):

    ALG_NAME = "meffRaster"
    
    INPUT = "INPUT"
    CLASS = "CLASS"
    OUTPUT = "OUTPUT"
        
    def createInstance(self):
        return MeffRaster()
        
    def name(self):
        return self.ALG_NAME
        
    def displayName(self):
        return tr("Raster Effective Mesh Size")
        
    def shortHelpString(self):
        return tr("Computes effective mesh size on a raster layer")

    def initAlgorithm(self, config=None):
        '''Here we define the inputs and output of the algorithm, along
        with some other properties'''
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT, "Input raster layer", optional=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.CLASS, "Choose Landscape Class", type=QgsProcessingParameterNumber.Integer, defaultValue=1))
        self.addOutput(QgsProcessingOutputNumber(
            self.OUTPUT, "Output effective mesh size"))
        
    def processAlgorithm(self, parameters, context, feedback):
        '''Here is where the processing itself takes place'''
        
        # Retrieve the values of the parameters entered by the user
        input = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        cl = self.parameterAsInt(parameters, self.CLASS, context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)        
                
        # Processing
        input_dpr = input.dataProvider()
        nodata = input_dpr.sourceNoDataValue(1)
        inputFilename = input.source()
        x_res = input.rasterUnitsPerPixelX() # Extract The X-Value
        y_res = input.rasterUnitsPerPixelY() # Extract The Y-Value
        pix_area = x_res * y_res
        feedback.pushDebugInfo("nodata = " + str(nodata))
        feedback.pushDebugInfo("Pixel area " + str(x_res) + " x " + str(y_res)
                                + " = " + str(pix_area))
        classes, array = qgsUtils.getRasterValsAndArray(str(inputFilename)) # get classes and array
        if cl not in classes:
            raise QgsProcessingException("Input layer has no cells with value " + str(cl))
        new_array = np.copy(array)
        feedback.pushDebugInfo("new_array = " + str(new_array))
        new_array[new_array!=cl] = 0
        new_array[array==cl] = 1
        feedback.pushDebugInfo("new_array = " + str(new_array))
        # 8-connexity ? TODO : investigate
        struct = scipy.ndimage.generate_binary_structure(2,2)
        labeled_array, nb_patches = scipy.ndimage.label(new_array,struct)
        feedback.pushDebugInfo("labeled_array = " + str(labeled_array))
        feedback.pushDebugInfo("nb_patches = " + str(nb_patches))
        if nb_patches == 0:
            feedback.reportError("No patches found",fatalError=True)

        res = []
        labels = list(range(1,nb_patches+1))
        feedback.pushDebugInfo("labels = " + str(labels))
        patches_len = scipy.ndimage.labeled_comprehension(new_array,labeled_array,labels,len,int,0)
        feedback.pushDebugInfo("patches_len = " + str(patches_len))
        
        sum_ai = 0
        sum_ai_sq = 0
        for patch_len in patches_len:
            ai = patch_len * pix_area
            sum_ai_sq += math.pow(ai,2)
            sum_ai += ai
        feedback.pushDebugInfo("sum_ai = " + str(sum_ai))
        feedback.pushDebugInfo("sum_ai_sq = " + str(sum_ai_sq))
        if sum_ai_sq == 0:
            feedback.reportError("Empty area for patches, please check your selection.")
        
        nb_pix = len(array[array != nodata])
        tot_area = nb_pix * pix_area
        #area_sq = math.pow(nb_pix,2)
        if nb_pix == 0:
            feedback.reportError("Unexpected error : empty area for input layer")
        
        res = float(sum_ai_sq) / float(tot_area)
        
        return {self.OUTPUT: res}

        
class MeffRasterCBC(QgsProcessingAlgorithm):

    ALG_NAME = "meffRasterCBC"
    
    INPUT = "INPUT"
    CLASS = "CLASS"
    REPORTING_LAYER = "REPORTING_LAYER"
    OUTPUT = "OUTPUT"
    OUTPUT_PATH = "OUTPUT_PATH"
        
    def createInstance(self):
        return MeffRasterCBC()
        
    def name(self):
        return self.ALG_NAME
        
    def displayName(self):
        return tr("Raster Effective Mesh Size (Cross-Boundary C)")
        
    def shortHelpString(self):
        return tr("Computes effective mesh size on a raster layer")

    def initAlgorithm(self, config=None):
        '''Here we define the inputs and output of the algorithm, along
        with some other properties'''
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT, "Input raster layer", optional=False))
        self.addParameter(QgsProcessingParameterNumber(
            self.CLASS, "Choose Landscape Class", type=QgsProcessingParameterNumber.Integer, defaultValue=1))
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.REPORTING_LAYER,
                description=tr("Reporting layer"),
                types=[QgsProcessing.TypeVectorPolygon],
                optional=True))
        self.addOutput(QgsProcessingOutputNumber(
            self.OUTPUT, "Output effective mesh size"))
        self.addOutput(QgsProcessingOutputRasterLayer(
            self.OUTPUT_PATH, "Output path"))
        
    def processAlgorithm(self, parameters, context, feedback):
        '''Here is where the processing itself takes place'''
        
        # Retrieve the values of the parameters entered by the user
        input = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        cl = self.parameterAsInt(parameters, self.CLASS, context)
        report_layer = self.parameterAsVectorLayer(parameters,self.REPORTING_LAYER,context)
        output = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)        
            
        # Processing
        input_dpr = input.dataProvider()
        nodata = input_dpr.sourceNoDataValue(1)
        inputFilename = input.source()
        x_res = input.rasterUnitsPerPixelX() # Extract The X-Value
        y_res = input.rasterUnitsPerPixelY() # Extract The Y-Value
        pix_area = x_res * y_res
        feedback.pushDebugInfo("nodata = " + str(nodata))
        feedback.pushDebugInfo("Pixel area " + str(x_res) + " x " + str(y_res)
                                + " = " + str(pix_area))
        classes, array = qgsUtils.getRasterValsAndArray(str(inputFilename)) # get classes and array
        if cl not in classes:
            raise QgsProcessingException("Input layer has no cells with value " + str(cl))
        new_array = np.copy(array)
        feedback.pushDebugInfo("new_array = " + str(new_array))
        new_array[new_array!=cl] = 0
        new_array[array==cl] = 1
        feedback.pushDebugInfo("new_array = " + str(new_array))
        # 8-connexity ? TODO : investigate
        struct = scipy.ndimage.generate_binary_structure(2,2)
        labeled_array, nb_patches = scipy.ndimage.label(new_array,struct)
        feedback.pushDebugInfo("labeled_array = " + str(labeled_array))
        feedback.pushDebugInfo("nb_patches = " + str(nb_patches))
        labels = list(range(1,nb_patches+1))
        labels_with_zero = list(range(0,nb_patches+1))
        feedback.pushDebugInfo("labels = " + str(labels))
        feedback.pushDebugInfo("labels_with_zero = " + str(labels_with_zero))        
        if nb_patches == 0:
            feedback.reportError("No patches found",fatalError=True)
        max_label = labels[-1]
        
        # Input clip
        if math.isnan(nodata):
            out_nodata = -1
            # type = 7 <=> Float32
            out_type = 7
        else:
            out_nodata = nodata
            # type = 0 <=> input data type
            out_type = 0
        input_clipped_path = QgsProcessingUtils.generateTempFilename("input_clipped.tif")
        input_clipped = qgsTreatments.clipRasterFromVector(inputFilename,report_layer,
            input_clipped_path,crop_cutline=False,nodata=out_nodata,
            data_type=out_type,context=context, feedback=feedback)
        input_classes, input_array = qgsUtils.getRasterValsAndArray(str(input_clipped_path))
        feedback.pushDebugInfo("input_array = " + str(input_array))
        if math.isnan(nodata):
            nodata = 0
        feedback.pushDebugInfo("nodata = " + str(out_nodata))
        nb_pix = len(input_array[input_array != out_nodata])
        feedback.pushDebugInfo("nb_pix = " + str(nb_pix))
        
        # Label clip
        labeled_path = QgsProcessingUtils.generateTempFilename("labeled.tif")
        clipped_path = QgsProcessingUtils.generateTempFilename("labeled_clipped.tif")
        if max_label < 256:
            label_out_type = gdal.GDT_Byte
        elif max_label < 65536:
            label_out_type = gdal.GDT_UInt16
        else:
            label_out_type = gdal.GDT_UInt32
        qgsUtils.exportRaster(labeled_array,inputFilename,labeled_path,
            nodata=0,type=label_out_type)
        clipped = qgsTreatments.clipRasterFromVector(labeled_path,report_layer,clipped_path,
            crop_cutline=False,context=context,feedback=feedback)
        clip_classes, clip_array = qgsUtils.getRasterValsAndArray(str(clipped_path))
        #clip_classes = labels
        feedback.pushDebugInfo("clip_classes = " + str(clip_classes))
        feedback.pushDebugInfo("clip_array = " + str(clip_array))
        # clip_array.astype(np.uint8)
        # feedback.pushDebugInfo("clip_array = " + str(clip_array))
        
        # dummy_type= np.dtype('O')
        # feedback.pushDebugInfo("dtype = " + str(dummy_type))
        
        feedback.pushDebugInfo("array size = " + str(array.size))
        feedback.pushDebugInfo("new_array size = " + str(new_array.size))
        feedback.pushDebugInfo("labeled_array size = " + str(labeled_array.size))
        feedback.pushDebugInfo("input_array size = " + str(input_array.size))
        feedback.pushDebugInfo("clip_array size = " + str(clip_array.size))
        patches_len = scipy.ndimage.labeled_comprehension(
            new_array,labeled_array,labels_with_zero,len,int,0)
        feedback.pushDebugInfo("patchess_len = " + str(patches_len))
        
        feedback.pushDebugInfo("na type = " + str(new_array.dtype))
        feedback.pushDebugInfo("la type = " + str(labeled_array.dtype))
        feedback.pushDebugInfo("ca type = " + str(clip_array.dtype))
        
        patches_len_clipped = scipy.ndimage.labeled_comprehension(
            new_array,clip_array,labels_with_zero,len,int,0)
        feedback.pushDebugInfo("patches_len_clipped = " + str(patches_len_clipped))
        
        # if 0 in clip_classes:
            # nb_nodata = patches_len_clipped[0]
            # patches_len_clipped = np.delete(patches_len_clipped,0)
        # else:
            # nb_nodata = 0
        # feedback.pushDebugInfo("clip_classes2 = " + str(clip_classes))
        
        sum_ai_sq = 0
        #feedback.pushDebugInfo("labels = " + str(labels))
        for cpt, lbl in enumerate(labels):
            lbl_val = int(lbl)
            feedback.pushDebugInfo("lbl_val = " + str(lbl_val))
            patch_len = patches_len[lbl_val]
            cbc_len = patches_len_clipped[cpt + 1]
            if patch_len != cbc_len:
                #feedback.pushDebugInfo("patch = " + str(patch))
                feedback.pushDebugInfo("patch_len = " + str(patch_len))
                #feedback.pushDebugInfo("patch_cbc = " + str(patch_cbc))
                feedback.pushDebugInfo("cbc_len = " + str(cbc_len))
            # Accumulators
            ai = patch_len * pix_area
            ai_cbc = cbc_len * pix_area
            sum_ai_sq += ai * ai_cbc
        feedback.pushDebugInfo("sum_ai_sq = " + str(sum_ai_sq))
            
        #nb_pix = len(clip_array[clip_array != nodata])
        #nb_pix = array.size - nb_nodata
        tot_area = nb_pix * pix_area
        feedback.pushDebugInfo("tot_area = " + str(tot_area))
        #area_sq = math.pow(nb_pix,2)
        if nb_pix == 0:
            feedback.reportError("Unexpected error : empty area for input layer")
        
        res = float(sum_ai_sq) / float(tot_area)
            
        #qgsUtils.loadRasterLayer(clipped_path,loadProject=True)
        #res = 0
        return {self.OUTPUT : res, self.OUTPUT_PATH : clipped_path}
            
            