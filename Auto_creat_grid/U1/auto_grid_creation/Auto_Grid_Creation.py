# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoGridCreation
                                 A QGIS plugin
 Auto Grid Creation with uniqe id 
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-06-20
        git sha              : $Format:%H$
        copyright            : (C) 2023 by pramod/genesys
        email                : pramoddb@emial.igenesys.com
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
from qgis import processing
from PyQt5.QtCore import QVariant

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .Auto_Grid_Creation_dialog import AutoGridCreationDialog
import os.path


class AutoGridCreation:
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
            'AutoGridCreation_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Auto Grid Creation')

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
        return QCoreApplication.translate('AutoGridCreation', message)


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

        icon_path = ':/plugins/Auto_Grid_Creation/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Auto Grid Creation'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Auto Grid Creation'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = AutoGridCreationDialog()
            self.dlg.Cancel.clicked.connect(self.close)
            self.dlg.Ok.clicked.connect(self.auto_creat_grid)
            self.dlg.Ok.clicked.connect(self.sorted_horizontally)
            # self.dlg.Ok.clicked.connect(self.unique_name)

        # show the dialog
        # self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.dlg.show()
        self.addlayers()
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
        self.dlg.comboBox.addItems([layer.name() for layer in self.layer]) 
        self.current_layer = self.dlg.comboBox.currentText()
        for lyr in self.layer:
            layers_name = lyr.name()
            if self.current_layer == layers_name:
                # print("layers_name",layers_name)
                self.lay  = lyr
    def auto_creat_grid(self):
        from math import ceil
        # self.lay = self.iface.activeLayer()
        xmin,ymin,xmax,ymax = self.lay .extent().toRectF().getCoords()
        id_name= (self.dlg.lineEdit.text())
        self.name=id_name
        h_distance= eval(self.dlg.lineEdit_2.text())/100
        v_distance= eval(self.dlg.lineEdit_3.text())/100
        gridWidth = h_distance
        gridHeight = v_distance
        x_spacing =  h_distance
        y_spacing = v_distance
        rows = ceil((ymax-ymin)/gridHeight)
        cols = ceil((xmax-xmin)/gridWidth)
        ringXleftOrigin = xmin
        ringXrightOrigin = xmin + gridWidth
        ringYtopOrigin = ymax
        ringYbottomOrigin = ymax-gridHeight
        uri = "Polygon?crs=" + self.lay.crs().authid()
        self.layer=QgsVectorLayer(uri, id_name, "memory")
        self.pr =self.layer.dataProvider()
        self.layer.dataProvider().addAttributes( [ QgsField("id", QVariant.Int), QgsField("prodgrid", QVariant.String), QgsField("prd_by", QVariant.String), QgsField("qc_by", QVariant.String),QgsField("cc_by", QVariant.String) ] )
        for i in range(int(cols)):
            # reset envelope for rows
            ringYtop = ringYtopOrigin
            ringYbottom =ringYbottomOrigin
            for j in range(int(rows)):
                # poly = [QgsPoint(ringXleftOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYtop)] 
                # # print(poly)
                # points=poly
                self.seg = QgsFeature()  
                x = xmin + (i * x_spacing)
                y = ymin + (j * y_spacing)
                rectangle = QgsRectangle(x, y, x + x_spacing, y + y_spacing)
                self.seg.setGeometry(QgsGeometry.fromRect(( rectangle)))
                self.pr.addFeatures( [self.seg] )
                self.layer.updateExtents() 
                ringYtop = ringYtop - gridHeight
                ringYbottom = ringYbottom - gridHeight
            ringXleftOrigin = ringXleftOrigin + gridWidth
            ringXrightOrigin = ringXrightOrigin + gridWidth

        QgsProject.instance().addMapLayer( self.layer)
        self.layer.startEditing()
    
        i=0
        count = 700
        # self.new_layer()
        for feature in self.lay.getFeatures():
            for feat in self.layer.getFeatures():
                i += 1
                percent = i / float(count) * 100
                self.dlg.progressBar.setValue(percent)
                if  not feat.geometry().intersects(feature.geometry()):
                    self.layer.deleteFeature(feat.id())
                    # idj=feat.id()
                    # f_list.append(feat.id())
        
                    # self.layer.startEditing()
                    # self.layer.select(idj)
        # for i in f_list:
        #     self.layer.startEditing()
        #     self.layer.select(i)
        #     # self.layer.deleteSelectedFeatures()
        #     self.layer.deleteFeature(i)
        self.layer.commitChanges()

        # selection = self.layer.selectedFeatures()
        # for feature in selection:
        #     self.pr.addFeatures([feature])
        # self.layer1.commitChanges()
        # QgsProject.instance().addMapLayer(self.layer1)
        # new_layer = self.layer.materialize(QgsFeatureRequest().setFilterFids(self.layer.selectedFeatureIds()))
        # QgsProject.instance().addMapLayer(new_layer)
        # self.new_layer=new_layer
        
                    # for i in f:
                    #     self.layer1.dataProvider().addFeatures( i)
                        # selected_feat.append(f)
                    # self.layer1.startEditing()
                    # self.layer1.dataProvider().addFeatures( feat)
                    # self.layer1.commitChanges()
                    # self.layer.deleteSelectedFeatures()
                    # self.layer.commitChanges()
        # for i in selected_feat:
        #     nselected_feat.append(QgsFeature(i))
        # self.new_layer()
        # self.layer1.startEditing()
        # self.layer1.dataProvider().addFeatures( nselected_feat)
        # self.layer1.commitChanges()
        # QgsProject.instance().addMapLayer( self.layer1)

    def new_layer(self):
        uri = "Polygon?crs=" + self.lay.crs().authid()
        self.layer1=QgsVectorLayer(uri, self.name, "memory")
        self.pr =self.layer1.dataProvider()
        self.layer1.dataProvider().addAttributes( [ QgsField("id", QVariant.Int), QgsField("prodgrid", QVariant.String), QgsField("prd_by", QVariant.String), QgsField("qc_by", QVariant.String),QgsField("cc_by", QVariant.String) ] )
        

    def sorted_horizontally(self):
        grid_layer=self.layer
        grid_layer.startEditing()
        features = grid_layer.getFeatures()
        ordered_ids = []
        current_id = 1
        for feature in features:
            geometry = feature.geometry()
            x_min = geometry.boundingBox().yMinimum() 

            ordered_ids.append((current_id, feature.id(), x_min))
            current_id += 1

        ordered_ids.sort(key=lambda x: x[2],reverse=True)  # Sort by x_min

        
        for idx, (_, feature_id, _) in enumerate(ordered_ids):
            grid_layer.changeAttributeValue(feature_id, grid_layer.fields().indexFromName('id'), idx + 1)
            id_=(idx+1)
            if id_<10:
                n=str('00')+str(id_)
            elif id_>9 and id_<100:
                n=str('0')+str(id_)
            else:
                n=str(id_)
            name=self.name+n
            grid_layer.changeAttributeValue(feature_id, grid_layer.fields().indexFromName('prodgrid'), name)
        QMessageBox.information(self.dlg, "Info"," Successfully Process completed")
        self.dlg.progressBar.setValue(10)
    



     # def auto_creat_grid(self):
    #     import processing
    #     from math import ceil
    #     self.lay = self.iface.activeLayer()
    #     # print(self.lay)
    #     self.lay.startEditing()
    #     xmin,ymin,xmax,ymax = self.lay.extent().toRectF().getCoords()
    #     # print(xmin,ymin,xmax,ymax)
    #     crs=self.lay.crs().authid()
    #     # print(crs)
    #     crs = QgsProject().instance().crs().toWkt() # it is EPSG:3857
    #     id_name= (self.dlg.lineEdit.text())
    #     self.name=id_name
    #     h_distance= eval(self.dlg.lineEdit_2.text())/100
    #     v_distance= eval(self.dlg.lineEdit_3.text())/100
    #     params = {'TYPE':2,
    #             # 'EXTENT': str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax),
    #             'EXTENT': str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax),
    #             'HSPACING':h_distance,
    #             'VSPACING':v_distance,
    #             'HOVERLAY':0,
    #             'VOVERLAY':0,
    #             'CRS':crs,
    #             'OUTPUT':'memory'}
    #     out1 = processing.run('native:creategrid', params)
    #     print(out1)
    #     grid = QgsVectorLayer(out1['OUTPUT'], id_name,'ogr')
    #     QgsProject().instance().addMapLayer(grid)
    #     # feat= QgsVectorLayer.getFeatures(grid)
    #     layer=grid
    #     self.layer=layer
    #     # print(layer)
    #     # print("1",feat)
    #     grid_list=[]
    #     grid_list_2=[]
    #     f_list=[]
    #     i=0
    #     count = 700
        
    #     for feature in self.lay.getFeatures():
    #         for feat in layer.getFeatures():
                
    #             i += 1
    #             percent = i / float(count) * 100
    #             self.dlg.progressBar.setValue(percent)
    #             grid_list_2.append(feat)
    #         # print("2",feature)
    #             if feat.geometry().intersects(feature.geometry()):
    #                 grid_list.append(feat)
    #     for id1 in grid_list_2:
    #         if id1 not in grid_list:
    #                 idj=id1.id()
    #         layer.select(idj)
    #         layer.startEditing()
    #         # layer.deleteFeatures(idj)
    #         layer.deleteSelectedFeatures()
    #         layer.commitChanges()
    #         f_list=[]
    #         for fields in feat.fields():
    #             f_list.append(fields.name())
    #             pass
    #         # else :
    #         #     idj=id1.id()
    #         # layer.select(idj)
    #         # # layer.deleteFeatures(idj)
    #         # layer.startEditing()
    #         # layer.deleteSelectedFeatures()
    #         # layer.commitChanges()
    #         # f_list=[]
    #         # for fields in feat.fields():
    #         #     f_list.append(fields.name())
    #     f_list1=f_list[2:]
    #     # print(f_list1)
    #     for fields in f_list1:
    #         f_delet= layer.fields().indexFromName(fields)
    #         layer.dataProvider().deleteAttributes([f_delet])
    #         layer.updateFields()
    #     layer.dataProvider().addAttributes( [ QgsField("prodgrid", QVariant.String), QgsField("prd_by", QVariant.String), QgsField("qc_by", QVariant.String),QgsField("cc_by", QVariant.String) ] )
    #     layer.updateFields()







    
    # def unique_name(self):
    #     id_list=[]
    #     id1=[]
    #     layer=self.layer
    #     # layer.startEditing()
    #     # for feature in layer.getFeatures():
    #     #     # id1.append(feature.id())
    #     #     for fields in feature.fields():
    #     #             # print("3")
    #     #             field_name=(fields.name())
    #     #             if field_name=="id"   :
    #     #                 id_list.append(feature['id'])
    #     #                 id_=(feature['id'])
    #     #             if id_<10:
    #     #                 n=str('00')+str(id_)
    #     #             elif id_>9 and id_<100:
    #     #                 n=str('0')+str(id_)
    #     #             else:
    #     #                 n=str(id_)
    #     #             # print(n)
    #     #             name=self.name+str('_')+n
    #     #             # field_idx = layer.fields().indexOf('prodgrid')
    #     #             field_idx = layer.fields().indexFromName('prodgrid')
    #     #             id1=feature.id()
    #     #             print(id)
    #     #             layer.changeAttributeValue(id1, field_idx,name)
    #     #             layer.commitChanges()
    #     QMessageBox.information(self.dlg, "Info"," Successfully Process completed")
       
            

        
        
    # def Row_data(self):

        '''working data 
'''
 # import processing
        # from math import ceil
        # self.lay = self.iface.activeLayer()
        # # print(self.lay)
        # self.lay.startEditing()
        # x_spacing =0.01
        # y_spacing = 0.01
       
        # # print(value)
        # xmin,ymin,xmax,ymax = self.lay.extent().toRectF().getCoords()
        # print(xmin,ymin,xmax,ymax)
        # # grid_size = 1000  # Size of each grid cell in map units
        # # xmin, ymin, xmax, ymax = 1000, 1000, 5000, 5000  # Extent of the grid

        # grid_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "Grid", "memory")
        # provider = grid_layer.dataProvider()
        # fields = QgsFields()
        # fields.append(QgsField("ID", QVariant.Int))
        # provider.addAttributes(fields)
        # grid_layer.updateFields()
        # grid_extent = QgsRectangle(xmin, ymin, xmax, ymax)
        # x_count = int((xmax - xmin) / x_spacing)
        # y_count = int((ymax - ymin) / y_spacing)
        # print("x",x_count)
        # print("y",y_count)
        # feature_id = 0
        # for i in range(x_count):
        #     print("first")
        #     for j in range(y_count):
        #         print("test")
        #         x = xmin + (i * x_spacing)
        #         y = ymin + (j * y_spacing)
        #         rectangle = QgsRectangle(x, y, x + x_spacing, y + y_spacing)
        #         feature = QgsFeature()
        #         feature.setGeometry(QgsGeometry.fromRect(rectangle))
        #         feature.setAttributes([feature_id])
        #         provider.addFeature(feature)
        #         feature_id += 1
        # QgsProject.instance().addMapLayer(grid_layer)
        # self.iface.mapCanvas().refresh()
 
        # # feature_id = 0
        # x = xmin
      
        # while x <= xmax:
        #     y = ymin
        #     while y <= ymax:
        #         feature = QgsFeature()
        #         feature.setGeometry(QgsGeometry.fromRect(QgsRectangle(x, y, x + grid_size, y + grid_size)))
        #         feature.setAttributes([feature_id])
        #         provider.addFeatures([feature])
        #         y += grid_size
        #         feature_id += 1
        #     x += grid_size

        # QgsProject.instance().addMapLayer(grid_layer)
        # iface.mapCanvas().refresh()



        # # print(xmin,ymin,xmax,ymax)
        # # crs=self.lay.crs().authid()
        # # # print(crs)
        # # crs = QgsProject().instance().crs().toWkt() # it is EPSG:3857
        # # import os
        # # myfilepath= self.iface.activeLayer().dataProvider().dataSourceUri()
        # # output_path='memory'
        # # # Create the vector layer
        # # uri = "Polygon?crs=" + self.lay.crs().authid()
        # # grid_layer = QgsVectorLayer(uri, 'grid', 'memory')
        # # grid_provider = grid_layer.dataProvider()
        # # # Define the grid extent and create the grid
        # # grid_extent = QgsRectangle(xmin, ymin, xmax, ymax)
        # # x_count = int((xmax - xmin) / x_spacing)
        # # y_count = int((ymax - ymin) / y_spacing)
        # # for i in range(x_count):
        # #     for j in range(y_count):
        # #         print("teat")
        # #         x = xmin + (i * x_spacing)
        # #         y = ymin + (j * y_spacing)
        # #         rectangle = QgsRectangle(x, y, x + x_spacing, y + y_spacing)
        # #         feature = QgsFeature()
        # #         feature.setGeometry(QgsGeometry.fromRect(rectangle))
        # #         grid_provider.addFeature(feature)
        # # Create the grid shapefile
        # # QgsVectorFileWriter.writeAsVectorFormat(grid_layer,  'utf-8',self.lay.crs().authid(), 'ESRI Shapefile')

        # # # Load the grid layer into QGIS (optional)
        # # self.iface.addVectorLayer(output_path, 'grid', 'ogr')









    #     id_list=[]
    #     layer=self.layer
    #     # idfield = 'id'
    #     # features = [f for f in layer.getFeatures()]
    #     # features.sort(key=lambda y: (round(y.geometry().centroid().asPoint().y()), round(y.geometry().centroid().asPoint().x())))
    #     # # order = [i[2] for i in features]
    #     # ix = layer.fields().indexOf(idfield)
    #     # name=1
    #     # attributemap = {f.id():{ix:e} for e,f in enumerate(features, name)}
    #     # layer.dataProvider().changeAttributeValues(attributemap)
    #     for feature in layer.getFeatures():
    #         for fields in feature.fields():
    #                 field_name=(fields.name())
    #                 if field_name=="id"   :
    #                 #    id_list.append(feature['id'])
    #                     id_=(feature['id'])
    #                     if id_<10:
    #                         n=str('00')+str(id_)
    #                     elif id_>9 and id_<100:
    #                         n=str('0')+str(id_)
    #                     else:
    #                         n=str(id_)
    #                     # print(n)
    #                     name=self.name+str('_')+n
    #                     field_idx = layer.fields().indexOf('prodGrid')
    #                     id=feature.id()
    #                     layer.changeAttributeValue(id, field_idx,name)
    #                     layer.commitChanges()
    #     QMessageBox.information(self.dlg, "Info"," Successfully")
    #     # for f in layer.getFeatures():
    #     #     field_idx = layer.fields().indexOf('prodGrid')
    #     #     id=f.id()
    #     #     layer.changeAttributeValue(id, field_idx,self.name)
    #     # layer.commitChanges()
    #     # for feature in layer.getFeatures():
    #     #     for fields in feature.fields():
    #     #             field_name=(fields.name())
    #     #             if field_name=="id"   :
    #     #                id_list.append(feature['id'])
    #     # print(len(id_list))
    #     # co=len(id_list)
    #     # k=1
    #     # for i in id_list:
    #     #         field_name = "id"
    #     #         filter_value = str (i)
    #     #         expression = QgsExpression(f'"{field_name}" = \'{filter_value}\'')
    #     #         context = QgsExpressionContext()
    #     #         context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(layer))
    #     #         feature3d=layer.getFeatures(QgsFeatureRequest(expression, context))
    #     #         field_idx = layer.fields().indexOf('id')
    #     #         for f in  feature3d:
    #     #             id=f.id()
    #     #             layer.changeAttributeValue(id, field_idx, self.name+str('_')+str(k))
    #     #         layer.commitChanges()
            

        
    #     pass
        
       










                    # my_field = layer.fields().indexFromName('left')
                    # my_field = layer.fields().indexFromName('right')
                    # my_field = layer.fields().indexFromName('top')
                    # my_field = layer.fields().indexFromName('bottom')
                    # my_field = layer.fields().indexFromName('id')
                    # layer.dataProvider().deleteAttributes([my_field])
                    # layer.updateFields()
                # for i in grid_list:
                #     ids=(i.id())
                #     if feat.id()!=ids:
                #         grid_list_2.append(feat)
                #     for j in grid_list_2:
                #         idj=j.id()
                #         layer.select(idj)



                    # grid_list_2.append(ids)
                    # layer.select(ids)
                    # if ids!=feat.id():
                    #     grid_list_2.append(feat.id())
