# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LanePolyCreater2
                                 A QGIS plugin
 create lane poly 2
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-07-26
        git sha              : $Format:%H$
        copyright            : (C) 2023 by genesys
        email                : pramoddb@igenesys.com
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
from PyQt5.QtWidgets import QFileDialog
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QLabel, QStyle
from qgis.gui import *
from qgis.core import *
from qgis.core import QgsMessageLog
from PyQt5 import *
from PyQt5.QtWidgets import QDialog
from qgis.PyQt.QtCore import Qt
import qgis
import json
import psycopg2
from qgis.core import QgsApplication
import sys
from math import degrees, atan2
import processing

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .lane_poly_creater_2_dialog import LanePolyCreater2Dialog
import os.path


class LanePolyCreater2:
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
            'LanePolyCreater2_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Lane Poly Creater 2')

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
        return QCoreApplication.translate('LanePolyCreater2', message)


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

        icon_path = ':/plugins/lane_poly_creater_2/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'lane_poly_creater_2'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True
        self.loadData()
        self.iface.layerTreeView().currentLayerChanged.connect(self.layer_selection_changed)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Lane Poly Creater 2'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = LanePolyCreater2Dialog()
            self.dlg.Cancel.clicked.connect(self.close)
            self.dlg.Submit.clicked.connect(self.create_Lane_Poly)
            # self.dlg.Submit.clicked.connect(self.lane_poly_creation)
            self.dlg.Set_Schema.clicked.connect(self.set_schema)
            
        self.layer_selection_changed(self.iface.activeLayer())
        self.TestConnection()
        self.add_schema()
        
        self.iface.actionSelect().trigger()
        self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.dlg.Submit.setEnabled(False)
        # self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        for lay in QgsProject.instance().layerStore().mapLayers().values():
            if  lay.name() == 'vw_lane_lines':
                lay.selectionChanged.connect(self.lane_poly_creation)
                lay.selectionChanged.connect(self.getSelectedFeatures)
                lay.selectionChanged.connect(self.show_id)
                lay.removeSelection()
                self.layer=lay
                # self.refresh()
               

        # show the dialog
        self.dlg.show()
        self.refresh()
        # self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
    def close(self):
        # self.dlg.close()
        self.refresh()
       
    
    def getSelectedFeatures(self):
        # print("hjknm")
        # self.lane_poly_creation()
        sel_layer = self.iface.activeLayer()
        for info in sel_layer.selectedFeatures():
            lane_data = info['lane_id']
            if self.variable == '':
                # if self.left_lane_id==lane_data:
                    self.variable = lane_data
                    # print("L lane_data",lane_data)
                    if self.variable1 == '' and self.variable2=='':
                        self.variable1 = self.left_lane_id
                        self.variable2 = self.right_lane_id
            else:
                if self.variable != lane_data:
                    if lane_data not in self.multiple_var:
                        # if self.right_lane_id!=lane_data and self.right_lane_id==lane_data:
                            self.multiple_var.append(lane_data)
                            # print("R lane_data",lane_data)
                            if self.variable1 != self.left_lane_id:
                                if self.right_lane_id not in self.multiple_var1:
                                    self.multiple_var1.append(self.left_lane_id)
                                    try:
                                        if self.variable2==self.left_lane_id: 
                                            self.dlg.Submit.setEnabled(True)
                                            # self.refresh()
                                            pass
                                        else:
                                        #     self.dlg.Submit.setEnabled(False)
                                            QMessageBox.critical(self.dlg, 'Error', "please Slect first left lane line ")
                                            self.refresh()
                                    except Exception as e:
                                        # err1 = "unable read data:-\n" + str(e)
                                        # QMessageBox.information(None, 'Error', err1)
                                        pass
                                    
        
            # # print("self.left_lane_id",self.left_lane_id)
            # # print("self.right_lane_id",self.right_lane_id)
            # if self.variable1 == '' and self.variable2=='':
            #         # if self.left_lane_id==lane_data:
            #             self.variable1 = self.left_lane_id
            #             self.variable2 = self.right_lane_id
            # #             print(" self.variable1",self.left_lane_id)
            # #             print(" self.variable2",self.variable2)
            # else:
            #     if self.variable1 != self.left_lane_id:
            #         if self.right_lane_id not in self.multiple_var1:
            #             # if self.right_lane_id!=lane_data and self.right_lane_id==lane_data:
            #                 self.multiple_var1.append(self.left_lane_id)
            #                 # print("self.multiple_var1",self.left_lane_id)
            #                 # print("self.multiple_var1  list",self.multiple_var1)
            #                 try:
            #                     if self.variable2==self.left_lane_id:
            #                         self.dlg.Submit.setEnabled(True)
            #                         # self.refresh()
            #                         pass
            #                     else:
            #                         self.dlg.Submit.setEnabled(False)
            #                         QMessageBox.critical(self.dlg, 'Error', "please Slect first left lane line ")
            #                         # self.refresh()
                                    
            #                 except Exception as e:
            #                     # err1 = "unable read data:-\n" + str(e)
            #                     # QMessageBox.information(None, 'Error', err1)
            #                     pass
                                    

    def show_id(self):
        # print('self.variable',self.variable)
        # print('self.multiple_var',self.multiple_var)
        self.l_id=self.variable 
        self.dlg.label_4.setText(self.l_id)
        for i in self.multiple_var:
            # print('i',i)
            self.r_id=i
            self.dlg.label_5.setText(self.r_id)
        # print("self.left_lane_id",self.left_lane_id)
        # print("self.right_lane_id",self.right_lane_id)
        print("self.variable",self.variable)
        print("self.variable1",self.variable1)
        print("self.variable2",self.variable2)
        print("self.multiple_var",self.multiple_var)
        print("self.multiple_var1",self.multiple_var1)
        
    
    def TestConnection(self):
        self.conn = psycopg2.connect(database=self.data['database'], user=self.data['user'],
                                     password=self.data['password'],
                                     host=self.data['host'],port=int(self.data['port']))
        self.cursor = self.conn.cursor()
    
    def loadData(self):
        self.data = {}
        path2 = self.plugin_dir
        path = os.path.join(path2, "AppConfig.json")
        try:
            if os.path.exists(path):
                with open(path) as json_file:
                    self.data = json.load(json_file)
                    pass
                # print (self.data)
                pass
        except Exception as e:
            err1 = "unable read data:-\n" + str(e)
            QMessageBox.information(None, 'Error', err1)
            pass
    
    def create_Lane_Poly(self):
        # print("self.left_lane_id",self.left_lane_id)
        # print("self.right_lane_id",self.right_lane_id)
        var=''
        for i in self.multiple_var:
            var += "'" + i + "'" + ','
        output = var[:-1]
        one_lane = "'" + self.variable + "'"

        # print("output",output)
        # print("one_lane",one_lane)
        try:
            # schema=self.data['schema']
            # query = "select * from jp_t117_000_v1_8.lane_poly_generate_auto(" + one_lane + "," + output + ")"
            query = f"select * from {self.schema}.lane_poly_generate_auto(" + one_lane + "," + output + ")"
            print("1",query)
            self.cursor = self.conn.cursor()
            self.cursor.execute(query)
            # print("2",query)
            self.conn.commit()
            QMessageBox.information(self.dlg, 'Successfull',
                                    "The operation has been successfully completed.\nHence the Lane_Poly is created.")
        except Exception as e:
            self.conn.rollback()
            err1 = "Please Select First left lane:-\n" + str(e)
            QMessageBox.information(None, 'Error', err1)
            pass
        self.refresh()
        # print("*******/n")
        # print("self.variable",self.variable)
        # print("self.variable1",self.variable1)
        # print("self.variable2",self.variable2)
        # print("self.multiple_var",self.multiple_var)
        # print("self.multiple_var1",self.multiple_var1)
        
        
    def refresh(self):
        self.variable =''
        self.variable1 =''
        self.variable2 =''
        self.multiple_var=[]
        self.multiple_var1=[]
        self.ids=[]
        # self.layer.removeSelection()
        self.iface.mapCanvas().refreshAllLayers()
        self.dlg.label_4.setText('')
        self.dlg.label_5.setText('')
        self.r_id=''
        self.l_id=''

    def set_schema(self):
        try:
            self.schema=self.dlg.cb.currentText()
            # print("self.schema",self.schema)
            # print("self.active_schema",self.active_schema)
            
            # match_schema='''"'''+self.schema+'''"'''
            # print("self.match_schema",match_schema)
            if self.active_schema==self.schema:
                self.dlg.Submit.setEnabled(False)
                QMessageBox.information(self.dlg, 'Success', "schema Set")
            else:
                self.dlg.Submit.setEnabled(False)
                QMessageBox.critical(self.dlg, 'Error', "Active layer schema & set schama 'Not Same' ")
        except Exception as e:
            pass
            # err1 = "select layer:-\n" + str(e)
            # QMessageBox.information(None, 'Error', err1)
        
        pass
    def add_schema(self):
        schema_lst=self.get_schema()
        self.dlg.cb.clear()
        self.dlg.cb.addItems(schema_lst)
        
        
    def get_schema(self):
        schemaList=[]
        # sql = "select * from information_schema.schemata where schema_name not like 'pg_%' and schema_name <>'information_schema' order by schema_name;"
        sql = "select * from information_schema.schemata where schema_name not like 'p%' and schema_name NOT LIKE 'i%' and schema_name NOT LIKE 'm%' and schema_name <>'information_schema' order by schema_name;"
        # self.cursor.execute(sql)
        
        isExecute, rows, sException_reson = self.sql_FeachRecords(sql)
        # self.conn.close()
        self.cursor = None
        if isExecute == False:
            QMessageBox.information(self.dlg, 'Get Schemas',
                                    "Unable to fetch Schemas from database:-" + str(sException_reson))
        else:
            for row in rows:
                schemaList.append(row[1])
            # print("schemaList", schemaList)
            return schemaList
        print("schemaList", schemaList)
        pass
    def sql_FeachRecords(self,sql,isCommit = False ,isSilent = True,isCloseConn = True):
        isExecute = False
        sException_reson = None
        cur =None
        rows =None
        QgsMessageLog.logMessage("Query :- " + str(sql), "pgSetting",Qgis.Info)
        # cur = self.cursor
        try:
            # print("sql",sql)
            self.cursor.execute(sql)
            if isCommit == True:
                self.conn.commit()
            rows = self.cursor.fetchall()
            # print("row f",rows)
            isExecute = True
        except Exception as e:
            sException_reson = str(sys.exc_info())
            if isSilent== False:
                QMessageBox.information(self.dlg, 'schema', "Unable to Feach Records Query reason:-" + str(sys.exc_info()))
            QgsMessageLog.logMessage("Unable to Feach Records Query reason :-" + str(e), "Schema",Qgis.Info)
            isExecute = False
        finally:
            if isCloseConn == True:
                # self.conn.close()
                self.cursor = None
        return isExecute,rows,sException_reson  
    def layer_selection_changed(self,layer):
        try:
            # print("singal received",layer)
            source = layer.source()
            # print("source",source)
            kvp = source.split(" ")
            for kv in kvp:
                if kv.startswith("table"):
                    # self.active_schema = kv.split("=")[1][0:-15]
                    schema1= kv.split("=")[1][0:-1]
                    _schema=schema1.split(".")[0]
                    self.active_schema=_schema[1:-1]
                    # print( "self.active_schema",self.active_schema)
                    # print( "self.active_schema",self.active_schema)
                    # print( "schema1",schema1)
        except Exception as e:
            pass
            # err1 = "select layer:-\n" + str(e)
            # QMessageBox.information(None, 'Error', err1)
    
    def get_line_points(self, line_feat):
        line_s = line_feat.geometry()
        line_geom = line_s.asPolyline()
        start_point = line_geom[0]
        end_point = line_geom[-1]

        # Calculate the middle point
        num_points = len(line_geom)
        middle_index = num_points // 2
        middle_point = line_geom[middle_index]

        start_point_g = QgsGeometry.fromPointXY(QgsPointXY(start_point.x(), start_point.y()))
        middle_point_g = QgsGeometry.fromPointXY(QgsPointXY(middle_point.x(), middle_point.y()))
        end_point_g = QgsGeometry.fromPointXY(QgsPointXY(end_point.x(), end_point.y()))

        return start_point_g, middle_point_g, end_point_g

    def get_intersect_feats(self, feat_id, side_buffer):
        side_buffer.setSubsetString(self.lane_id + "='" + feat_id + "'")
        buffer_fets = side_buffer.getFeatures()
        intrsect_feats = []
        for fet in buffer_fets:
            buf_geom = fet.geometry()
            for intr_feat in self.lane_layer.getFeatures():
                intr_feat_geom = intr_feat.geometry()
                if fet[self.lane_id] != intr_feat[self.lane_id]:
                    if intr_feat_geom.intersects(buf_geom):
                        intrsect_feats.append(intr_feat)
        return intrsect_feats

    def get_azimuth(self, geometry):
        # Calculate the azimuth of the line geometry.
        line = geometry.asPolyline()
        x1, y1, x2, y2 = line[0].x(), line[0].y(), line[-1].x(), line[-1].y()
        angle = atan2(x2 - x1, y2 - y1)

        # Convert radians to degrees.
        return degrees(angle)


    def lane_poly_creation(self):
        self.lane_layer = self.iface.activeLayer()
        count = self.lane_layer.selectedFeatureCount()
        if count == 0:
            pass
            # QMessageBox.information(self.dlg, 'Information',
            #                         "Please select some lanes, then click 'OK'")
        else:
            # self.schema = self.data['schema']  # The schema where your table is located
            self.lane_id = self.data['lane_table_columns']['lane_id']
            # self.dlg.progressBar.show()
            # self.dlg.ok_button.hide()
            # self.dlg.cancel_button.hide()
            # self.dlg.progressBar.setValue(0)
            self.error_list = []

            # prg = 0

            lay_path = self.lane_layer.dataProvider().dataSourceUri()
            params = {'DISTANCE': 0.00012, 'INPUT':
                QgsProcessingFeatureSourceDefinition(lay_path, selectedFeaturesOnly=True, featureLimit=-1,
                                                     geometryCheck=QgsFeatureRequest.GeometryAbortOnInvalid),
                      'JOIN_STYLE': 0, 'MITER_LIMIT': 2, 'OUTPUT': 'TEMPORARY_OUTPUT', 'SEGMENTS': 8, 'SIDE': 1}

            side_buffer = processing.run("native:singlesidedbuffer", params)['OUTPUT']
            # QgsProject.instance().addMapLayer(side_buffer)
            for feat in self.lane_layer.selectedFeatures():
                feat_id = str(feat[self.lane_id])
                feat_geom = feat.geometry()
                intrsect_feats = self.get_intersect_feats(feat_id, side_buffer)
                start_point, middle_point, end_point = self.get_line_points(feat)
                closest_line = None
                min_distance = float('inf')
                for int_feat in intrsect_feats:
                    int_feat_geom = int_feat.geometry()
                    if start_point.buffer(0.00012, 0.00012).intersects(int_feat_geom) and middle_point.buffer(0.00012,0.00012).intersects(int_feat_geom) and end_point.buffer(0.00012, 0.00012).intersects(int_feat_geom):
                        azimuth1 = self.get_azimuth(feat_geom)
                        azimuth2 = self.get_azimuth(int_feat_geom)

                        # Define a threshold for considering two lines in the same direction.
                        threshold = 15  # You can adjust this threshold as needed.
                        threshold_minus = 165
                        angle_difference = abs((azimuth1 - azimuth2 + 180) % 180)
                        if threshold_minus < angle_difference or angle_difference < threshold:
                            distance = feat_geom.distance(int_feat_geom)
                            if distance < min_distance:
                                min_distance = distance
                                closest_line = int_feat
                if closest_line:
                    # if feat['type'].lower() != 'roadboundary' or closest_line['type'].lower() != 'roadboundary':
                        # error_mrk = []
                        self.left_lane_id = feat[self.lane_id]
                        self.right_lane_id = closest_line[self.lane_id]
                        
                        return self.left_lane_id, self.right_lane_id 
    

    
       
