from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *


class Snap_Features:
    def __init__(self, parent,layer =None):
        self.parent = parent
        self.memoryLayer = None
        self.layer = layer
        self.QgsSpatialIndex = QgsSpatialIndex()
        self.List_snap_point = []
        self.List_fids = []
        self.onSelection = True
    
    def findSnapPoints(self):
        self.reSet()
        self.feature_toPoint()
        return self.getSnapPoints()
    def fixSnapissue_old(self,onSelection = True):
        self.onSelection =onSelection 
        self.reSet()
        self.feature_toPoint()
        self.getSnapPoints()
        for snapobj in self.List_snap_point:
            #snapobj.point = None
            for snapFeat in snapobj.List_Features:
                tempFeature = self.layer.getFeatures(QgsFeatureRequest().setFilterFid( snapFeat.fID))
                for feat in tempFeature:
                    geom = feat.geometry()
                    if snapobj.point is None:
                        snapobj.point =  geom.vertexAt(snapFeat.vrtx_index)
                        break
                    #geom.moveVertex(QgsPoint (snapobj.point),snapFeat.vrtx_index)
                    geom.moveVertex(snapobj.point.x(),snapobj.point.y() ,snapFeat.vrtx_index)
                    self.layer.changeGeometry(feat.id(),geom)
    def fixSnapissue(self,onSelection = True):
        self.onSelection =onSelection 
        self.reSet()
        self.feature_toPoint()
        self.getSnapPoints()
        cleanlist = []
        [cleanlist.append(x) for x in self.List_fids if x not in cleanlist]
        for fids in cleanlist:
            flg = False
            QgsMessageLog.logMessage( "Snapping for " + str(fids), "SnapPoints",Qgis.Info)
            tempFeature = self.layer.getFeatures(QgsFeatureRequest().setFilterFid( fids))
            geom = None
            for feat in tempFeature:
                geom = feat.geometry()
            if geom is not None: 
                for snapobj in self.List_snap_point:
                    for snapFeat in snapobj.List_Features:
                        #tempFeature = self.layer.getFeatures(QgsFeatureRequest().setFilterFid( snapFeat.fID))
                        if snapFeat.fID == fids:
                        #geom.moveVertex(QgsPoint (snapobj.point),snapFeat.vrtx_index)
                            QgsMessageLog.logMessage( "Snapping Point Vertex " + str(snapFeat.vrtx_index), "SnapPoints",Qgis.Info)
                            geom.moveVertex(snapobj.point.x(),snapobj.point.y() ,snapFeat.vrtx_index)
                            flg = True
                                
                if flg == True:
                    self.layer.changeGeometry(fids,geom)
                    QgsMessageLog.logMessage( "changeGeometry", "SnapPoints",Qgis.Info)

    def vector_layer_add_in_memory (self,LayerName, GeoType):
        if GeoType.upper() ==  "POINT":
            GeoType = "Point"
        elif GeoType.upper() ==  "LINE" or GeoType.upper() ==  "POLYLINE":
            GeoType =  "LineString"
        elif GeoType.upper() == "POLYGON":
            GeoType = "Polygon"
        uri = GeoType + "?crs=epsg:4326&field=id:integer&index=yes"
        vl = QgsVectorLayer(uri, LayerName, "memory")
        vl.startEditing()
        layerData = vl.dataProvider()
        layerData.addAttributes([ QgsField("FOID", QVariant.String),QgsField("vindex", QVariant.String)])
        vl.commitChanges()
        return vl
    
    def feature_toPoint(self):
        self.memoryLayer = self.vector_layer_add_in_memory('point','POINT')
        list_PointsFeatures = []
        fcnt = 1
        features = self.layer.selectedFeatures()
        for f in features:
            geom = f.geometry()
            p = geom.vertexAt(0)
            n   = 0
            while(p != QgsPoint(0,0)): 
                new_feat = QgsFeature() 
                new_feat.setAttributes([fcnt,f.id(),n]) 
                new_feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(p)))
                list_PointsFeatures.append(new_feat)
                fcnt+=1
                n +=1
                p=geom.vertexAt(n)
        prov = self.memoryLayer.dataProvider()
        prov.addFeatures(list_PointsFeatures)
        self.memoryLayer.updateExtents()
    def getSnapPoints(self ):
        self.QgsSpatialIndex = QgsSpatialIndex()
        for f in self.memoryLayer.getFeatures():
            self.QgsSpatialIndex.insertFeature(f)
        for f in self.memoryLayer.getFeatures():
            #print f.id()
            r =0.00000005
            p = f.geometry().asPoint ()
            point_buffer = QgsGeometry.fromPolyline([QgsPoint(p.x()+r,p.y()),
                                                    QgsPoint(p.x(),p.y()+r),
                                                    QgsPoint(p.x()-r,p.y()),
                                                    QgsPoint(p.x(),p.y()-r),
                                                    QgsPoint(p.x()+r,p.y())])
            point_buffer = QgsRectangle(p.x()-r,p.y()-r,p.x()+r,p.y()+r)
            #pnt = f.geometry().asPoint ()
            result_ids =self.QgsSpatialIndex.intersects(point_buffer)
            if len(result_ids)>1:
                QgsMessageLog.logMessage( "Fined Point", "SnapPoints",Qgis.Info)
                mSnap_point = Snap_point(p)
                for fid in result_ids:
                    tempFeature = self.memoryLayer.getFeatures(QgsFeatureRequest().setFilterFid( fid))
                    for feat in tempFeature:
                        self.List_fids.append(feat.attribute('FOID'))
                        mSnap_point.List_Features.append(Snap_Feature(feat.attribute('FOID'),feat.attribute('vindex')))
                self.List_snap_point.append(mSnap_point)
        return self.List_snap_point
    def reSet(self):
        self.memoryLayer = None
        self.QgsSpatialIndex = QgsSpatialIndex()
        self.List_snap_point = []
class Snap_point:
    def __init__(self, Point):        
        self.point = Point
        self.List_Features = []
class Snap_Feature:
    def __init__(self ,fID =None ,vrtx_index =None ):
        self.fID = fID
        self.vrtx_index = vrtx_index
