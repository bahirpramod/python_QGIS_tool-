
"""
    Behaviour of the auto method of tracing:
    
    *cursor is within snappable distance of a vertices with the shift key goes down
    
    onMouseMove:
        Remove any uncommitted vertices from the rubber band
        If shift is down:
            call proposeRBUpdate()
        
    onShiftKeyGoingDown:
        call proposeRBUpdate()
      
    onShistKeyComingUp:
        Remove any uncommitted vertices from the rubber band
    
    Function proposeRBUpdate():
        If the last point in the RB is snapped to a feature:
            If we're currently snapping to the same feature:
                Determine the vertices that make the shortest path between v1 and v2
                Add them as uncommitted vertices to the rb
        
    If the left button is clicked and the shift key is down:
        Unmark any vertices marked as preliminary
        
    
    High level
    ==========
    
    When the user presses shift and hovers over a vertices, the rubber-band
    should update to show the auto-traced path around the 
"""
import math
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
import time
import win32api
#from pyproj import Proj, transform
import unicodedata
from .disthead import distanceAndHeading
from .point import Point
# Vertex Finder Tool class
class VertexTracerTool(QgsMapTool):
    def __init__(self, parent):
        self.parent =parent
        self.canvas= parent.iface.mapCanvas()
        QgsMapTool.__init__(self,self.canvas)
        self.setAction(parent.action)
        self.started = False
        self.snapper = self.canvas.snappingUtils()
        self.snapIndicator = None
        self.mCtrl = False
        self.mShift = False
        self.lastPoint = None
        self.pointsProposed = False
        self.propVertCnt = 0
        self.snappedLayer = None
        self.snappedGeometry = None
        self.snappedVertexNr = None
        self.snappedPartNr = None
        self.snappedRingNr = None
        self.snappedRingVertexOffset = None
        self.snappedToPolygon = False
        self.fixcedAngle = None
        self.isIgnorePoint = False
        self.IsShowVertexSymbol = False
        self.vertexMarkers = []
        self.canvasSrid =4326
        self.crs_4326 = QgsCoordinateReferenceSystem(int(4326))
        self.crs_Canvas = None
        self.crs_Transfrom_MapCrs_To_4326 =None
        self.crs_Transfrom_4326_To_MapCrs =None
        self.earthSemimajorAxis = 6378137.
        self.earthFlattening = 1 / 298.257223563
        self.vertexMarkers_Test = []
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rb_Cureve = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rb_Buffer = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.secondLastPt_test = None
        self.lastPt_test = None

        self.autoCursor = QCursor(QPixmap(["16 16 3 1",
               "      c None",
               ".     c #FF00FF",
               "+     c #FFFFFF",
               "                ",
               "       +.+      ",
               "      ++.++     ",
               "     +.....+    ",
               "    +.     .+   ",
               "   +.   .   .+  ",
               "  +.    .    .+ ",
               " ++.    .    .++",
               " ... ...+... ...",
               " ++.    .    .++",
               "  +.    .    .+ ",
               "   +.   .   .+  ",
               "   ++.     .+   ",
               "    ++.....+    ",
               "      ++.++     ",
               "       +.+      "]))
        self.getInputFlags()
    def getInputFlags(self):
        self.isIgnorePoint = False
        self.IsConvexHull =self.parent.lockBoxConvexHullGeom.isChecked()
        self.IsShowVertexSymbol = self.parent.lockBoxShowVertexSymbol.isChecked()
        if self.IsConvexHull:
            self.distanceLock = False
            self.distanceRangeLock = False
            self.angleLock = False
            self.toleranceLock = False
            self.iS90Lock = False
            self.arcCureve = False
            self.bufferLine = False
        else:
            self.relBox = self.parent.relBox.isChecked()
            self.distance = self.parent.spinBoxDist.value()
            self.angle = self.parent.spinBoxAngle.value()
            self.distanceLock = self.parent.lockBoxDist.isChecked()
            self.angleLock = self.parent.lockBoxAngle.isChecked()
            self.toleranceLock=self.parent.lockBoxAngleTolerance.isChecked()
            self.tolerance =self.parent.spinBoxLockAngleTolerance.value()
            self.distance_Min =self.parent.spinBoxDist_Min.value()
            self.distance_Max =self.parent.spinBoxDist_Max.value()
            self.distanceRangeLock =self.parent.lockBoxDist_Max.isChecked()
            self.IsConvexHull =self.parent.lockBoxConvexHullGeom.isChecked()
            self.iS90Lock =self.parent.lockBoxAngle90.isChecked()
            self.arcCureve =self.parent.lockBoxPreVertex.isChecked()
            self.bufferLine =self.parent.lockBoxbuffer.isChecked()
            self.arcSegments= self.parent.spinBoxPreVertexCount.value()
            self.bufferSize= self.parent.spinBoxBufferValue.value()
            if self.iS90Lock == True:
                self.angleLock = False
                self.toleranceLock = False
                self.relBox = True
                self.arcSegments = 2
            elif self.toleranceLock == True:
                self.angleLock = False
                self.relBox = True

    def toolName(self):
        return "Advance-Digitize-Auto-trace"
    def setupRubberBand(self):
        s = QSettings()
        rb_w = s.value("/qgis/digitizing/line_width", 1, type=int)
        rb_r = s.value("/qgis/digitizing/line_color_red", 255, type=int)
        rb_g = s.value("/qgis/digitizing/line_color_green", 0, type=int)
        rb_b = s.value("/qgis/digitizing/line_color_blue", 0, type=int)
        rb_a = s.value("/qgis/digitizing/line_color_alpha", 150, type=int)
        
        rb_fill_r = s.value("/qgis/digitizing/fill_color_red", 255, type=int)
        rb_fill_g = s.value("/qgis/digitizing/fill_color_green", 0, type=int)
        rb_fill_b = s.value("/qgis/digitizing/fill_color_blue", 0, type=int)
        rb_fill_a = s.value("/qgis/digitizing/fill_color_alpha", 150, type=int)

        self.rb.setColor(QColor(rb_r, rb_g, rb_b, rb_a))
        self.rb.setFillColor(QColor(rb_fill_r, rb_fill_g, rb_fill_b, rb_fill_a))
        self.rb.setWidth(rb_w)
        self.rb_Cureve.setColor(QColor(rb_r, rb_g, rb_b, rb_a))
        self.rb_Cureve.setLineStyle(Qt.DashLine)
        self.rb_Cureve.setWidth(rb_w)
        self.canvas.refresh()
    def restRubberBands(self):
        self.rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        self.rb_Cureve=QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        self.rb_Buffer = QgsRubberBand(self.canvas,QgsWkbTypes.PolygonGeometry)
        self.parent.lblConvexhullarea.setText('')
        self.canvas.refresh()
    def proposeRBUpdate(self, event=None):
        """
          Pop the last vert off the rb (the current mouse position)
          Push our proposed ones on
          Make not of how many proposed verts were added (propVertCnt)
          Push back the last vert
        """
        if self.started:
          
            # We have to do our capturing of mouse coords here else we just end up popping the same point off and on again if moving
            # i.e. the cursor doesn't follow the mouse
            
            if self.snappedLayer is None:
                return
            
            newMouseP = None
            retval = 0
            snapResults = []
            if event is not None:
                x = event.pos().x()
                y = event.pos().y()
                newMouseP =  QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
                eventPoint = QPoint(x,y)
                snapResults = self.snapper.snapToMap(eventPoint)
            else:
                x = self.canvas.mouseLastXY().x()
                y = self.canvas.mouseLastXY().y()
                vertCount = self.rb.numberOfVertices()
                #newMouseP = QgsPoint( self.rb.getPoint( 0, vertCount - 1 ) )
                
                snapResults = self.snapper.snapToMap( QPoint(x,y) )
              
            if not snapResults.isValid():
                # There was nothing to snap to here, just update the end of the rb
                self.clearSnapIndicator()
                point = QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
                self.rb.movePoint(point)
                # self.show_area() by gulab
                return
            else:
                self.updateSnapIndicator(snapResults[0].snappedVertex)
                part, ring = self.getPartAndRing(snapResults[0].layer, snapResults[0].snappedAtGeometry, snapResults[0].snappedVertexNr)
                if snapResults[0].layer != self.snappedLayer or \
                    snapResults[0].snappedAtGeometry != self.snappedGeometry or \
                    self.snappedPartNr != part or \
                    self.snappedRingNr != ring:
                    # We snapped to something but we can't do anything fancy with it
                    self.rb.movePoint(snapResults[0].snappedVertex)
                    # self.show_area() by gulab
                    return
                
            # By this point, we should be snapping to the same layer and geomtry as last time (so we can now 
            # calculate paths between the two points
            
            self.rb.removeLastPoint()
            # Now determine the points that we need to add
            newVerts = self.getAdditionalVerts( snapResults[0].snappedVertexNr )

            f = QgsFeature()
            self.snappedLayer.getFeatures(QgsFeatureRequest(self.snappedGeometry)).nextFeature(f)

            for newVert in newVerts:
                if self.snappedToPolygon:
                    v = f.geometry().vertexAt(newVert)
                else:
                    v = f.geometry().vertexAt(newVert)
                v = self.canvas.mapRenderer().layerToMapCoordinates(self.snappedLayer, v)
                self.rb.addPoint(v,False)
                self.propVertCnt += 1
                self.pointsProposed = True
            self.rb.update()
            
            self.rb.addPoint(snapResults[0].snappedVertex)
            # self.show_area() by gulab
      
    def getAdditionalVerts( self, secondVertexNr ):
        """
            For a given geometry (even multi-part polygons) determien the 
            shortest (or longest) route between:
              
                self.snappedVertexNr
                and
                secondVertexNr
                on
                self.snappedGeometry
                
                Are they both the same vertice?
                    Are they really the same vertice (0 and 4 in a square)
        """
        firstVertexNr = self.snappedVertexNr
        
        firstVertexNr -= self.snappedRingVertexOffset
        secondVertexNr -= self.snappedRingVertexOffset
        
        if firstVertexNr == secondVertexNr:
            return []
        
        largerNr = max(firstVertexNr,secondVertexNr)
        smallerNr = min(firstVertexNr,secondVertexNr)
        
        f = QgsFeature()
        self.snappedLayer.getFeatures(QgsFeatureRequest(self.snappedGeometry)).nextFeature(f)
        
        if not f.geometry().isMultipart():
            if f.geometry().type() == QgsWkbTypes.LineGeometry:
                vertCount = len( f.geometry().asPolyline() )
            else:
                vertCount = len( f.geometry().asPolygon()[self.snappedRingNr] )
        else:
            if f.geometry().type() == QgsWkbTypes.LineGeometry:
                vertCount = len( f.geometry().asMultiPolyline()[self.snappedPartNr] )
            else:
                vertCount = len( f.geometry().asMultiPolygon()[self.snappedPartNr][self.snappedRingNr] )
        
        if self.snappedToPolygon:
            if ((firstVertexNr == vertCount-1) and (secondVertexNr == 0)) or ((secondVertexNr == vertCount-1) and (firstVertexNr == 0)):
                return []
        
        if self.snappedToPolygon:
            # Determine which route is shorter
            joinFaster = False
            normalDistance = largerNr - smallerNr
            joinDistance = (vertCount - largerNr - 1) + smallerNr
            if joinDistance < normalDistance:
                joinFaster = True
            if self.mCtrl:
                joinFaster = not(joinFaster)
            
            if joinFaster:
                if secondVertexNr > firstVertexNr:
                    a = range(firstVertexNr-1,-1,-1)
                    b = range(vertCount-2,secondVertexNr,-1)
                    a.extend(b)
                    return [x+self.snappedRingVertexOffset for x in a]
                else:
                    a = range(firstVertexNr+1,vertCount,1)
                    b = range(1,secondVertexNr,1)
                    a.extend(b)
                    return [x+self.snappedRingVertexOffset for x in a]
            
        # else if jointFaster is not true
        if secondVertexNr > firstVertexNr:
            newverts = range(firstVertexNr+1,secondVertexNr,1)
            return [x+self.snappedRingVertexOffset for x in newverts]
        else:
            newverts = range(firstVertexNr-1,secondVertexNr,-1)
            return [x+self.snappedRingVertexOffset for x in newverts]

    def acceptProposedRBUpdate(self):
        self.propVertCnt = 0
        self.pointsProposed = False
    
    def revertProposedRBUpdate(self):
        """
            Pop the last vert off the rb
            Pop off and discard propVertCnt vertices
            Push the last vert back on again
        """
        if self.pointsProposed:
            mouseP = QgsPointXY( self.rb.getPoint( 0, self.rb.numberOfVertices()-1 ) )
            self.rb.removeLastPoint()
            for i in range(self.propVertCnt):
                self.rb.removeLastPoint()
            self.rb.addPoint(mouseP)
            self.propVertCnt = 0
            self.pointsProposed = False
            # self.show_area() by gulab
    
    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Control:
            self.mCtrl = True
            if self.mShift:
                self.revertProposedRBUpdate()
                self.proposeRBUpdate()
        if event.key() == Qt.Key_Shift:
            self.mShift = True
            self.proposeRBUpdate()

    def keyReleaseEvent(self,  event):
        event_key  = event.key()
        if event_key == Qt.Key_Control:
            self.mCtrl = False
            if self.mShift:
                self.revertProposedRBUpdate()
                self.proposeRBUpdate()
        if event_key == Qt.Key_Shift:
            self.mShift = False
            self.revertProposedRBUpdate()
        #remove the last added point when the delete key is pressed
        if event_key == Qt.Key_Backspace:
            self.removeLastPoint()
            self.rb_Cureve.reset()
            if self.rb.numberOfVertices() ==1:
                event_key = Qt.Key_Escape
        if event_key == Qt.Key_R:
            self.add_arc()
        if event_key == Qt.Key_Escape:
            self.reset()
        #change map extent on arrow keys
        if event_key in (Qt.Key_Down, Qt.Key_Up, Qt.Key_Left, Qt.Key_Right):
            return
            canvas_center = self.canvas.center()
            canvas_width = self.canvas.extent().width()
            canvas_height = self.canvas.extent().height()
            QgsMessageLog.logMessage('canvas_center - '+str(canvas_center), 'VertexTracerTool')
            QgsMessageLog.logMessage('canvas_width - '+str(canvas_width), 'VertexTracerTool')
            QgsMessageLog.logMessage('canvas_height - '+str(canvas_height), 'VertexTracerTool')
            if event.key() == Qt.Key_Down:
                y = canvas_center.y() + (0.95 * canvas_height)
                x = canvas_center.x()
            elif event.key() == Qt.Key_Up:
                y = canvas_center.y() - (0.95 * canvas_height)
                x = canvas_center.x()
            elif event.key() == Qt.Key_Left:
                x = canvas_center.x() + (0.95 * canvas_width)
                y = canvas_center.y()
            elif event.key() == Qt.Key_Right:
                x = canvas_center.x() - (0.95 * canvas_width)
                y = canvas_center.y()
            new_center = QgsPointXY( x, y )
            self.canvas.setCenter(new_center)
            QgsMessageLog.logMessage('new_center - '+str(new_center), 'VertexTracerTool')
            self.canvas.refresh()

    def removeLastPoint(self):
        if self.rb.numberOfVertices() > 0:
            self.rb.removeLastPoint()
            self.removeLastVartexMarker()
        rbVertCount = self.rb.numberOfVertices()
        if rbVertCount >= 2:
            self.lastPoint = self.rb.getPoint(0, rbVertCount-2)
            lastPointOnScreen = self.canvas.getCoordinateTransform().transform(self.lastPoint)
            retval, snapResults = self.snapper.snapToBackgroundLayers(QPoint( lastPointOnScreen.x(), lastPointOnScreen.y()))
            if len(snapResults) > 0:
                # self.updateDetailsOfLastSnap(snapResults[0]) by gulab
                pass
            else:
                self.updateDetailsOfLastSnap()
        else:
            self.updateDetailsOfLastSnap()
        # self.show_area() by gulab

    def canvasPressEvent(self,event):
        #on left click, we add a point
        if event.button() == Qt.LeftButton:
            layer = self.canvas.currentLayer()
            if not layer:
              return

            #if it the start of a new trace, set the rubberband up
            if self.started == False:
                self.restRubberBands()
                if self.parent.lineSplitPoly or self.parent.reshapePolygon:
                    self.rb.reset(QgsWkbTypes.LineGeometry)
                elif self.parent.fillRing:
                    self.rb.reset(QgsWkbTypes.PolygonGeometry)
                else:
                    self.rb.reset(layer.geometryType())
                self.setupRubberBand()
                self.lastPoint = None
                layer.removeSelection()
                try:
                    crsIdMapCanvas = self.parent.iface.mapCanvas().mapSettings().destinationCrs().authid()
                    stripcRS = unicodedata.normalize('NFKD', crsIdMapCanvas).encode('ascii','ignore')
                    crsStr,crsNum = stripcRS.split(':')
                    self.canvasSrid = crsNum
                    self.crs_Canvas = QgsCoordinateReferenceSystem(int(self.canvasSrid))
                    
                    self.crs_Transfrom_MapCrs_To_4326 =QgsCoordinateTransform(self.crs_Canvas, self.crs_4326)
                    self.crs_Transfrom_4326_To_MapCrs =QgsCoordinateTransform(self.crs_4326 ,self.crs_Canvas)
                    #QgsMessageLog.logMessage(str(self.canvasSrid),"crs_Transfrom")
                except:
                    QgsMessageLog.logMessage(str(sys.exc_info()),"crs_Transfrom")
                    self.canvasSrid = 4326
                    self.crs_Canvas = QgsCoordinateReferenceSystem(int(4326))
            self.started = True
            self.acceptProposedRBUpdate()
            
            if layer != None:
                #if self.mCtrl == False:
                x = event.pos().x()
                y = event.pos().y()
                selPoint = QPoint(x,y)
                result = self.snapper.snapToMap(selPoint)
                # print(dir(result))
                
                #the point is either from snapping result
                if result.isValid():
                    point = result.point()
                    # self.updateDetailsOfLastSnap(result[0]) by gulab
                    
                #or just a plain point
                else:
                    point =  QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
                    self.updateDetailsOfLastSnap()
                  
                self.appendPoint(QgsPointXY(point))
    
    def getPartAndRing(self, layer, featureId, snappedVertNr):
      """ Return the index of the part and ring that snappedVertNr exists 
      in.  Lines will always have ring=0. """
      
      f = QgsFeature()
      layer.getFeatures(QgsFeatureRequest(featureId)).nextFeature(f)
      geom = f.geometry()
      snapGeom = QgsGeometry().fromPoint( geom.vertexAt(snappedVertNr) )
      
      if not geom.isMultipart():
          if geom.type() == QgsWkbTypes.LineGeometry:
              # If it was not snapped to this line, we wouldn't even be here
              self.snappedRingVertexOffset = 0
              return 0, 0
          elif geom.type() == QgsWkbTypes.PolygonGeometry:
              ringId = 0
              vertOffset = 0
              for ring in geom.asPolygon():
                  if ringId > 0:
                      vertOffset += lastRingLen
                  ringGeom = QgsGeometry().fromPolyline( ring )
                  if snapGeom.intersects(ringGeom):
                      self.snappedRingVertexOffset = vertOffset
                      return 0, ringId
                  ringId += 1
                  lastRingLen = len(ring)
              self.snappedRingVertexOffset = 0
              return 0, 0 # We should not get here
          else:
              self.snappedRingVertexOffset = 0
              return 0, 0
      
      else:
          # Multipart
          if geom.type() == QgsWkbTypes.LineGeometry:
              partId = 0
              vertOffset = 0
              for part in geom.asMultiPolyline():
                  if partId > 0:
                      vertOffset += lastLineLength
                  lineGeom = QgsGeometry().fromPolyline( part )
                  if lineGeom.intersects(snapGeom):
                      self.snappedRingVertexOffset = vertOffset
                      return partId, 0
                  partId += 1
                  lastLineLength = len(part)
              return 0, 0 # We should not get here
          elif geom.type() == QgsWkbTypes.PolygonGeometry:
              partId = 0
              vertOffset = 0
              for part in geom.asMultiPolygon():
                  ringId = 0
                  for ring in part:
                      if partId > 0 or ringId > 0:
                          vertOffset += lastRingLen
                      ringGeom = QgsGeometry().fromPolyline( ring )
                      if snapGeom.intersects(ringGeom):
                          self.snappedRingVertexOffset = vertOffset
                          return partId, ringId
                      ringId += 1
                      lastRingLen = len(ring)
                  partId += 1
              self.snappedRingVertexOffset = 0
              return 0, 0 # We should not get here
          else:
              self.snappedRingVertexOffset = 0
              return 0, 0

    def updateDetailsOfLastSnap(self, snappingResult=None):
        if snappingResult is not None:
            self.snappedLayer = snappingResult.layer
            self.snappedGeometry = snappingResult.snappedAtGeometry
            self.snappedVertexNr = snappingResult.snappedVertexNr
            part, ring = self.getPartAndRing(self.snappedLayer, self.snappedGeometry, self.snappedVertexNr)
            self.snappedPartNr = part
            self.snappedRingNr = ring
            if self.snappedLayer.geometryType() == 2:
                self.snappedToPolygon = True
            else:
                self.snappedToPolygon = False
        else:
            self.snappedLayer = None
            self.snappedGeometry = None
            self.snappedVertexNr = None
            self.snappedPartNr = None
            self.snappedRingNr = None
            self.snappedRingVertexOffset = None
            self.snappedToPolygon = False

    def initialiseSnapIndicator(self, position):
        self.snapIndicator = QgsVertexMarker(self.canvas)
        self.snapIndicator.setIconType(QgsVertexMarker.ICON_CROSS)
        self.snapIndicator.setIconSize(20)
        self.snapIndicator.setColor( QColor(85,85,85) )
        self.snapIndicator.setPenWidth(1)

    def updateSnapIndicator(self, newPosition):
        if self.snapIndicator == None:
            self.initialiseSnapIndicator(newPosition)
        else:
            self.snapIndicator.setCenter(newPosition)

    def clearSnapIndicator(self):
        if self.snapIndicator != None:
            self.canvas.scene().removeItem(self.snapIndicator)
            self.snapIndicator = None

    def canvasMoveEvent(self,event):
        
        x = event.pos().x()
        y = event.pos().y()
        eventPoint = QPoint(x,y)
        if self.started:
            if self.mShift and self.snappedLayer is not None:
                self.revertProposedRBUpdate()
                self.proposeRBUpdate(event)
            else:
                # If there is a snapable point nearby, move the end of the rb to it
                result = self.snapper.snapToMap(eventPoint)
                if result.isValid():
                    if self.rb.numberOfVertices() > 1:
                        newPt = self.calculatePointPos(result.point())
                        self.rb.movePoint(QgsPointXY(newPt))
                    else:
                        self.rb.movePoint(result.point())
                    self.updateSnapIndicator(result.point())
                else:
                    point = QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
                    if self.rb.numberOfVertices() > 1:
                        newPt = self.calculatePointPos(point)
                        self.rb.movePoint(QgsPointXY(newPt))
                    else:
                        self.rb.movePoint(point)
                    self.clearSnapIndicator()
                # self.show_area() by gulab
        # Display the snap indicat or even if we have not yet started
        else:
            result = self.snapper.snapToMap(eventPoint)
            if result.isValid():
                self.updateSnapIndicator(result.point())
            else:
                self.clearSnapIndicator()

    def canvasReleaseEvent(self, event):
        #with right click the digitizing is finished
        if self.mShift:
            # User can only finish digitising when they are not holding down shift
            return
        if event.button() == Qt.RightButton:
            layer = self.canvas.currentLayer()
            if layer and self.started == True:
                if layer.type() != 0 :
                    result = QMessageBox.information(None, 'AdvanceDigitize_AutoTrace', 'Current Layer is not vector Layer. Click OK to continue for digitizing or CANCEL to EXIST.')
                    # if result == QMessageBox.Ok:
                    return
                elif layer.isEditable() ==False and (layer.geometryType() == 1 or layer.geometryType() == 2):
                    result = QMessageBox.information( None,'AdvanceDigitize_AutoTrace', 'Current Layer is not editable. Click OK to continue for digitizing or CANCEL to EXIST.')
                    # if result == QMessageBox.Ok:
                    return
            if self.canvas.currentLayer() and self.started == True:
                self.sendGeometry()
            #remember that this trace is finished, the next left click starts a new one
            self.started = False
            self.clearSnapIndicator()
            self.clearVertexMarker()

    def appendPoint(self, point):
        #if self.toleranceLock and self.isIgnorePoint:
            #return
        #don't add the point if it is identical to the last point we added
        if (self.lastPoint != point) :
            if self.rb.numberOfVertices() > 1:
                newPt = self.calculatePointPos(point)
                # if self.secondLastPt_test is not None and self.secondLastPt_test is not None:
                    # p1 = Point(self.secondLastPt_test.y(), self.secondLastPt_test.x())
                    # p2 = Point(self.lastPt_test.y(), self.lastPt_test.x())
                    # p3 = Point(newPt.y(), newPt.x())
                    # distance1, heading1 = disthead.distanceAndHeading(p1, p2)
                    # distance2, heading2 = disthead.distanceAndHeading(p2, p3)
                    # angle = heading1 - heading2
                    # dh = angle -self.angle;
                    # QgsMessageLog.logMessage("p1 x: " + str(p1.format(nDigits = 10)) ,"AdvanceDigitize_AutoTrace_1",QgsMessageLog.INFO)
                    # QgsMessageLog.logMessage("p2 x: " + str(p2.format(nDigits = 10)),"AdvanceDigitize_AutoTrace_1",QgsMessageLog.INFO)
                    # QgsMessageLog.logMessage("p3 x: " + str(p3.format(nDigits = 10)),"AdvanceDigitize_AutoTrace_1",QgsMessageLog.INFO)
                    # QgsMessageLog.logMessage("heading1: " + str(heading1),"AdvanceDigitize_AutoTrace_1",QgsMessageLog.INFO)
                    # QgsMessageLog.logMessage("heading2: " + str(heading2),"AdvanceDigitize_AutoTrace_1",QgsMessageLog.INFO)
                    # QgsMessageLog.logMessage("angle : " + str(angle) + " dh: " + str(dh) ,"AdvanceDigitize_AutoTrace_1",QgsMessageLog.INFO)
                if (self.lastPoint != newPt) :
                    self.rb.addPoint(QgsPointXY(newPt))
                    self.lastPoint = newPt
                    self.addVertextMarker(newPt)
            else:
                self.rb.addPoint(QgsPointXY(point))
                self.lastPoint = point
                self.addVertextMarker(point)
        # self.show_area() by gulab
    def sendGeometry(self):
        layer = self.canvas.currentLayer() 

        coords = []
        #backward compatiblity for a bug in qgsRubberband, that was fixed in 1.7
        # if Qgis.QGIS_VERSION_INT >= 10700: by gulab
        #     #[coords.append(self.rb.getPoint(0, i)) for i in range(self.rb.numberOfVertices())]
        [ coords.append(self.rb.getPoint(0, i)) for i in range(self.rb.numberOfVertices()-1) ] # PW Fix for duplicate final vertice when adding lines
        # else:
        # [coords.append(self.rb.getPoint(0,i)) for i in range(1,self.rb.numberOfVertices())]

        ## On the Fly reprojection.
        layerEPSG = layer.crs().authid()
        # projectEPSG = self.canvas.mapRenderer().destinationCrs().authid()  by gulab
        #
        # if layerEPSG != projectEPSG:
        #     coords_tmp = coords[:]
        #     coords = []
        #     for point in coords_tmp:
        #         transformedPoint = self.canvas.mapRenderer().mapToLayerCoordinates( layer, point );
        #         coords.append(transformedPoint)
        #
        #     coords_tmp = coords[:]
        #     coords = []
        #     lastPt = None
        #     for pt in coords_tmp:
        #         if (lastPt != pt) :
        #             coords.append(pt)
        #             lastPt = pt
           
        if self.parent.lineSplitPoly or self.parent.reshapePolygon:
            g = QgsGeometry().fromPolylineXY(coords)
        elif self.parent.fillRing:
            g = QgsGeometry().fromPolygonXY([coords])
        else:
            ## Add geometry to feature.
            if layer.geometryType() == QgsWkbTypes.PolygonGeometry :
                g = QgsGeometry().fromPolygonXY([coords])
            else:
                g = QgsGeometry().fromPolylineXY(coords)
        if self.IsConvexHull and  layer.geometryType() == QgsWkbTypes.PolygonGeometry:
            g = QgsGeometry( g.convexHull())
            self.convexhullArea(g)
        # self.emit(SIGNAL("traceFound(PyQt_PyObject)"),g)
        self.parent.createFeature(g)
        
        #self.emit(SIGNAL("traceFound(PyQt_PyObject)"),self.rb.asGeometry()) 
        if self.parent.lineSplitPoly or self.parent.reshapePolygon:
            self.rb.reset(QgsWkbTypes.LineGeometry)
        elif self.parent.fillRing:
            self.rb.reset(QgsWkbTypes.PolygonGeometry)
        else:
            self.rb.reset(layer.geometryType())
        self.rb_Cureve.reset(QgsWkbTypes.LineGeometry)
        self.rb_Buffer.reset(QgsWkbTypes.PolygonGeometry)
    def activate(self):
        self.canvas.setCursor(self.autoCursor)
        if self.parent.reTain ==False:
            self.reset()
        QgsMessageLog.logMessage("Tool activate", "AdvanceDigitize_AutoTrace" ,Qgis.Info)

    def reset(self):
        QgsMessageLog.logMessage("Tool reset", "AdvanceDigitize_AutoTrace" ,Qgis.Info)
        self.rb.reset()
        self.rb_Cureve.reset()
        self.rb_Buffer.reset()
        self.clearSnapIndicator()
        self.started = False
        self.snapIndicator = None
        self.mCtrl = False
        self.mShift = False
        self.lastPoint = None
        self.pointsProposed = False
        self.propVertCnt = 0
        self.snappedLayer = None
        self.snappedGeometry = None
        self.snappedVertexNr = None
        self.snappedPartNr = None
        self.snappedRingNr = None
        self.snappedRingVertexOffset = None
        self.snappedToPolygon = False
        self.clearVertexMarker()
    def deactivate(self):
        QgsMessageLog.logMessage("Tool deactivate", "AdvanceDigitize_AutoTrace" ,Qgis.Info)
        # if self.canvas.mapTool():
            # QgsMessageLog.logMessage(str(self.canvas.mapTool().toolName()) + "|" + str(self.canvas.mapTool().action().text()), "AdvanceDigitize_AutoTrace" ,QgsMessageLog.INFO)

        # if self.canvas.mapTool() and ( self.canvas.mapTool().toolName() in ( "mycustomeCursorTool", "Pan") \
        # or ( "Measure "  in self.canvas.mapTool().action().text()) ):
            # self.parent.reTain = True
        # else:
            # self.parent.reTain = False
        # try:
            # if self.parent.reTain ==False: 
                # self.reset()
        # except AttributeError:
            # pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True
    def calculatePointPos(self, pt_):
        x,y = self.convert_currentPrj_to_4326(pt_.x(),pt_.y())
        pt =  QgsPointXY(x,y )
        self.msg_ ="" 
        self.getInputFlags()

        if self.rb.numberOfVertices() ==2 and (self.toleranceLock  == True or self.iS90Lock == True) :
            self.angleLock = False
            self.toleranceLock = False
            self.iS90Lock = False

        lastPt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-2) # Take the second last point, since the last one is just for the interactive movement        
        x,y = self.convert_currentPrj_to_4326(lastPt_.x(),lastPt_.y())
        lastPt = QgsPointXY(x,y )
        self.lastPt_test = lastPt
        newAngle = 0 # This will store the computed angle
        newDist = 10 # This will store the computed distance

        if self.relBox or self.toleranceLock or self.iS90Lock:
            # If the angle is not absolute, we have to compute the angle of the last entered line segment
            if self.rb.numberOfVertices() > 2:
                secondLastPt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-3)
                x,y =self.convert_currentPrj_to_4326(secondLastPt_.x(),secondLastPt_.y())
                secondLastPt = QgsPointXY(x,y)
                self.secondLastPt_test = secondLastPt
                lastAngle = math.atan2(lastPt.y() - secondLastPt.y(), lastPt.x() - secondLastPt.x())
                #lastAngle =disthead.heading_without_dig(Point(secondLastPt.y(), secondLastPt.x()),Point(lastPt.y(), lastPt.x()))
            else:
                #If there is no last entered line segment, we start we a 0 angle
                lastAngle = 0
            if self.toleranceLock or self.iS90Lock:
                p1 = Point(secondLastPt.y(), secondLastPt.x())
                p2 = Point(lastPt.y(), lastPt.x())
                p3 = Point(pt.y(), pt.x())
                distance1, heading1 = distanceAndHeading(p1, p2)
                distance2, heading2 = distanceAndHeading(p2, p3)
                angle = heading1 - heading2
                log_msg = "angle " +  str(angle)
                if  self.iS90Lock == True :
                    log_msg += " | iS90Lock"
                    if ( -151 <= angle <= 151 ) or ( 209 <= angle <= 360 ) or ( -360 <= angle <= -209 ):
                        factor = self.getAngle_side(angle)
                        self.angle = 90 * factor
                        self.angleLock = True
                    else:
                        log_msg += " | ignore "
                        #QgsMessageLog.logMessage( log_msg, "AdvanceDigitize_AutoTrace" ,QgsMessageLog.INFO)
                        self.rb_Cureve.reset()
                        self.rb_Buffer.reset()
                        return self.lastPoint
                elif self.toleranceLock == True :
                    log_msg += " | toleranceLock"
                    if ( -91 <= angle <= 91 ) or ( 269 <= angle<= 360 ) or ( -360 <= angle <= -269 ):
                        log_msg += " | In 91 Tolerance "
                        IsValid ,factor = self.isInRange(self.tolerance,angle)
                        if IsValid ==False and factor is not None:
                            self.angle = self.tolerance * factor
                            self.angleLock = True
                    else:
                        #QgsMessageLog.logMessage( log_msg + "| Out of 91 Tolerance " , "AdvanceDigitize_AutoTrace" ,QgsMessageLog.INFO)
                        self.rb_Cureve.reset()
                        self.rb_Buffer.reset()
                        return self.lastPoint
                #QgsMessageLog.logMessage( log_msg + "| Final angle" + str(self.angle),  "AdvanceDigitize_AutoTrace" ,QgsMessageLog.INFO)
        if self.angleLock:
            # If the angle is locked
            if not self.relBox:
                newAngle =  self.angle/180.0*math.pi # We compute the new angle based on the input angle (ABSOLUTE)
            else:
                newAngle = lastAngle +  self.angle/180.0*math.pi # We compute the new angle based on the input angle (RELATIVE)
        else:
            newAngle = math.atan2((pt.y()-lastPt.y()), pt.x()-lastPt.x()) # We simply set the new angle to the current angle
            if not self.relBox:
                self.parent.spinBoxAngle.setValue(newAngle/math.pi*180.0)# Update the spinBox to reflect the current distance
            else:
                self.parent.spinBoxAngle.setValue( (newAngle-lastAngle)/math.pi*180.0) # Update the spinBox to reflect the current distance                

        newDist = self.getDistance (lastPt, pt, newAngle )
        if self.distanceLock or self.angleLock or self.iS90Lock:
            newpnt=self.getValidPoint(lastPt,newAngle,newDist)
            #verify angle
            if self.toleranceLock or self.iS90Lock:
                p3 = Point(newpnt.y(), newpnt.x())
                distance1, heading1 = distanceAndHeading(p1, p2)
                distance2, heading2 = distanceAndHeading(p2, p3)
                angle = heading1 - heading2
                if angle > 270:
                    angle -= 360
                if angle < -270:
                    angle -= -360
                dh = angle -self.angle
                if not ( -0.05 <= angle <= 0.05 ) :
                    try:
                        new_FixAngle = self.angle/(angle/self.angle)
                        self.angle =new_FixAngle
                        QgsMessageLog.logMessage("p1: " + str(p1.format(nDigits=10)) + " | p2: " + str(p2.format(nDigits=10)) + " | p3: " + str(p3.format(nDigits=10)) , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                        QgsMessageLog.logMessage("heading1: " + str(heading1) + " | heading2: " + str(heading2)  , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                        QgsMessageLog.logMessage("self.angle: " + str(self.angle) + " | angle: " + str(angle) + " | dh: " + str(dh) , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                        QgsMessageLog.logMessage("dh: " + str(dh) + " | newAngle: " + str(newAngle) + " | New Fix Angle: " + str(new_FixAngle) , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                        if not self.relBox:
                            newAngle =  self.angle/180.0*math.piq
                        else:
                            #QgsMessageLog.logMessage( "else relBox" , "AdvanceDigitize_AutoTrace" ,QgsMessageLog.INFO)
                            newAngle = lastAngle +  self.angle/180.0*math.pi
                        if ( -360 <= dh <= 360 ):                
                            newpnt =self.getValidPoint(lastPt,newAngle,newDist)
                        else:
                            QgsMessageLog.logMessage("p1: " + str(p1.format(nDigits=10)) + " | p2: " + str(p2.format(nDigits=10)) + " | p3: " + str(p3.format(nDigits=10)) , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                            QgsMessageLog.logMessage("heading1: " + str(heading1) + " | heading2: " + str(heading2)  , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                            QgsMessageLog.logMessage("self.angle: " + str(self.angle) + " | angle: " + str(angle) + " | dh: " + str(dh) , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                            QgsMessageLog.logMessage("dh: " + str(dh) + " | newAngle: " + str(newAngle) + " | New Fix Angle: " + str(new_FixAngle) , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                            QgsMessageLog.logMessage("out of range" , "AdvanceDigitize_AutoTrace_2" ,Qgis.Info)
                    except:
                        QgsMessageLog.logMessage( "calculate_NextSegments  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)

            self.calculate_NextSegments(lastPt,newpnt,self.angle,newDist)
            x,y = self.convert_4326_to_currentPrj(newpnt.x(),newpnt.y())
            return QgsPointXY(x,y )
        else:
            self.calculate_NextSegments(lastPt,pt,((newAngle-lastAngle)/math.pi*180.0),newDist)
            #self.refresh_arctool()
            return pt_

    def refresh_arctool(self):
        if self.rb.numberOfVertices()>1:
            lastAngle=0
            pt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-1) # Take the second last point, since the last one is just for the interactive movement        
            x,y = self.convert_currentPrj_to_4326(pt_.x(),pt_.y())
            pt = QgsPointXY(x,y )
            lastPt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-2)
            x,y =self.convert_currentPrj_to_4326(lastPt_.x(),lastPt_.y())
            lastPt = QgsPointXY(x,y)
            if self.rb.numberOfVertices() > 2:
                secondLastPt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-3)
                x,y =self.convert_currentPrj_to_4326(secondLastPt_.x(),secondLastPt_.y())
                secondLastPt = QgsPointXY(x,y)
                lastAngle = math.atan2(lastPt.y() - secondLastPt.y(), lastPt.x() - secondLastPt.x())
            newAngle = math.atan2((pt.y()-lastPt.y()), pt.x()-lastPt.x())

            p1 = Point(secondLastPt.y(), secondLastPt.x())
            p2 = Point(lastPt.y(), lastPt.x())
            p3 = Point(pt.y(), pt.x())
            distance1, heading1 = distanceAndHeading(p1, p2)
            distance2, heading2 = distanceAndHeading(p2, p3)
            angle = heading1 - heading2
            newDist = math.sqrt( (pt.x()-lastPt.x())*(pt.x()-lastPt.x()) + (pt.y()-lastPt.y())*(pt.y()-lastPt.y()) )

            QgsMessageLog.logMessage( str(((newAngle-lastAngle)/math.pi*180.0)), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
            QgsMessageLog.logMessage( str(angle), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
            QgsMessageLog.logMessage( str(newDist), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
            self.calculate_NextSegments(lastPt,pt,((newAngle-lastAngle)/math.pi*180.0),newDist)
    def refresh_arctool1(self):
        if self.rb.numberOfVertices()>1:
            lastAngle=0
            pt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-1) # Take the second last point, since the last one is just for the interactive movement        
            x,y = self.convert_currentPrj_to_4326(pt_.x(),pt_.y())
            pt = QgsPointXY(x,y )
            lastPt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-2)
            x,y =self.convert_currentPrj_to_4326(lastPt_.x(),lastPt_.y())
            lastPt = QgsPointXY(x,y)
            if self.rb.numberOfVertices() > 2:
                secondLastPt_ = self.rb.getPoint(0, self.rb.numberOfVertices()-3)
                x,y =self.convert_currentPrj_to_4326(secondLastPt_.x(),secondLastPt_.y())
                secondLastPt = QgsPointXY(x,y)
                lastAngle = math.atan2(lastPt.y() - secondLastPt.y(), lastPt.x() - secondLastPt.x())
            newAngle = math.atan2((pt.y()-lastPt.y()), pt.x()-lastPt.x())
            newDist = self.getDistance (lastPt, pt, newAngle )
            QgsMessageLog.logMessage( str(((newAngle-lastAngle)/math.pi*180.0)), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
            self.calculate_NextSegments(lastPt,pt,((newAngle-lastAngle)/math.pi*180.0),newDist)
    def add_arc(self):
        if self.rb_Cureve.numberOfVertices() == 0 :
            return
        for x in range(1, self.rb_Cureve.numberOfVertices()):
            p = self.rb_Cureve.getPoint(0, x)
            if x== 1 and p != self.rb.getPoint(0, self.rb.numberOfVertices()-1):
                self.rb.addPoint(p)
                self.addVertextMarker(p)
            elif x != 1:
                self.rb.addPoint(p)
                self.addVertextMarker(p)
        self.lastPoint =self.rb.getPoint(0, self.rb.numberOfVertices()-1)
        secondlastpnt_  = self.rb.getPoint(0, self.rb.numberOfVertices()-2)
        x,y = self.convert_currentPrj_to_4326(self.lastPoint.x(),self.lastPoint.y())
        lastPoint =  QgsPointXY(x,y )
        x,y = self.convert_currentPrj_to_4326(secondlastpnt_.x(),secondlastpnt_.y())
        secondlastpnt =  QgsPointXY(x,y )
        self.calculate_NextSegments(secondlastpnt,lastPoint,self.last_heading_NextSegments,self.last_dist_NextSegments)
        self.lastPoint =self.rb.getPoint(0, self.rb.numberOfVertices()-2)
        self.setCursorPosition(self.rb.getPoint(0, self.rb.numberOfVertices()-1))
    def getAngle_side(self, angle):
        if ( -180 <= angle and angle<=0 ) or ( 180 <= angle <= 360 ):
            return -1
        elif ( angle <= 180 ) or ( -360 <= angle <= -180 ):
            return 1
        return None

    def isInRange(self,rng, angle):
        isValid = False
        factor = None
        max = 360- rng
        if ( (rng*-1) <= angle <= rng ) or ( max <= angle <= 360 ) or ( -360 <= angle <= (max*-1) ):
            isValid = True
        else:
            factor = self.getAngle_side(angle)
        return isValid,factor

    def getNextProposePoint(self,p1,p2,angle,distance):
        lastAngle = math.atan2(p2.y() - p1.y(), p2.x() - p1.x())
        newAngle =self.getNextAngle(lastAngle,angle)
        return self.getValidPoint(p2,newAngle,distance)

    def getNextAngle(self,last_heading,angle):
        return last_heading +  angle/180.0*math.pi
        
    def calculate_NextSegments(self,p1,p2,h,d):
        if self.arcCureve ==False:
            return
        self.last_heading_NextSegments =h
        self.last_dist_NextSegments =d
        try:
            self.rb_Cureve.reset(QgsWkbTypes.LineGeometry)
            points =[p2]
            last_pnt = p1
            cur_pnt = p2
            for x in range(0, int(self.arcSegments)):
                pnt = self.getNextProposePoint(last_pnt,cur_pnt,h,d)
                points.append(pnt)
                last_pnt = cur_pnt
                cur_pnt = pnt
            for   p in points:
                x,y = self.convert_4326_to_currentPrj(p.x(),p.y())
                self.rb_Cureve.addPoint( QgsPointXY(x,y ))
            self.rb_Cureve.show()
        except:
            QgsMessageLog.logMessage( "calculate_NextSegments  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)


    def getValidPoint(self,lastPt, newAngle,newDist):
        a = math.cos(newAngle) * newDist
        b = math.sin(newAngle) * newDist
        newpnt =QgsPointXY(lastPt.x() + a, lastPt.y() + b)
        # p1 = Point(lastPt.y(), lastPt.x())
        # p2 = Point(newpnt.y(), newpnt.x())
        # angle =disthead.heading_without_dig(p1,p2)
        # new_FixAngle = angle/(newAngle/angle)
        # QgsMessageLog.logMessage("Input Angle: " + str(newAngle) + "new_FixAngle : " + str( new_FixAngle), "AdvanceDigitize_AutoTrace_3",QgsMessageLog.INFO) 
        # a = math.cos(new_FixAngle) * newDist
        # b = math.sin(new_FixAngle) * newDist
        # newpnt_ =QgsPoint(lastPt.x() + a, lastPt.y() + b)
        
        #QgsMessageLog.logMessage("Input Angle: " + str(newAngle) + "After Angle : " + str( math.atan2((newpnt.y()-lastPt.y()), newpnt.x()-lastPt.x())), "AdvanceDigitize_AutoTrace_3",QgsMessageLog.INFO) 
        #QgsMessageLog.logMessage("heading: " + str(disthead.heading(p1,p2)) + "heading_without_dig : " + str( disthead.heading_without_dig(p1,p2)), "AdvanceDigitize_AutoTrace_3",QgsMessageLog.INFO) 
        
        return newpnt
    def convert_currentPrj_to_4326(self,x, y):
        if self.canvasSrid == 4326:# or self.canvasSrid == 3857:
            return x,y
        xform = self.crs_Transfrom_MapCrs_To_4326 #QgsCoordinateTransform(self.crs_Canvas, self.crs_4326)
        transfpoint = xform.transform(QgsPointXY(float(x),float(y)))
        return transfpoint.x() ,transfpoint.y()

    def convert_4326_to_currentPrj(self,lon, lat):
        if self.canvasSrid == 4326:# or self.canvasSrid == 3857:
            return lon, lat
        xform = self.crs_Transfrom_4326_To_MapCrs #QgsCoordinateTransform( self.crs_4326,self.crs_Canvas)
        transfpoint = xform.transform(QgsPointXY(float(lon),float(lat)))
        return transfpoint.x() ,transfpoint.y()

    def getDistance(self ,lastPt, pt, newAngle):
        newDist = 0
        try:
            if self.distanceLock and self.distanceRangeLock == False:
                newDist = self.distance
                return self.distance
            if self.angleLock:
                newDist = self.projectedDistance( lastPt, pt, newAngle ) # We simply set the new distance to the current distance
            else:
                newDist = math.sqrt( (pt.x()-lastPt.x())*(pt.x()-lastPt.x()) + (pt.y()-lastPt.y())*(pt.y()-lastPt.y()) ) # Or to its projection if the angle is locked
            if self.distanceRangeLock:
                if newDist > self.distance_Max:
                    newDist = self.distance_Max
                    self.distanceLock = True
                elif newDist < self.distance_Min:
                    newDist = self.distance_Min
                    self.distanceLock = True
                else:
                    self.distanceLock = False
            return newDist
        except:
            QgsMessageLog.logMessage( "getDistance  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
        finally:
            self.parent.spinBoxDist.setValue(newDist)

    def projectedDistance(self, lastPt, mousePt, angle):
        ang = angle#/180.0*math.pi
        projVect = QVector2D(math.cos(ang), math.sin(ang))
        #projVect.normalize()
        mouseVect = QVector2D(mousePt.x()-lastPt.x(),mousePt.y()-lastPt.y())

        return QVector2D.dotProduct(mouseVect,projVect)


        #pa = lastPt
        #pb = QPoint( lastPt.x()+math.cos(ang), lastPt.y()+math.sin(ang))

        #m = (pb.y() - pa.y()) / (pb.x() - pa.x())
        #b = pa.y() - (m * pa.x())
    
        #x = (m * mousePt.y() + mousePt.x() - m * b) / (m * m + 1)
        #y = (m * m * mousePt.y() + m * mousePt.x() + b) / (m * m + 1)

        #return math.sqrt( (x-pa.x())*(x-pa.x()) + (y-pa.y())*(y-pa.y()) )
    def setCursorPosition(self,pnt):
        cur = QCursor()
        cur_point = QgsMapTool(self.parent.iface.mapCanvas()).toCanvasCoordinates(pnt)
        transformed_point = self.parent.iface.mapCanvas().mapToGlobal(cur_point)
        cur.setPos(transformed_point.x(),transformed_point.y())
        point = QgsMapToPixel.toMapCoordinates(self.parent.iface.mapCanvas().getCoordinateTransform (), cur_point.x(),cur_point.y())
    def addVertextMarker(self,p):
        if self.IsShowVertexSymbol:
            m = QgsVertexMarker(self.canvas)
            m.setCenter(p)
            self.vertexMarkers.append(m)
    def removeLastVartexMarker(self):
        if self.vertexMarkers != []:
            marker = self.vertexMarkers[ len(self.vertexMarkers) -1]
            self.canvas.scene().removeItem(marker)
            self.vertexMarkers.remove (marker)
            del marker
            self.canvas.refresh()
    def clearVertexMarker (self):
        # Delete also all vertex markers
        for marker in self.vertexMarkers:
            self.canvas.scene().removeItem(marker)
            del marker  
        self.vertexMarkers = []
        self.canvas.refresh()
    def convexhullArea(self ,geom):
        self.show_area(isConvex = True)
        return
        km_area=0
        try:
            area = QgsDistanceArea() #creating object
            area.setEllipsoid('WGS84') #setting ellipsoid
            area.setEllipsoidalMode(True)
            multiPart = geom.isMultipart()
            if (multiPart is False):
                pol = geom.asPolygon()
                km_area =area.measurePolygon(pol[0])
            else:
                pol = geom.asMultiPolygon()
                i=1
                for geom_ in pol:
                    km_area +=area.measurePolygon(geom_[0])
                    i +=1
        except:
            QgsMessageLog.logMessage( "convexhullArea  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
        finally:
            self.parent.lblConvexhullarea.setText( "Area:" + str(round(km_area,4)) + " m")
    def addAllVertexMarker(self):
        try:
            rbVertCount = self.rb.numberOfVertices()
            for index in range(rbVertCount-1):
                p = self.rb.getPoint(0, index)
                self.addVertextMarker(p)
        except:
            QgsMessageLog.logMessage( "addAllVertexMarker  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
        try:
            rbVertCount = self.rb_Cureve.numberOfVertices()
            for index in range(rbVertCount-1):
                p = self.rb_Cureve.getPoint(0, index)
                self.addVertextMarker(p)
        except:
            QgsMessageLog.logMessage( "addAllVertexMarker  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
    
    def latLonScale(self,phi): # in meters per degree
      eSq = self.earthFlattening * (2 - self.earthFlattening)
      sinPhi = math.sin(math.radians(phi))
      c = 1 - eSq * sinPhi * sinPhi
      k = self.earthSemimajorAxis / math.degrees(math.sqrt(c))
      return ((1 - eSq) * k / c, math.cos(math.radians(phi)) * k)

    def distance_1(self,p, q):
      latScale, lonScale = self.latLonScale((p.lat + q.lat) * 0.5)
      dx = (q.lon - p.lon) * lonScale
      dy = (q.lat - p.lat) * latScale
      return math.sqrt(dx * dx + dy * dy)
    def show_area(self,in_geom = None,isConvex = False):
        try:
            if in_geom is None:
                geom = QgsGeometry(self.rb.asGeometry())
            else:
                geom = QgsGeometry(in_geom)
            if geom.type() ==2:
                if isConvex == True:
                    geom = QgsGeometry(geom.convexHull())
                centerpnt =geom.centroid().asPoint()
                srid_zone = self.utmzone(centerpnt)
                rf = QgsCoordinateReferenceSystem(int(srid_zone))
                t = QgsCoordinateTransform(self.crs_Canvas, rf)
                geom.transform(t)
                self.parent.lblConvexhullarea.setText( "Area:" + str(round(geom.area(),4)) + " m")
            else:
                self.parent.lblConvexhullarea.setText('')
        except:
            self.parent.lblConvexhullarea.setText('')
            QgsMessageLog.logMessage( "show_area  Error: " + str(sys.exc_info()), "AdvanceDigitize_AutoTrace" ,Qgis.Info)
    def utmzone(self,pnt):
        x,y =self.convert_currentPrj_to_4326(pnt.x(),pnt.y())
        if (y)>0 :
            pref=32600;
        else:
            pref=32700;
        zone=int(((x+180)/6)+1);
        return zone+pref;