# print("1",grid_list)
        # print("2",grid_list_2)
        # for j in grid_list_2:
        #     ids1=(j.id())
        #     layer.select(ids1)
       
    
        







        # cellsize = 0.0001 #Cell Size in WGS 84 will be 10 x 10 meters 
        # crs = "EPSG:4326" #WGS 84 System 
        # input = processing.getObject(gridbh.name()) #Use the processing.getObject to get information from our vector layer
        # xmin = (input.extent().xMinimum()) #extract the minimum x coord from our layer
        # xmax =  (input.extent().xMaximum()) #extract our maximum x coord from our layer
        # ymin = (input.extent().yMinimum()) #extract our minimum y coord from our layer
        # ymax = (input.extent().yMaximum()) #extract our maximum y coord from our layer
        # #prepare the extent in a format the VectorGrid tool can interpret (xmin,xmax,ymin,ymax)
        # extent = str(xmin)+ ',' + str(xmax)+ ',' +str(ymin)+ ',' +str(ymax)  
        # grid="PATH_FOR_VECTORGRID_CREATION"
        # processing.runalg('qgis:vectorgrid',  extent, cellsize, cellsize,  0, grid)







        # Grid_extent=extent
        # Horizontal_spacing=10
        # Vertical_spacing=10
        
        
        # extent = Grid_extent.split(',')
        # (xmin, xmax, ymin, ymax) = (float(extent[0]), float(extent[1]), float(extent[2]), float(extent[3]))
        # hspacing = Horizontal_spacing
        # vspacing = Vertical_spacing
        
        # # Create the grid layer
        # crs = iface.mapCanvas().mapSettings().destinationCrs().toWkt()
        # vector_grid = QgsVectorLayer('Polygon?crs='+ crs, 'vector_grid' , 'memory')
        # prov = vector_grid.dataProvider()
        
        # # Add ids and coordinates fields
        # fields = QgsFields()
        # fields.append(QgsField('ID', QVariant.Int, '', 10, 0))
        # fields.append(QgsField('XMIN', QVariant.Double, '', 24, 6))
        # fields.append(QgsField('XMAX', QVariant.Double, '', 24, 6))
        # fields.append(QgsField('YMIN', QVariant.Double, '', 24, 6))
        # fields.append(QgsField('YMAX', QVariant.Double, '', 24, 6))
        # prov.addAttributes(fields)
        
        # # Generate the features for the vector grid
        # id = 0
        # y = ymax
        # while y >= ymin:
        #     x = xmin
        #     while x <= xmax:
        #         point1 = QgsPoint(x, y)
        #         point2 = QgsPoint(x + hspacing, y)
        #         point3 = QgsPoint(x + hspacing, y - vspacing)
        #         point4 = QgsPoint(x, y - vspacing)
        #         vertices = [point1, point2, point3, point4] # Vertices of the polygon for the current id
        #         inAttr = [id, x, x + hspacing, y - vspacing, y]
        #         feat = QgsFeature()
        #         feat.setGeometry(QgsGeometry().fromPolygon([vertices])) # Set geometry for the current id
        #         feat.setAttributes(inAttr) # Set attributes for the current id
        #         prov.addFeatures([feat])
        #         x = x + hspacing
        #         id += 1
        #     y = y - vspacing
        
        # # Update fields for the vector grid
        # vector_grid.updateFields()
        
        # # Add the layer to the Layers panel
        # QgsMapLayerRegistry.instance().addMapLayers([vector_grid])
        #  from math import ceil
        # canvas= qgis.utils.iface.mapCanvas()
        # # first layer
        # layer = canvas.layer(0)
        # xmin,ymin,xmax,ymax = layer.extent().toRectF().getCoords()
        # gridWidth = 1000
        # gridHeight = 1000
        # rows = ceil((ymax-ymin)/gridHeight)
        # cols = ceil((xmax-xmin)/gridWidth)
        # ringXleftOrigin = xmin
        # ringXrightOrigin = xmin + gridWidth
        # ringYtopOrigin = ymax
        # ringYbottomOrigin = ymax-gridHeight
        # pol = Crea_layer("grid", "Polygon")
        # for i in range(int(cols)):
        #     # reset envelope for rows
        #     ringYtop = ringYtopOrigin
        #     ringYbottom =ringYbottomOrigin
        #     for j in range(int(rows)):
        #         poly = [QgsPoint(ringXleftOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYtop)] 
        #         pol.create_poly(poly) 
        #         ringYtop = ringYtop - gridHeight
        #         ringYbottom = ringYbottom - gridHeight
        #     ringXleftOrigin = ringXleftOrigin + gridWidth
        #     ringXrightOrigin = ringXrightOrigin + gridWidth

        # pol.disp_layer
