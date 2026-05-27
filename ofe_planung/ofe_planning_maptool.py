# -*- coding: utf-8 -*-
"""
/***************************************************************************

***************************************************************************/
"""

import logging
import math
import processing

from qgis.core import (
    QgsGeometry,
    QgsLineString,
    QgsPoint,
    QgsPointXY,
    QgsRectangle,
    QgsWkbTypes,
    QgsTolerance,
    QgsSnappingConfig,
    QgsVectorLayer,
    QgsFeature,
    Qgis
)
from qgis.gui import (
    QgsMapTool,
    QgsRubberBand,
    QgsMapMouseEvent,
    QgsSnapIndicator,
)
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtCore import Qt, pyqtSignal
from .enum_versuchstypen import Versuchstyp, MapToolMode
from .constants import (
    SNAPPING_TOLERANCE_PIXELS,
    RB_RECTANGLE_COLOR, RB_RECTANGLE_WIDTH,
    RB_POINT_A_COLOR, RB_POINT_B_COLOR, RB_POINT_C_COLOR, RB_POINT_D_COLOR,
    RB_POINT_WIDTH,
    RB_CUTTING_LINES_COLOR, RB_CUTTING_LINES_WIDTH,
    RB_PLOTS_COLOR, RB_PLOTS_WIDTH,
    RB_AB_POINT_A_COLOR, RB_AB_POINT_B_COLOR, RB_AB_POINT_WIDTH,
    RB_AB_LINE_COLOR, RB_AB_LINE_WIDTH,
)

logger = logging.getLogger(__name__)

