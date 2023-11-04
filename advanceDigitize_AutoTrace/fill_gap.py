# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FillGap
                                 A QGIS plugin
 FillGap
                              -------------------
        begin                : 2018-06-05
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Fill Gap
        email                : nutang
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
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
##from fill_gap_dialog import FillGapDialog
import os.path
from .snap_features import Snap_Features


class FillGap:
    """QGIS Plugin Implementation."""

    def __init__(self, parent, action):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.parent = parent
        self.iface = self.parent.iface
        self.action = action
##        # initialize plugin directory
##        self.plugin_dir = os.path.dirname(__file__)
##        # initialize locale
##        locale = QSettings().value('locale/userLocale')[0:2]
##        locale_path = os.path.join(
##            self.plugin_dir,
##            'i18n',
##            'FillGap_{}.qm'.format(locale))
##
##        if os.path.exists(locale_path):
##            self.translator = QTranslator()
##            self.translator.load(locale_path)
##
##            if qVersion() > '4.3.3':
##                QCoreApplication.installTranslator(self.translator)
##
##
##        # Declare instance attributes
##        self.actions = []
##        
##        self.menu = self.tr(u'&FillGap')
##        # TODO: We are going to let the user set this up in a future iteration
##        self.toolbar = self.iface.addToolBar(u'FillGap')
##        self.toolbar.setObjectName(u'FillGap')
##
##    # noinspection PyMethodMayBeStatic
##    def tr(self, message):
##        """Get the translation for a string using Qt translation API.
##
##        We implement this ourselves since we do not inherit QObject.
##
##        :param message: String for translation.
##        :type message: str, QString
##
##        :returns: Translated version of message.
##        :rtype: QString
##        """
##        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
##        return QCoreApplication.translate('FillGap', message)
##
##
##    def add_action(
##        self,
##        icon_path,
##        text,
##        callback,
##        enabled_flag=True,
##        add_to_menu=True,
##        add_to_toolbar=True,
##        status_tip=None,
##        whats_this=None,
##        parent=None):
##        """Add a toolbar icon to the toolbar.
##
##        :param icon_path: Path to the icon for this action. Can be a resource
##            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
##        :type icon_path: str
##
##        :param text: Text that should be shown in menu items for this action.
##        :type text: str
##
##        :param callback: Function to be called when the action is triggered.
##        :type callback: function
##
##        :param enabled_flag: A flag indicating if the action should be enabled
##            by default. Defaults to True.
##        :type enabled_flag: bool
##
##        :param add_to_menu: Flag indicating whether the action should also
##            be added to the menu. Defaults to True.
##        :type add_to_menu: bool
##
##        :param add_to_toolbar: Flag indicating whether the action should also
##            be added to the toolbar. Defaults to True.
##        :type add_to_toolbar: bool
##
##        :param status_tip: Optional text to show in a popup when mouse pointer
##            hovers over the action.
##        :type status_tip: str
##
##        :param parent: Parent widget for the new action. Defaults None.
##        :type parent: QWidget
##
##        :param whats_this: Optional text to show in the status bar when the
##            mouse pointer hovers over the action.
##
##        :returns: The action that was created. Note that the action is also
##            added to self.actions list.
##        :rtype: QAction
##        """
##
##        # Create the dialog (after translation) and keep reference
##        self.dlg = FillGapDialog()
##
##        icon = QIcon(icon_path)
##        action = QAction(icon, text, parent)
##        action.triggered.connect(callback)
##        action.setEnabled(enabled_flag)
##
##        if status_tip is not None:
##            action.setStatusTip(status_tip)
##
##        if whats_this is not None:
##            action.setWhatsThis(whats_this)
##
##        if add_to_toolbar:
##            self.toolbar.addAction(action)
##
##        if add_to_menu:
##            self.iface.addPluginToMenu(
##                self.menu,
##                action)
##
##        self.actions.append(action)
##
##        return action
##
##    def initGui(self):
##        """Create the menu entries and toolbar icons inside the QGIS GUI."""
##
##        icon_path = ':/plugins/AdvanceDigitize_AutoTrace/fill.png'
##        self.action = self.add_action(
##            icon_path,
##            text=self.tr(u'FillGap'),
##            callback=self.run,
##            parent=self.iface.mainWindow())
##
##
##    def unload(self):
##        """Removes the plugin menu item and icon from QGIS GUI."""
##        for action in self.actions:
##            self.iface.removePluginMenu(
##                self.tr(u'&FillGap'),
##                action)
##            self.iface.removeToolBarIcon(action)
##        # remove the toolbar
##        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        
        self.mLayer = self.iface.activeLayer()
        if self.mLayer.type() == 0 and self.mLayer.geometryType() == 2:
            if self.mLayer.selectedFeatureCount() > 0:
                self.allFeatures = self.mLayer.selectedFeatures()
            else:
                QMessageBox.information(None, 'Fill Gap', 'Please select all the polygons surrounding the gap to be filled.')
                self.action.setChecked(False)
                return
        else:
            QMessageBox.information(None, 'Fill Gap', 'Please select polygon layer.')
            self.action.setChecked(False)
            return

        QMessageBox.information(None, 'Fill Gap', 'Now place a point in the gap to be filled.')
        self.selectGapTool = SelectFillLocation(self, self.action)
##        selectedPoint = None
##        if selectGapTool.m is not None:
##            selectGapTool.m = None
        self.iface.mapCanvas().setMapTool(self.selectGapTool)
