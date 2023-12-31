# -*- coding: utf-8 -*-
"""
/***************************************************************************
 NNG_road_network_Tool
                                 A QGIS plugin
 NNG_road_network_Tool
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-11-02
        git sha              : $Format:%H$
        copyright            : (C) 2023 by genesys
        email                : pramoddb@email.igenesys.com
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
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *
from qgis.utils import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from qgis.core import *
from qgis.gui import *
from collections import *
import sys
from math import sqrt
import itertools
# from qgis import processing
import processing
import math
from math import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .NNG_road_network_Tool_dialog import NNG_road_network_ToolDialog
import os.path


class NNG_road_network_Tool:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'NNG_road_network_Tool_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&NNG_road_network_Tool')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('NNG_road_network_Tool', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/NNG_road_network_Tool/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'NNG_road_network_Tool'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&NNG_road_network_Tool'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = NNG_road_network_ToolDialog()
            # self.dlg.Cancel.clicked.connect(self.close)
            self.dlg.Ok.clicked.connect(self.getvertex)

        # show the dialog
        self.dlg.show()
        self.addlayers()
        self.dlg.progressBar.setValue(0)
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
    def close(self):
        self.dlg.close()
        

    def addlayers(self):
        self.layer=QgsProject.instance().mapLayers().values()
        self.dlg.comboBox.clear()
        self.dlg.comboBox_2.clear()
        self.dlg.comboBox.addItems([layer.name() for layer in self.layer]) 
        self.dlg.comboBox_2.addItems([layer.name() for layer in self.layer]) 
    
    def getvertex(self):
        self.current_layer = self.dlg.comboBox.currentText()
        # print('txt')
        for lyr in self.layer:
            layers_name = lyr.name()
            if self.current_layer == layers_name:
                # print("layers_name",layers_name)
                self.input_layer = lyr
        count = self.input_layer.selectedFeatureCount()
        if count <= 0:
                QMessageBox.information(self.dlg, "Info",
                                        " Please select the features")
                return
        MANEUVERS_layer = self.dlg.comboBox_2.currentText()
        # print('txt')MANEUVERS_sample
        for lyr in self.layer:
            layers_name = lyr.name()
            if MANEUVERS_layer == layers_name:
                # print("layers_name",layers_name)
                self.MANEUVERS_layer = lyr
                self.MANEUVERS_layer.startEditing()

        self.errorPointFeatures = []
        self.MANEUVERSFeatures = []
        uri = "LineString?crs=" + self.input_layer.crs().authid()
        vMemorylayer2 = QgsVectorLayer(uri, "MANEUVERS_LINE", "memory")
        vMemorylayer2.startEditing()
        layerData2 = vMemorylayer2.dataProvider()
        layerData2.addAttributes([ QgsField("F_EDGE", QVariant.String), QgsField("JUCTION", QVariant.String), QgsField("T_EDGE", QVariant.String)])
        dctErrPnts2 = defaultdict()
      
        uri = "Point?crs=" + self.input_layer.crs().authid()
        vMemorylayer = QgsVectorLayer(uri, "Rail line Error", "memory")
        vMemorylayer.startEditing()
        layerData = vMemorylayer.dataProvider()
        layerData.addAttributes([QgsField("Fid", QVariant.String), QgsField("layer name", QVariant.String), QgsField("Error name", QVariant.String)])
        dctErrPnts = defaultdict()
        dctErrPnts2 = defaultdict()
        vertex_list=[]
        prg = 0
        fid=1
        
        for feature in self.input_layer.selectedFeatures():
            # lyr.startEditing()
            # self.dlg.progressBar.setValue(0)
            percent = prg / float(count) * 100
            self.dlg.progressBar.setValue(percent)
            prg += 1
            geom=feature.geometry()
            if geom.wkbType() in [QgsWkbTypes.MultiLineString ]:
                vertex_list=geom.asMultiPolyline()[0]
            else:
                vertex_list=geom.asPolyline()

        
            Fst_last_vertex=[]
            a=vertex_list[0]
            # Fst_last_vertex.append(a)
            b=vertex_list[-1]
            c=vertex_list[-2]
            Fst_last_vertex.append(b)
            # print("Fst_last_vertex",Fst_last_vertex)
            az=b.azimuth(vertex_list[-2])
            az0=c.azimuth(b)
         
            for vertex in Fst_last_vertex:
                    point_geom= QgsGeometry.fromPointXY(QgsPointXY(vertex))
                    # print("point_geom",point_geom)
                    self.buffer=point_geom.buffer(0.0000005,5)
                    # print("self.buffer",self.buffer)
                    bbox=self.buffer.boundingBox()
                    intersectFeats = [f for f in self.input_layer.getFeatures(QgsFeatureRequest(bbox))]
                    geom_list2=[]
                    T_JUNC_ver_list=[]
                    for feat in intersectFeats:
                        geom=feat.geometry()
                        if geom.wkbType() in [QgsWkbTypes.MultiLineString ]:
                            T_JUNC_ver=geom.asMultiPolyline()[0]
                        else:
                            T_JUNC_ver=geom.asPolyline()
                        f_T_JUNC_ver=(T_JUNC_ver[0])
                        s_T_JUNC_ver=(T_JUNC_ver[1])
                        az1=f_T_JUNC_ver.azimuth(s_T_JUNC_ver)
                        angle=self.get_azimuth(az0,az1 )
                        # print("az0",az0)
                        # print("az",az)
                        # print("az1",az1)
                        # print("az-az1",az-az1)
                        if feat.id()!=feature.id():
                            if feature['T_JUNC'] == feat['F_JUNC'] and angle<165:
                                # print("intersectFeats",len(intersectFeats))
                                # geom_list2.append(feat)
                                # print("geom_list2 ff ",geom_list2)
                                if feat.geometry().intersects(feature.geometry()):
                                    if vertex==f_T_JUNC_ver :
                                        # print("vertex",vertex)
                                        # print("f_T_JUNC_ver",f_T_JUNC_ver)
                                        # dctErrPnts[prg] = [ point_geom, self.input_layer.name(),"before_point"]
                                        az=b.azimuth(vertex_list[-2])
                                        before_point=b.project(0.00005,az)
                                        nearDist, queryPnt1, aftVtx1, segDirect = geom.closestSegmentWithContext(before_point)
                                        if queryPnt1 :
                                            nearest_point= QgsGeometry.fromPointXY(QgsPointXY(queryPnt1))
                                            point_geom1 = feature.geometry().nearestPoint(nearest_point)
                                            # dctErrPnts[prg+1] = [ point_geom1, self.input_layer.name(),"before_point"] 
                                        
                                        next_point=b.project(0.00005,az1)
                                        nearDist, queryPnt2, aftVtx1, segDirect = geom.closestSegmentWithContext(next_point)
                                        if queryPnt2 :
                                            # point_geom2= QgsGeometry.fromPointXY(QgsPointXY(queryPnt2))
                                            nearest_point= QgsGeometry.fromPointXY(QgsPointXY(queryPnt2))
                                            point_geom2 = feat.geometry().nearestPoint(nearest_point)
                                            # dctErrPnts[prg+2] = [ point_geom2, self.input_layer.name(),"before_point"]
                                        # print("az",az)
                                        queryPnt12=point_geom1.asPoint()
                                        queryPnt22=point_geom2.asPoint()
                                        new_x = queryPnt12.x() + queryPnt22.x() - vertex.x()
                                        new_y = queryPnt12.y() + queryPnt22.y() - vertex.y()
                                        point_geom3=QgsPointXY(new_x, new_y)
                                        point_geom4= QgsGeometry.fromPointXY(QgsPointXY(point_geom3))
                                        # dctErrPnts[prg+3] = [ point_geom4, self.input_layer.name(),"before_point"]
                                        if angle<105 and angle >75:
                                            # print("hghkf")
                                            dctErrPnts2[fid] = [ point_geom1,point_geom4,feature["ID_1"],feature['T_JUNC'],feat['ID_1'],1]
                                        else:
                                            
                                            dctErrPnts2[fid] = [ point_geom1,point_geom4,feature["ID_1"],feature['T_JUNC'],feat['ID_1'],2]
                                        fid+=1
                                        # dctErrPnts2[feature["ID_1"]] = [ point_geom1,point_geom4,feature['T_JUNC'],feat['ID_1']]
                                        # fid+=1
                                        # self.drawLine(point_geom1,point_geom4)
                                        # print("point_geom1",point_geom1)
                                        # print("point_geom4",point_geom4)
                                        

        for ids, feats in dctErrPnts2.items():  # pntGeom = QgsGeometry().fromPointXY(iter[0])
            # print("dctErrPnts2",dctErrPnts2)
            # print("ids",ids)
            # print('feats',feats)
            # attrList=self.updateMANEUVERSFeatures([ids, feats[2],feats[3]], feats[0],feats[1])
            attrList=self.updateMANEUVERSFeatures([ids, 'Null',1,feats[2],feats[3],feats[4],feats[5]], feats[0],feats[1])
        if len(dctErrPnts2) > 0:
            # print("self.MANEUVERSFeatures",len(self.MANEUVERSFeatures))
            v_layer= self.MANEUVERS_layer
            # v_layer= vMemorylayer2
            # QgsProject.instance().addMapLayer(v_layer)
            QgsProject.instance().addMapLayer(v_layer)
            layerData2 = v_layer.dataProvider()
            layerData2.addFeatures(self.MANEUVERSFeatures)
            v_layer.updateExtents()
            v_layer.commitChanges()
            self.update_atrri(attrList)
            
            QMessageBox.information(None, 'Done', 'Process completed.')
        else:
            QMessageBox.information(None, 'Done', 'Process IN-completed.')
            pass

        for ids, feats in dctErrPnts.items():  # pntGeom = QgsGeometry().fromPointXY(iter[0])
            # print("dctErrPnts",dctErrPnts)
            # print("ids",ids)
            # print('feats',feats)
            self.updateErrorPointFeatures([ids, feats[1],feats[2]], feats[0])
        if len(dctErrPnts) > 0:
            print("self.errorPointFeatures",len(self.errorPointFeatures))
            QgsProject.instance().addMapLayer(vMemorylayer)
            layerData.addFeatures(self.errorPointFeatures)
            vMemorylayer.commitChanges()
            QMessageBox.information(None, 'Done', 'Process completed.')
    def updateMANEUVERSFeatures(self, attrList, start,end):
        start_point=start.asPoint()
        end_point=end.asPoint()
        newfeat = QgsFeature()
        newfeat.setAttributes(attrList)
        line_geometry = QgsGeometry.fromPolylineXY([start_point, end_point]) 
        new_geometry = QgsGeometry(line_geometry)
        newfeat.setGeometry(new_geometry)
        self.MANEUVERSFeatures.append(newfeat)
        return attrList
    def update_atrri(self,attrList):
            #    for ids, feats in dctErrPnts2.items():
            # print("attrilist",attrList)
            for feature in self.MANEUVERS_layer.getFeatures():
                for fields in feature.fields():
                    field_name=str(fields.name())
                    # fields_name=field_name.lower()
                    # print("fields_name",fields_name)
                    if field_name=="F_EDGE":
                        # feature['F_EDGE'] = attrList[0]
                        # self.MANEUVERS_layer.updateFeature(feature)
                        print("1234")
                        field_idx = self.MANEUVERS_layer.fields().indexOf('F_EDGE')
                        self.MANEUVERS_layer.changeAttributeValue(feature.id(), self.MANEUVERS_layer.fields().indexFromName('F_EDGE'),attrList[0])
                        # self.MANEUVERS_layer.changeAttributeValue(feature.id(), field_idx, attrList[0])
                        self.MANEUVERS_layer.commitChanges()

    def updateErrorPointFeatures(self, attrList, point):
        # print("attrilist",attrList)
        self.pnt=point
        newfeat = QgsFeature()
        newfeat.setAttributes(attrList)
        newfeat.setGeometry(point)
        self.errorPointFeatures.append(newfeat)

    def get_azimuth(self, az1,az2):
        if az1>0:
            angle=(az2-az1)+180
            if angle<0:
                angle=-angle
            if angle>180:
                angle=360-angle
            # print(">")
        else :
            angle=(az2-az1)+180
            if angle>180:
                angle=360-angle
            if angle<0:
                angle=-angle
        return angle
    
        
        