class OfePlanningMapTool(QgsMapTool):
    ab_line_created = pyqtSignal(object, object, object)

    def __init__(self, map_canvas) -> None:
        QgsMapTool.__init__(self, map_canvas)
        self.map_canvas = map_canvas
        self.map_canvas_crs = self.map_canvas.mapSettings().destinationCrs()
        
        self.mode = MapToolMode.NONE
        self.selected_node = None
        self.ab_line_inprogress = False
        self.rubber_initialized = False
        self.pt_A = None
        self.pt_B = None
        self.p0 = None
        self.pA = None
        self.ab_line = None
        self.ab_line_initialized = False
        self.plots = None
        self.rotation = 0.0
        self.rotation_init = 0.0
        self.all_points = []
        self.rubbers = []

        self.init_rubber()
        self.init_snapping()

    def _init_ab_line_rubbers(self):
        """Initialize rubber bands for AB line drawing."""
        self.ab_A = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        self.ab_A.setColor(RB_AB_POINT_A_COLOR)
        self.ab_A.setWidth(RB_AB_POINT_WIDTH)
        self.ab_A.setIcon(QgsRubberBand.ICON_X)
        self.ab_B = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        self.ab_B.setColor(RB_AB_POINT_B_COLOR)
        self.ab_B.setWidth(RB_AB_POINT_WIDTH)
        self.ab_B.setIcon(QgsRubberBand.ICON_X)
        self.rb_abline = QgsRubberBand(self.map_canvas, QgsWkbTypes.LineGeometry)
        self.rb_abline.setStrokeColor(RB_AB_LINE_COLOR)
        self.rb_abline.setWidth(RB_AB_LINE_WIDTH)

    def _init_plot_rubbers(self):
        """Initialize rubber bands for plot rectangle, nodes, cutting lines, and plots."""
        self.rb = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.rb.setStrokeColor(RB_RECTANGLE_COLOR)
        self.rb.setWidth(RB_RECTANGLE_WIDTH)

        self.rbPA = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        self.rbPA.setColor(RB_POINT_A_COLOR)
        self.rbPA.setWidth(RB_POINT_WIDTH)
        self.rbPB = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        self.rbPB.setColor(RB_POINT_B_COLOR)
        self.rbPB.setWidth(RB_POINT_WIDTH)
        self.rbPC = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        self.rbPC.setColor(RB_POINT_C_COLOR)
        self.rbPC.setWidth(RB_POINT_WIDTH)
        self.rbPD = QgsRubberBand(self.map_canvas, QgsWkbTypes.PointGeometry)
        self.rbPD.setColor(RB_POINT_D_COLOR)
        self.rbPD.setWidth(RB_POINT_WIDTH)

        self.rbLines = QgsRubberBand(self.map_canvas, QgsWkbTypes.LineGeometry)
        self.rbLines.setColor(RB_CUTTING_LINES_COLOR)
        self.rbLines.setWidth(RB_CUTTING_LINES_WIDTH)

        self.rbPlots = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.rbPlots.setStrokeColor(RB_PLOTS_COLOR)
        self.rbPlots.setWidth(RB_PLOTS_WIDTH)

    def init_rubber(self):
        if not self.rubber_initialized:
            self._init_ab_line_rubbers()
            self._init_plot_rubbers()
            self.rubbers = [
                self.rb, self.rbPA, self.rbPB, self.rbPC, self.rbPD,
                self.rbLines, self.rbPlots,
                self.ab_A, self.ab_B, self.rb_abline,
            ]
            self.ab_line_initialized = True
            self.rubber_initialized = True
        self.setCursor(Qt.ArrowCursor)
        return True



    def init_snapping(self):
        self.snapping_tolerance = SNAPPING_TOLERANCE_PIXELS
        self.snapper = self.map_canvas.snappingUtils()
        snap_config = QgsSnappingConfig()
        snap_config.setEnabled(True)
        snap_config.setType(QgsSnappingConfig.SnappingType.VertexAndSegment)
        snap_config.setUnits(QgsTolerance.Pixels)
        snap_config.setTolerance(self.snapping_tolerance)
        snap_config.setMode(Qgis.SnappingMode.AllLayers) 
        snap_config.setIntersectionSnapping(True)
            
        self.snapper.setConfig(snap_config)
        self.snapindicator = QgsSnapIndicator(self.map_canvas)

    
    def hide(self):
        for rb in self.rubbers:
            rb.reset()

    def disable_rubber(self):
        """Clean up AB-line drawing rubber bands after drawing is complete.
        Plot preview rubber bands (rbLines, rbPlots) are intentionally left
        untouched so the green preview persists until the user creates new plots
        or explicitly clears via clear_maptool / hide."""
        for rb in (self.ab_A, self.ab_B, self.rb_abline):
            rb.reset()
        self.snapindicator.setVisible(False)
        self.ab_line_inprogress = False

    def disable_snapping(self):
        """Disable snapping functionality."""
        snap_config = self.snapper.config()
        snap_config.setEnabled(False)
        self.snapper.setConfig(snap_config)
        self.snapindicator.setVisible(False)


    def canvasPressEvent(self, event: QgsMapMouseEvent) -> None:
        if self.rb_abline:
            self.rb_abline.reset()
        if self.ab_A:
            self.ab_A.reset()
        if self.ab_B:
            self.ab_B.reset()
        self.ab_line = None
        pt = self.doSnap(event.pos())
        
        if pt is None:
            pt = self.map_canvas.getCoordinateTransform().toMapCoordinates(
                event.pos().x(), event.pos().y()
            )
        self.p0 = QgsPointXY(pt)
        self.ab_A.setToGeometry(QgsGeometry.fromPointXY(QgsPointXY(self.p0)))
        self.ab_line_inprogress = True
        

    def canvasMoveEvent(self, event: QgsMapMouseEvent) -> None:
        if not self.ab_line_inprogress:
            return

        pos = event.pos()
        snap_match = self.snapper.snapToMap(pos)
        self.snapindicator.setMatch(snap_match)
        
        pt = self.map_canvas.getCoordinateTransform().toMapCoordinates(pos.x(), pos.y())
        pt_A = QgsPointXY(self.p0)
        pt_B = QgsPointXY(pt)
        self.ab_line = QgsGeometry.fromPolylineXY([pt_A, pt_B])
        self.ab_B.setToGeometry(QgsGeometry.fromPointXY(pt_B))
        self.rb_abline.setToGeometry(self.ab_line)


    def canvasReleaseEvent(self, e: QgsMapMouseEvent) -> None:
        pos = e.pos()
        pt = self.doSnap(pos)
        if pt is None:
            pt = self.map_canvas.getCoordinateTransform().toMapCoordinates(pos.x(), pos.y())

        self.pt_A = QgsPointXY(self.p0)
        self.pt_B = QgsPointXY(pt)
        self.ab_line = QgsGeometry.fromPolylineXY([self.pt_A, self.pt_B])
        self.ab_B.setToGeometry(QgsGeometry.fromPointXY(self.pt_B))
        self.rb_abline.setToGeometry(self.ab_line)
        #self.update_rubber()
        
        # Emit signal with the created AB line
        self.ab_line_created.emit(self.ab_line, self.pt_A, self.pt_B)
        
        self.snapindicator.setVisible(False)
        self.ab_line_inprogress = False   

    def create_plots(self, 
                     versuchstyp, 
                     feld_layer, 
                     anzahl_x, 
                     anzahl_y, 
                     plot_width, 
                     plot_length, 
                     gap_x=0,
                     gap_y=0,
                     ohne_vorgewende=True, 
                     vorgewendebreite=0
                     ):
        if versuchstyp is Versuchstyp.STREIFEN:
            bbox = feld_layer.extent()
            plot_length = max((bbox.yMaximum() - bbox.yMinimum()), bbox.xMaximum() - bbox.xMinimum())
            
        # create plots
        plot_points = [] 
        p0_next = QgsPointXY(self.p0)
        if versuchstyp is Versuchstyp.STREIFEN:
            for x in range(anzahl_x):
                plot_points.append([
                    QgsPointXY(p0_next.x(), p0_next.y() - plot_length),
                    QgsPointXY(p0_next.x(), p0_next.y() + plot_length),
                    QgsPointXY(p0_next.x() + plot_width, p0_next.y() + plot_length),
                    QgsPointXY(p0_next.x() + plot_width, p0_next.y() - plot_length),
                    QgsPointXY(p0_next.x(), p0_next.y() - plot_length)
                ])
                p0_next.setX(p0_next.x() + plot_width)
        else:
            for y in range(anzahl_y+1):
                for x in range(anzahl_x):
                    plot_points.append([
                        QgsPointXY(p0_next.x(), p0_next.y()),
                        QgsPointXY(p0_next.x(), p0_next.y() + plot_length),
                        QgsPointXY(p0_next.x() + plot_width, p0_next.y() + plot_length),
                        QgsPointXY(p0_next.x() + plot_width, p0_next.y()),
                        QgsPointXY(p0_next.x(), p0_next.y())
                    ])
                    p0_next.setX(p0_next.x() + plot_width + gap_x)
                p0_next = QgsPointXY(self.p0)
                p0_next.setY(p0_next.y() + y*(plot_length + gap_y))
        
        # turn
        if self.ab_line:
            azimuth = self.azimuth(self.ab_line)
            theta = azimuth
            
            # 2. rotate plots
            for points in plot_points:
                self.rotate(theta, self.p0, points)
        
        self.all_points = plot_points
        self.rbLines.setToGeometry(QgsGeometry.fromMultiPolylineXY(self.all_points))
        return False


    def enlarge_abline(self, extension):
        linelayer = QgsVectorLayer(
            f"LineString?crs={self.map_canvas_crs.authid()}",
            "AB Line",
            "memory",
        )
        feature = QgsFeature(1)
        feature.setGeometry(self.ab_line)
        linelayer.addFeature(feature)

        extend_result = processing.run("native:extendlines", 
                                     {'INPUT':linelayer,
                                      'START_DISTANCE':extension,
                                      'END_DISTANCE':extension,
                                      'OUTPUT':'TEMPORARY_OUTPUT'})
        

        return extend_result["OUTPUT"]

    def get_ab_line(self):
        """Returns the drawn AB line geometry and endpoints."""
        if self.ab_line:
            return {
                'geometry': self.ab_line,
                'point_a': self.pt_A,
                'point_b': self.pt_B,
                'azimuth': self.azimuth(self.ab_line) if self.ab_line else None
            }
        return None

    def toggleSnapping(self):
        self.snapper.toggleEnabled()


    def doSnap(self, pos: any):
        if not pos:
            return None
        snap_match = self.snapper.snapToMap(pos)
        if not snap_match.isValid():
            return None
        
        self.snapindicator.setMatch(snap_match)
        pt = snap_match.interpolatedPoint()
        #self.widget.info(f"Snap match created: {pt.x()}, {pt.y()}")

        if pt and pt.x() != math.nan:
            return QgsPointXY(pt)
        return None

    def updateSnapSettings(self, layer, addLayer=True):
        if layer is None or not layer.isValid():
            #self.widget.info("layer is not available for snapping")
            return False
        if addLayer:
            snap_config = self.snapper.config()
            snap_config.setEnabled(True)
            snap_config.setType(QgsSnappingConfig.VertexAndSegment)
            snap_config.setUnits(QgsTolerance.Pixels)
            snap_config.setTolerance(SNAPPING_TOLERANCE_PIXELS)
            snap_config.setIntersectionSnapping(True)
            snap_config.setMode(QgsSnappingConfig.SnappingMode.AdvancedConfiguration)
            lyr_settings = QgsSnappingConfig.IndividualLayerSettings(
                True, QgsSnappingConfig.SnappingType.VertexAndSegment,
                self.snapping_tolerance, QgsTolerance.Pixels)
            snap_config.setIndividualLayerSettings(layer, lyr_settings)
            self.snapper.setConfig(snap_config)
            self.map_canvas.setSnappingUtils(self.snapper)

        self.setCursor(Qt.ArrowCursor)


    def azimuth(self, line: QgsLineString) -> float:
        if line:
            abline = line.asPolyline()
            return abline[0].azimuth(abline[1])
        else:
            return None

    def azimuth_from_points(self, a: QgsPoint, b: QgsPoint) -> float:
        if a and b:
            return a.azimuth(b)
        else:
            return None
        

    def move(self, pt_move: QgsPointXY, to_move: list) -> None:
        if pt_move is None or to_move is None or len(to_move) < 1:
            return
        dx = pt_move.x() - self.pA.x()
        dy = pt_move.y() - self.pA.y()
        self.pA = pt_move
        for p in to_move:
            A = QgsGeometry.fromPointXY(p).asPoint()
            p.setX(A.x() + dx)
            p.setY(A.y() + dy)


    def rotate(self, rotation: float, pt_rotate: QgsPointXY, to_rotate: list) -> None:
        if rotation is None or pt_rotate is None or to_rotate is None:
            pass

        for p in to_rotate:
            if p.x() == pt_rotate.x() and p.y() == pt_rotate.y():
                pass
            A = QgsGeometry.fromPointXY(p)
            A.rotate(rotation, pt_rotate)
            p.setX(A.asPoint().x())
            p.setY(A.asPoint().y())