#         from math import ceil
#         # canvas= qgis.utils.iface.mapCanvas()
#         # # first layer
#         # layer = canvas.layer(0)
#         layer = self.iface.activeLayer()
#         xmin,ymin,xmax,ymax = layer.extent().toRectF().getCoords()
#         gridWidth = 1000
#         gridHeight = 1000
#         rows = ceil((ymax-ymin)/gridHeight)
#         cols = ceil((xmax-xmin)/gridWidth)
#         ringXleftOrigin = xmin
#         ringXrightOrigin = xmin + gridWidth
#         ringYtopOrigin = ymax
#         ringYbottomOrigin = ymax-gridHeight
#         pol = Crea_layer("grid", "Polygon")
#         for i in range(int(cols)):
#             # reset envelope for rows
#             ringYtop = ringYtopOrigin
#             ringYbottom =ringYbottomOrigin
#             for j in range(int(rows)):
#                 poly = [QgsPoint(ringXleftOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYtop)] 
#                 pol.create_poly(poly) 
#                 ringYtop = ringYtop - gridHeight
#                 ringYbottom = ringYbottom - gridHeight
#             ringXleftOrigin = ringXleftOrigin + gridWidth
#             ringXrightOrigin = ringXrightOrigin + gridWidth

#         pol.disp_layer

# class Crea_layer(object):
#     def __init__(self,name,type):
#         self.type=type
#         self.name = name
#         self.layer =  QgsVectorLayer(self.type, self.name , "memory")
#         self.pr =self.layer.dataProvider() 
#     def create_poly(self,points):
#         self.seg = QgsFeature()  
#         self.seg.setGeometry(QgsGeometry.fromPolyline(points))
#         self.pr.addFeatures( [self.seg] )
#         self.layer.updateExtents()
#     @property
#     def disp_layer(self):
#         QgsMapLayerRegistry.instance().addMapLayers([self.layer])