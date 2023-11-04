# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Clipper
                                 A QGIS plugin
 Clips features using polygon features of a layer
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-06-27
        copyright            : (C) 2019 by Genesys
        email                : mumbai@igenesys.com
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

__author__ = 'Genesys'
__date__ = '2019-06-27'
__copyright__ = '(C) 2019 by Genesys'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from shapely.wkt import loads
from shapely.geometry import LineString, MultiLineString, Polygon, MultiPolygon
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
from collections import deque
from PyQt5.QtCore import QCoreApplication
from processing.gui.wrappers import WidgetWrapper
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)


class FeatureCopyPasteAlgo(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    DESTINATION="DESTINATION"

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        input=QgsProcessingParameterVectorLayer(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        input.setMetadata({
            'widget_wrapper': {
                'class': MultipleVectorLayer}})
        self.addParameter(input)
        destination=QgsProcessingParameterVectorLayer(
                self.DESTINATION,
                self.tr('Destination Layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        destination.setMetadata({
            'widget_wrapper': {
                'class': MultipleVectorLayer}})
        self.addParameter(
            destination
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        destination = self.parameterAsVectorLayer(parameters, self.DESTINATION, context)
        # (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
        #         context, source.fields(), source.wkbType(), source.sourceCrs())
        if source.geometryType() != destination.geometryType():
            feedback.reportError('Source Geometry Type Does not Match With Destination Geometry Type ',True)
            feedback.cancel()
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.selectedFeatures()
        if len(features)<=0:
            feedback.reportError('Please Select the Features',True)
            feedback.cancel()

        destination.startEditing()
        if destination.isEditable() == False:
            feedback.reportError('Destination Layer Is Not Editable', True)
            feedback.cancel()
        source_fields=source.fields()
        destination_fields=[f for f in destination.fields()]
        source_index=[]
        destin_fld_ind=[]
        for field in source_fields:
            # print("field", field.typeName())
            field_name=field.name()
            source_field_name=field_name.lower()
            for fld in destination_fields:
                # print("fld",fld.typeName())
                fld_name=fld.name()
                desti_fld_name=fld_name.lower()
                if source_field_name==desti_fld_name :
                    field_index = source.fields().indexFromName(field.name())
                    source_index.append(field_index)
                    field_index1 = destination.fields().indexFromName(fld.name())
                    destin_fld_ind.append(field_index1)
                    pass
        primary_key_dest=destination.primaryKeyAttributes()
        if str(destination.dataProvider().name()).lower() == 'ogr':
            for fld in destination_fields:
                i=destination.fields().indexFromName(fld.name())
                if destination.dataProvider().defaultValueClause(i)=='Autogenerate':
                    field_index1 = destination.fields().indexFromName(fld.name())
                    primary_key_dest.append(field_index1)
                    pass
                pass
            pass
        # self.featList_desti = list(filter(lambda x: x not in primary_key_dest, destin_fld_ind))
        # self.featList_sou = list(filter(lambda x: x not in primary_key_dest, source_index))
        # print("self.featList_desti",self.featList_desti)
        # print("self.featList_sou",self.featList_sou)
        feat=QgsFeature()
        destination.beginEditCommand(u"Assign UUID")
        for current, feature in enumerate(features):
            att=feature.attributes()
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            # Add a feature in the sink
            geom=feature.geometry()
            #geom = self.shortSegment(geom).makeValid()
            if geom.wkbType() not in [QgsWkbTypes.Point,QgsWkbTypes.LineString,QgsWkbTypes.Polygon,QgsWkbTypes.MultiPoint,QgsWkbTypes.MultiLineString,QgsWkbTypes.MultiPolygon,
                                      QgsWkbTypes.NoGeometry,QgsWkbTypes.PointZ,QgsWkbTypes.LineStringZ,QgsWkbTypes.PolygonZ,QgsWkbTypes.MultiPointZ,QgsWkbTypes.MultiLineStringZ,QgsWkbTypes.MultiPolygonZ,
                                      QgsWkbTypes.PointM,QgsWkbTypes.LineStringM,QgsWkbTypes.PolygonM,QgsWkbTypes.MultiPointM,QgsWkbTypes.MultiLineStringM,QgsWkbTypes.MultiPolygonM,
                                      QgsWkbTypes.PointZM,QgsWkbTypes.LineStringZM,QgsWkbTypes.PolygonZM,QgsWkbTypes.MultiPointZM,QgsWkbTypes.MultiLineStringZM,QgsWkbTypes.MultiPolygonZM,
                                      QgsWkbTypes.Point25D,QgsWkbTypes.LineString25D,QgsWkbTypes.Polygon25D,QgsWkbTypes.MultiPoint25D,QgsWkbTypes.MultiLineString25D,QgsWkbTypes.MultiPolygon25D]:
                geom1=geom.asGeometryCollection()
                geoms = []
                for geo in geom1:
                    geom1 = geo.get()
                    geom2 = geom1.segmentize(0.001, QgsAbstractGeometry.MaximumDifference)
                    geoms.append(QgsGeometry(geom2))
                geom = QgsGeometry.unaryUnion(geoms)
                pass
            if geom.wkbType()!=destination.wkbType():
                geom1 = geom.get()
                # if destination.wkbType() in [QgsWkbTypes.Point,QgsWkbTypes.LineString,QgsWkbTypes.Polygon,QgsWkbTypes.MultiPoint,QgsWkbTypes.MultiLineString,QgsWkbTypes.MultiPolygon,QgsWkbTypes.NoGeometry,
                #                               QgsWkbTypes.PointM,QgsWkbTypes.LineStringM,QgsWkbTypes.PolygonM,QgsWkbTypes.MultiPointM,QgsWkbTypes.MultiLineStringM,QgsWkbTypes.MultiPolygonM,
                #                               QgsWkbTypes.NoGeometry,QgsWkbTypes.PointZ,QgsWkbTypes.LineStringZ,QgsWkbTypes.PolygonZ,QgsWkbTypes.MultiPointZ,QgsWkbTypes.MultiLineStringZ,QgsWkbTypes.MultiPolygonZ,
                #                               QgsWkbTypes.PointZM,QgsWkbTypes.LineStringZM,QgsWkbTypes.PolygonZM,QgsWkbTypes.MultiPointZM,QgsWkbTypes.MultiLineStringZM,QgsWkbTypes.MultiPolygonZM]:
                #     print("hi")
                #     geom1.dropZValue()
                #     geom1.dropMValue()
                if geom1.is3D() and geom1.isMeasure()==False and destination.wkbType() in [QgsWkbTypes.Point,QgsWkbTypes.LineString,QgsWkbTypes.Polygon,QgsWkbTypes.MultiPoint,QgsWkbTypes.MultiLineString,QgsWkbTypes.MultiPolygon,
                                     QgsWkbTypes.PointM,QgsWkbTypes.LineStringM,QgsWkbTypes.PolygonM,QgsWkbTypes.MultiPointM,QgsWkbTypes.MultiLineStringM,QgsWkbTypes.MultiPolygonM]:
                    geom1.dropZValue()
                    pass
                elif geom1.is3D()==False and geom1.isMeasure() and destination.wkbType() in [QgsWkbTypes.Point,QgsWkbTypes.LineString,QgsWkbTypes.Polygon,QgsWkbTypes.MultiPoint,QgsWkbTypes.MultiLineString,QgsWkbTypes.MultiPolygon,
                                      QgsWkbTypes.NoGeometry,QgsWkbTypes.PointZ,QgsWkbTypes.LineStringZ,QgsWkbTypes.PolygonZ,QgsWkbTypes.MultiPointZ,QgsWkbTypes.MultiLineStringZ,QgsWkbTypes.MultiPolygonZ]:
                    geom1.dropMValue()
                    pass
                elif geom1.is3D() and geom1.isMeasure() and destination.wkbType() in [QgsWkbTypes.Point,QgsWkbTypes.LineString,QgsWkbTypes.Polygon,QgsWkbTypes.MultiPoint,QgsWkbTypes.MultiLineString,QgsWkbTypes.MultiPolygon]:
                    geom1.dropZValue()
                    geom1.dropMValue()
                    pass
                elif geom1.is3D() and geom1.isMeasure() and destination.wkbType() in [QgsWkbTypes.PointZ,QgsWkbTypes.LineStringZ,QgsWkbTypes.PolygonZ,QgsWkbTypes.MultiPointZ,QgsWkbTypes.MultiLineStringZ,QgsWkbTypes.MultiPolygonZ]:
                    geom1.dropMValue()
                    pass
                elif geom1.is3D() and geom1.isMeasure() and destination.wkbType() in [QgsWkbTypes.PointM,QgsWkbTypes.LineStringM,QgsWkbTypes.PolygonM,QgsWkbTypes.MultiPointM,QgsWkbTypes.MultiLineStringM,QgsWkbTypes.MultiPolygonM]:
                    geom1.dropZValue()
                    pass

                geom =QgsGeometry.fromWkt(geom1.asWkt())
                pass
            feat.setGeometry(geom)
            feat.initAttributes(len(destination_fields))
            i=0
            for idx1 in source_index:
                at=att[idx1]
                fld_name=destin_fld_ind[i]
                if fld_name in primary_key_dest:
                    i += 1
                    continue
                feat.setAttribute(fld_name, at)
                i+=1
            destination.addFeature(feat)
            feedback.setProgress(int(current * total))
        destination.endEditCommand()
        destination.triggerRepaint()

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'feature_copy_paste'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Feature Copy and Paste')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return None

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return FeatureCopyPasteAlgo()

class MultipleVectorLayer(WidgetWrapper):
    # print("Hello")
    def createWidget(self):
        self._combo = QgsMapLayerComboBox()
        self.refreshLayers()
        QgsProject.instance().layersAdded.connect(self.refreshLayers)
        QgsProject.instance().layersRemoved.connect(self.refreshLayers)
        return self._combo

    def value(self):
        layer=self._combo.currentLayer()
        if layer==None:
            return None
        return layer.source()

    def refreshLayers(self):
        self.layers = [layer for layer in QgsProject.instance().layerStore().mapLayers().values()]
        if len(self.layers) == 0 and self.show:
            self.dlg.done(1)
            return False
            pass
        polygon_layers = []
        layers = []
        for layer in self.layers:
            if layer.type() != QgsMapLayer.VectorLayer:
                polygon_layers.append(layer)
                continue
            if layer.geometryType() not in [QgsWkbTypes.PointGeometry,QgsWkbTypes.LineGeometry,
                                            QgsWkbTypes.PolygonGeometry,QgsWkbTypes.UnknownGeometry]:
                polygon_layers.append(layer)
                pass
        self._combo.setExceptedLayerList(polygon_layers)
        if len(self.layers) == len(polygon_layers):
            return False
            pass
        return True
        pass
