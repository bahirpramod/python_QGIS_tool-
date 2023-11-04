# -*- coding: utf-8 -*-

"""
/***************************************************************************
 PTPTools
                                 A QGIS plugin
 Tools For PTP
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-03-08
        copyright            : (C) 2021 by Sibin Sarmadan
        email                : sibinsa@email.igenesys.com
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

__author__ = 'Sibin Sarmadan'
__date__ = '2021-03-08'
__copyright__ = '(C) 2021 by Sibin Sarmadan'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import *


class PTPTopologyCheckerV2Algorithm(QgsProcessingAlgorithm):
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
    RULE = 'RULE'
    TARGET = 'TARGET'

    rules = ['Must Be Covered By Boundary Of', 'Must Cover Each Other',
             'Must Be properly inside', 'Must Be Covered By End Point Of',
             'Must Be Covered By Feature Class Of', 'Must Be Inside', 'Must Not Overlap With', 'Must Overlap With'
        , 'Must Be Snapped To', 'Must Edge match with']

    polygonTypes = [QgsWkbTypes.Polygon, QgsWkbTypes.PolygonZ, QgsWkbTypes.PolygonZM,
                    QgsWkbTypes.MultiPolygon, QgsWkbTypes.MultiPolygonZ, QgsWkbTypes.MultiPolygonZM]

    lineTypes = [QgsWkbTypes.LineString, QgsWkbTypes.LineStringZ, QgsWkbTypes.LineStringZM,
                 QgsWkbTypes.MultiLineString, QgsWkbTypes.MultiLineStringZ, QgsWkbTypes.MultiLineStringZM]

    pointTypes = [QgsWkbTypes.Point, QgsWkbTypes.PointZ, QgsWkbTypes.PointZM,
                  QgsWkbTypes.MultiPoint, QgsWkbTypes.MultiPointZ, QgsWkbTypes.MultiPointZM]

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPoint, QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.RULE,
                self.tr('Topology Rule'),
                self.rules
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.TARGET,
                self.tr('Target layer'),
                [QgsProcessing.TypeVectorPoint, QgsProcessing.TypeVectorLine, QgsProcessing.TypeVectorPolygon]
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        sink = None
        dest_id = None

        rule = self.parameterAsEnum(parameters, self.RULE, context)
        # feedback.pushConsoleInfo('Rule :'+self.rules[rule])
        if rule == 0:
            (sink, dest_id) = self.mustBeCoveredByBoundaryOf(parameters, context, feedback)
            pass
        elif rule == 1:
            (sink, dest_id) = self.mustCoverEachOther(parameters, context, feedback)
            pass
        elif rule == 2:
            (sink, dest_id) = self.mustBeProperlyInside(parameters, context, feedback)
            pass
        elif rule == 3:
            (sink, dest_id) = self.mustBeCoveredByEndPointOf(parameters, context, feedback)
            pass
        elif rule == 4:
            (sink, dest_id) = self.mustBeCoveredByFeaturesOfClass(parameters, context, feedback)
            pass
        elif rule == 5:
            (sink, dest_id) = self.mustBeInside(parameters, context, feedback)
            pass
        elif rule == 6:
            (sink, dest_id) = self.mustNotOverlapWith(parameters, context, feedback)
            pass
        elif rule == 7:
            (sink, dest_id) = self.mustOverlapWith(parameters, context, feedback)
            pass
        elif rule == 8:
            (sink, dest_id) = self.mustBeSnappedTo(parameters, context, feedback)
            pass
        elif rule == 9:
            (sink, dest_id) = self.mustEdgematchwith(parameters, context, feedback)
            pass

        # Return the results of the algorithm. In this case our only result is
        # the feature sink which contains the processed features, but some
        # algorithms may return multiple feature sinks, calculated numeric
        # statistics, etc. These should all be included in the returned
        # dictionary, with keys matching the feature corresponding parameter
        # or output names.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'topology_checker_v2'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return 'Topology Checker V2'

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
        return 'Geometry Analysis'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PTPTopologyCheckerV2Algorithm()

    def mustBeInside(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)
        if target.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Target Layer')
            return (None, None)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "contains(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            flag = 0
            if feature.geometry().isEmpty():
                continue
            geom_wkt = feature.geometry().asWkt()
            req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                if feat.geometry().contains(feature.geometry()):
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustBeCoveredByEndPointOf(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)

        if source.wkbType() not in self.pointTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Point type Source Layer')
            return (None, None)

        if target.wkbType() not in self.lineTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Line type Target Layer')
            return (None, None)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = " intersects( start_point(  $geometry ), geom_from_wkt( '{geom}')) OR intersects( end_point(  $geometry ), geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            # req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            req = QgsFeatureRequest(feature.geometry().boundingBox())

            self.dist = 0.0001
            da = QgsDistanceArea()
            da.setSourceCrs(QgsCoordinateReferenceSystem(3857), QgsCoordinateTransformContext())
            if source.sourceCrs().authid() not in (3857, '3857'):
                self.dist = da.convertLengthMeasurement(self.dist, source.sourceCrs().mapUnits())

            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                geom = feat.geometry()
                d = geom.length()
                start_point = geom.interpolate(0)
                # feedback.pushConsoleInfo(str(start_point))
                end_point = geom.interpolate(d)
                # feedback.pushConsoleInfo(str(end_point))
                if feature.geometry().intersects(start_point) or feature.geometry().intersects(end_point) or \
                        feature.geometry().distance(start_point) <= self.dist or feature.geometry().distance(
                    end_point) <= self.dist:
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustBeCoveredByFeaturesOfClass(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)

        if source.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Source Layer')
            return (None, None)

        if target.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Target Layer')
            return (None, None)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "contains(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                if feat.geometry().contains(feature.geometry()):
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustBeProperlyInside(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)

        if source.wkbType() not in self.pointTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Point type Source Layer')
            return (None, None)

        if target.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Target Layer')
            return (None, None)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "contains(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                if feat.geometry().contains(feature.geometry()):
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustBeCoveredByBoundaryOf(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)

        if source.wkbType() not in self.lineTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Line type Source Layer')
            return (None, None)

        if target.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Target Layer')
            return (None, None)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "contains(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                if feat.geometry().contains(feature.geometry()):
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustCoverEachOther(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)

        if source.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Source Layer')
            return (None, None)

        if target.wkbType() not in self.polygonTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Target Layer')
            return (None, None)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "intersects(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            # print(exp.format(geom=geom_wkt))
            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                # print(feat.id())
                # print(feat.geometry().within(feature.geometry()))
                if feat.geometry().within(feature.geometry()):
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustNotOverlapWith(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "overlaps(  $geometry , geom_from_wkt( '{geom}')) or crosses(  $geometry , geom_from_wkt( '{geom}')) " \
              " or contains(  $geometry , geom_from_wkt( '{geom}')) or within(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            # feedback.pushConsoleInfo('Expression  :' + exp.format(geom=geom_wkt))
            # req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            req = QgsFeatureRequest(feature.geometry().boundingBox())
            for feat in target.getFeatures(req):
                # print(feature.id(),feat.id(),feat.geometry().overlaps(feature.geometry()))
                if feedback.isCanceled():
                    break
                    pass
                # feedback.pushConsoleInfo('Geom1 :' + feature.geometry().asWkt())
                # feedback.pushConsoleInfo('Geom2 :' + feat.geometry().asWkt())
                # feedback.pushConsoleInfo('Geom1 overlaps  Geom2 :' + str(feature.geometry().overlaps(feat.geometry())))
                # feedback.pushConsoleInfo('Geom2 overlaps  Geom1 :' + str(feat.geometry().overlaps(feature.geometry())))
                if feat.geometry().overlaps(feature.geometry()):
                    flag = 1
                    break
                elif feature.geometry().crosses(feat.geometry()):
                    flag = 1
                    break
                elif feature.geometry().contains(feat.geometry()):
                    flag = 1
                    break
                elif feature.geometry().within(feat.geometry()):
                    flag = 1
                    break
                elif feature.geometry().isGeosEqual(feat.geometry()):
                    flag = 1
                    break
                else:
                    # feedback.pushConsoleInfo('Geom1 :' + feature.geometry().asWkt())
                    # feedback.pushConsoleInfo('Geom2 :' + feat.geometry().asWkt())
                    pass
                pass
            if flag == 1:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustOverlapWith(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = "overlaps(  $geometry , geom_from_wkt( '{geom}')) or crosses(  $geometry , geom_from_wkt( '{geom}')) " \
              " or contains(  $geometry , geom_from_wkt( '{geom}')) or within(  $geometry , geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            # feedback.pushConsoleInfo('Expression  :' + exp.format(geom=geom_wkt))
            # req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            req = QgsFeatureRequest(feature.geometry().boundingBox())
            for feat in target.getFeatures(req):
                # print(feature.id(),feat.id(),feat.geometry().overlaps(feature.geometry()))
                if feedback.isCanceled():
                    break
                    pass
                # feedback.pushConsoleInfo('Geom1 :' + feature.geometry().asWkt())
                # feedback.pushConsoleInfo('Geom2 :' + feat.geometry().asWkt())
                # feedback.pushConsoleInfo('Geom1 overlaps  Geom2 :' + str(feature.geometry().overlaps(feat.geometry())))
                # feedback.pushConsoleInfo('Geom2 overlaps  Geom1 :' + str(feat.geometry().overlaps(feature.geometry())))
                if feat.geometry().overlaps(feature.geometry()):
                    flag = 1
                    break
                elif feature.geometry().crosses(feat.geometry()):
                    flag = 1
                    break
                elif feature.geometry().contains(feat.geometry()):
                    flag = 1
                    break
                elif feature.geometry().within(feat.geometry()):
                    flag = 1
                    break
                elif feature.geometry().isGeosEqual(feat.geometry()):
                    flag = 1
                    break
                else:
                    # feedback.pushConsoleInfo('Geom1 :' + feature.geometry().asWkt())
                    # feedback.pushConsoleInfo('Geom2 :' + feat.geometry().asWkt())
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustBeSnappedTo(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)

        if source.wkbType() not in self.pointTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Point type Source Layer')
            return (None, None)

        if target.wkbType() not in self.lineTypes:
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Line type Target Layer')
            return (None, None)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        exp = " intersects( start_point(  $geometry ), geom_from_wkt( '{geom}')) OR intersects( end_point(  $geometry ), geom_from_wkt( '{geom}'))"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            geom_wkt = feature.geometry().asWkt()
            # req = QgsFeatureRequest().setFilterExpression(exp.format(geom=geom_wkt))
            req = QgsFeatureRequest(feature.geometry().boundingBox())

            self.dist = 0.5
            da = QgsDistanceArea()
            da.setSourceCrs(QgsCoordinateReferenceSystem(3857), QgsCoordinateTransformContext())
            if source.sourceCrs().authid() not in (3857, '3857'):
                self.dist = da.convertLengthMeasurement(self.dist, source.sourceCrs().mapUnits())

            for feat in target.getFeatures(req):
                if feedback.isCanceled():
                    break
                    pass
                geom = feat.geometry()
                d = geom.length()
                start_point = geom.interpolate(0)
                # feedback.pushConsoleInfo(str(start_point))
                end_point = geom.interpolate(d)
                # feedback.pushConsoleInfo(str(end_point))
                if feature.geometry().intersects(geom) or \
                        feature.geometry().distance(geom) <= self.dist:
                    flag = 1
                    break
                    pass
                pass
            if flag == 0:
                sink.addFeature(feature, QgsFeatureSink.FastInsert)
                pass
            feedback.setProgress(int(current * total))
            pass
        return (sink, dest_id)
        pass

    def mustEdgematchwith(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        target = self.parameterAsSource(parameters, self.TARGET, context)
        # bufferdistance = self.parameterAsDouble(parameters, self.INPUT_BUFFERDIST,context)
        if (target.wkbType() not in self.polygonTypes) and (target.wkbType() not in self.lineTypes):
            # feedback.pushConsoleInfo(str(source.wkbType()))
            feedback.pushConsoleInfo('Requires Polygon type Target Layer')
            return (None, None)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                                               context, source.fields(), source.wkbType(), source.sourceCrs())
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        bufferFeature = QgsFeature(source.fields())
        exp = "buffer($geometry, distance[, segments=8])"
        for current, feature in enumerate(features):
            if feedback.isCanceled():
                break
                pass
            if feature.geometry().isEmpty():
                continue
            flag = 0
            self.dist = 0.5
            da = QgsDistanceArea()
            da.setSourceCrs(QgsCoordinateReferenceSystem(3857), QgsCoordinateTransformContext())
            if source.sourceCrs().authid() not in (3857, '3857'):
                self.dist = da.convertLengthMeasurement(self.dist, source.sourceCrs().mapUnits())
            geom = feature.geometry()
            buffer = geom.buffer(self.dist, 8)
            bufferFeature.setGeometry(geom)
            bb = QgsFeatureRequest(buffer.boundingBox())
            refFeatures = target.getFeatures(bb)
            for refFeature in refFeatures:
                if (feature.id() != refFeature.id()) and (feature.id() < refFeature.id()):
                #if feature["sub_class"] == refFeature["sub_class"] and (feature.id() != refFeature.id()) and (feature.id() < refFeature.id()):
                    if feature.geometry().distance(refFeature.geometry()) <= self.dist:
                        if feature.geometry().intersects(refFeature.geometry()) and bufferFeature.geometry().intersects(
                                refFeature.geometry()):
                            pass
                        else:
                            sink.addFeature(feature, QgsFeatureSink.FastInsert)
        feedback.setProgress(int(current * total))
        return (sink, dest_id)