##        selectedPoint = selectGapTool.m
##        if selectedPoint:
##            if self.iface.mapCanvas().mapSettings().destinationCrs().authid().upper() != 'EPSG:4326':
##                crsSrc = self.iface.mapCanvas().mapSettings().destinationCrs()
##                crsDest = QgsCoordinateReferenceSystem(4326)
##                xform = QgsCoordinateTransform(crsSrc, crsDest)
##                transfpoint = xform.transform(selectedPoint)
##            else:
##                transfpoint = selectedPoint
##        
##            self.checkPolygonGaps(transfpoint)

    def checkPolygonGaps(self, selectedPoint):
        QgsMessageLog.logMessage('checkPolygonGaps', "FillGap" ,Qgis.Info)
        gapPolygonFeatures = []
        index = QgsSpatialIndex()
        id = 1
        unionGeometry = None
        errorFeats = []
        buffer = 0.000001
        try:
            for i, feat in enumerate(self.allFeatures):
                QApplication.processEvents()
                if feat.geometry():
                    index.insertFeature(feat)
                    if i == 0:
                        unionGeometry = feat.geometry()
                    else:
                        unionGeometry = unionGeometry.combine(feat.geometry())

            extentWkt = unionGeometry.boundingBox().asWktPolygon()
            extentGeom = QgsGeometry().fromWkt(extentWkt)
            bufferExtent = extentGeom.buffer(2,3)
            differenceGeoms = bufferExtent.difference(unionGeometry)

            for g in differenceGeoms.asGeometryCollection():
                QApplication.processEvents()
                if extentGeom.contains(g) and len( set([ p.geometry().intersects(g) for p in self.allFeatures ]) ) == 1:
                    newfeat = QgsFeature()
                    newfeat.setGeometry(g)
                    id += 1
                    errorFeats.append(newfeat)
##            if len(errorFeats) > 0:
##                vMemorylayer = QgsVectorLayer("Polygon?crs=epsg:4326", "gaps_filled", "memory")
##                vMemorylayer.startEditing()
##                layerData = vMemorylayer.dataProvider()
##                layerData.addFeatures(errorFeats)
##                vMemorylayer.commitChanges()

            if len(errorFeats) == 0:
                QMessageBox.information(None, 'Fill Gap', 'No Gap found between the selected polygons.')
                self.mLayer.removeSelection()
                self.iface.mapCanvas().unsetMapTool(self.selectGapTool)
                self.selectGapTool.clearHandlers()
                self.iface.actionTouch().trigger()
                return

            addSuccess = False
            self.mLayer.startEditing()
            mSnap_Features = Snap_Features(self, self.mLayer)
            for gapFeat in errorFeats:
                if gapFeat.geometry().contains(QgsGeometry().fromPointXY(selectedPoint)):
                    QApplication.processEvents()
                    self.iface.mapCanvas().setCurrentLayer(self.mLayer)
                    addSuccess = self.parent.createFeature(gapFeat.geometry())
                    break
##                provider = self.mLayer.dataProvider()
##                fields = provider.fields()
##                f = QgsFeature(fields)
##                f.setGeometry(gapFeat.geometry())
##                f.setAttribute(0, self.mLayer.defaultValue(0))
##                self.mLayer.addFeature(f)
##                self.iface.actionSaveActiveLayerEdits()
##                self.iface.mapCanvas().refresh()
            if addSuccess:
                bBox = gapFeat.geometry().boundingBox()
                self.mLayer.selectByRect(bBox)
                mSnap_Features.fixSnapissue()
                QMessageBox.information(None, 'Fill Gap', 'Success!')
            else:
                QMessageBox.information(None, 'Fill Gap', 'Failed..no gap found at selected location.')

            self.mLayer.removeSelection()
            self.iface.mapCanvas().unsetMapTool(self.selectGapTool)
            self.selectGapTool.clearHandlers()
            self.iface.actionTouch().trigger()
##            QgsMapLayerRegistry.instance().addMapLayer(vMemorylayer) 
            
        except:
            QgsMessageLog.logMessage("Error:-" + str(sys.exc_info()), "FillGap", Qgis.Info)
            self.iface.mapCanvas().unsetMapTool(self.selectGapTool)
            self.selectGapTool.clearHandlers()
            # self.iface.actionTouch().trigger()


class SelectFillLocation(QgsMapTool):
    def __init__(self, parent, action):
        self.parent = parent
        self.iface = self.parent.iface
        self.canvas = self.iface.mapCanvas()
        QgsMapTool.__init__(self, self.canvas)
        self.setAction(action)
        self.m = None
        self.custom_cursor = QCursor(QPixmap(":/plugins/AdvanceDigitize_AutoTrace/fill_cursor.png"))
        self.setCursor(self.custom_cursor)

    def toolName(self):
        return "Select Fill Location"

    def canvasPressEvent(self, e):      
        EPoint = self.toMapCoordinates(e.pos()) 

        if(self.m is not None):
           self.canvas.scene().removeItem(self.m)
           self.m = None

        self.m = QgsVertexMarker(self.canvas)        
        self.m.setCenter(EPoint)
        self.m.setColor(QColor(255, 0, 0))
        self.m.setIconSize(5)
        self.m.setIconType(QgsVertexMarker.ICON_BOX) 
        self.m.setPenWidth(5)
        self.canvas.refresh()

        if self.iface.mapCanvas().mapSettings().destinationCrs().authid().upper() != 'EPSG:4326':
            crsSrc = self.iface.mapCanvas().mapSettings().destinationCrs()
            crsDest = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform(crsSrc, crsDest)
            transfpoint = xform.transform(EPoint)
        else:
            transfpoint = EPoint
    
        self.parent.checkPolygonGaps(transfpoint)

    def clearHandlers(self):
        if self.m is not None:
           self.canvas.scene().removeItem(self.m)
           self.m = None










































            
