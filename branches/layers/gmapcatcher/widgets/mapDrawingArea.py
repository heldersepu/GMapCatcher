# -*- coding: utf-8 -*-
## @package gmapcatcher.widgets.mapDrawingArea
# Base DrawingArea with some functionality

import gtk
import pango
import gmapcatcher.mapUtils as mapUtils
from gmapcatcher.mapConst import *
from threading import Timer, Thread, Event
import time


## This widget esxpands gtk.DrawingArea
class DrawingArea(gtk.DrawingArea):
    center = ((0, 0), (128, 128))
    draging_start = (0, 0)
    markerThread = None
    isPencil = False
    visualdl_gc = False
    scale_gc = False
    arrow_gc = False
    track_gc = False
    trackThreadInst = None
    trackTimer = None
    gpsTrackInst = None

    def __init__(self):
        super(DrawingArea, self).__init__()

    def stop(self):
        if self.trackThreadInst:
            self.trackThreadInst.stop()
        if self.gpsTrackInst:
            self.gpsTrackInst.stop()

    ## Repaint the drawing area
    def repaint(self):
        self.queue_draw()

    ## Convert coord to screen
    def coord_to_screen(self, x, y, zl, getGlobal=False):
        mct = mapUtils.coord_to_tile((x, y, zl))
        xy = mapUtils.tile_coord_to_screen(
            (mct[0][0], mct[0][1], zl), self.get_allocation(), self.center, getGlobal
        )
        if xy:
            # return (xy[0] + mct[1][0], xy[1] + mct[1][1])
            for x, y in xy:
                return (x + mct[1][0], y + mct[1][1])

    ## Set the Graphics Context used in the visual download
    def set_visualdl_gc(self):
        if not self.visualdl_gc:
            fg_col = gtk.gdk.color_parse("#0F0")
            bg_col = gtk.gdk.color_parse("#0BB")
            self.visualdl_gc = self.window.new_gc(
                    fg_col, bg_col, None, gtk.gdk.COPY,
                    gtk.gdk.SOLID, None, None, None,
                    gtk.gdk.INCLUDE_INFERIORS,
                    0, 0, 0, 0, True, 3, gtk.gdk.LINE_DOUBLE_DASH,
                    gtk.gdk.CAP_NOT_LAST, gtk.gdk.JOIN_ROUND)
            self.visualdl_gc.set_dashes(0, [3])
            self.visualdl_gc.set_rgb_fg_color(fg_col)
            self.visualdl_gc.set_rgb_bg_color(bg_col)
            self.visualdl_lo = pango.Layout(self.get_pango_context())
            self.visualdl_lo.set_font_description(
                pango.FontDescription("sans normal 12"))

    ## Set the Graphics Context used in the scale
    def set_scale_gc(self):
        if not self.scale_gc:
            fg_scale = gtk.gdk.color_parse("#000")
            bg_scale = gtk.gdk.color_parse("#FFF")
            self.scale_gc = self.window.new_gc(
                    fg_scale, bg_scale, None, gtk.gdk.INVERT,
                    gtk.gdk.SOLID, None, None, None,
                    gtk.gdk.INCLUDE_INFERIORS,
                    0, 0, 0, 0, True, 3, gtk.gdk.LINE_SOLID,
                    gtk.gdk.CAP_NOT_LAST, gtk.gdk.JOIN_MITER)
            self.scale_gc.set_rgb_bg_color(bg_scale)
            self.scale_gc.set_rgb_fg_color(fg_scale)
            self.scale_lo = pango.Layout(self.get_pango_context())
            self.scale_lo.set_font_description(
                pango.FontDescription("sans normal 10"))

    def set_track_gc(self, initial_color):
        if not self.track_gc:
            color = gtk.gdk.color_parse(initial_color)
            self.track_gc = self.window.new_gc(
                color, color, None, gtk.gdk.COPY,
                gtk.gdk.SOLID, None, None, None,
                gtk.gdk.CLIP_BY_CHILDREN, 0, 0, 0,
                0, False, 1, gtk.gdk.LINE_SOLID,
                gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_BEVEL)

    ## Set the graphics context for the gps arrow
    def set_arrow_gc(self):
        if not self.arrow_gc:
            fg_arrow = gtk.gdk.color_parse("#777")
            bg_arrow = gtk.gdk.color_parse("#FFF")
            self.arrow_gc = self.window.new_gc(
                    fg_arrow, bg_arrow, None, gtk.gdk.INVERT,
                    gtk.gdk.SOLID, None, None, None,
                    gtk.gdk.INCLUDE_INFERIORS,
                    0, 0, 0, 0, True, 2, gtk.gdk.LINE_SOLID,
                    gtk.gdk.CAP_NOT_LAST, gtk.gdk.JOIN_MITER)
            self.arrow_gc.set_rgb_bg_color(bg_arrow)
            self.arrow_gc.set_rgb_fg_color(fg_arrow)

    ## Draws a circle
    def draw_circle(self, screen_coord, gc):
        radius = 10
        self.window.draw_arc(
            gc, True, screen_coord[0] - radius, screen_coord[1] - radius,
            radius * 2, radius * 2, 0, 360 * 64
        )

    ## Draws a point
    def draw_point(self, screen_coord, gc):
        self.window.draw_point(
            gc, screen_coord[0], screen_coord[1]
        )

    def draw_tracks(self, conf, tracks, zl, track_width, draw_distance=False):
        if not self.trackThreadInst:
            self.set_track_gc('blue')
            self.trackThreadInst = self.TrackThread(self, self.track_gc,
                conf.units, tracks, zl, track_width, draw_distance)
            self.trackThreadInst.start()
        else:
            update_all = False
            if self.trackThreadInst.zl != zl:
                update_all = True
            self.trackThreadInst.unit = conf.units
            self.trackThreadInst.zl = zl
            self.trackThreadInst.tracks = tracks
            self.trackThreadInst.track_width = track_width
            self.trackThreadInst.draw_distance = draw_distance
            if update_all:
                self.trackThreadInst.update_all.set()
                self.trackThreadInst.update.set()
            else:
                if self.trackTimer:
                    self.trackTimer.cancel()
                self.trackTimer = Timer(conf.overlay_delay, self.trackThreadInst.update.set)
                self.trackTimer.start()

    class TrackThread(Thread):
        def __init__(self, da, gc, unit, tracks, zl, track_width, draw_distance=False):
            Thread.__init__(self)
            self.da = da
            self.gc = gc
            self.colors = ['purple', 'blue', 'yellow', 'pink', 'brown', 'orange', 'black']
            self.unit = unit
            self.tracks = tracks
            self.zl = zl
            self.track_width = track_width
            self.draw_distance = draw_distance
            self.screen_coords = {}
            self.update = Event()
            self.update.set()
            self.update_all = Event()
            self.update_all.set()
            self.__stop = Event()

            self.setDaemon(True)

        def run(self):
            while not self.__stop.is_set():
                self.update.wait()      # Wait for update signal to start updating
                self.update.clear()     # Clear the signal straight away to allow stopping of the update
                if self.update_all.is_set():
                    rect = self.da.get_allocation()
                    self.base_point = mapUtils.pointer_to_coord(rect, (0, 0), self.da.center, self.zl)
                    for track in self.tracks:
                        self.screen_coords[track] = []
                    self.update_all.clear()
                i = 0
                for track in self.tracks:
                    if track.name == 'GPS track':
                        self.draw_line(track, 'red', self.zl, False)
                    else:
                        self.draw_line(track, self.colors[i % len(self.colors)], self.zl)
                        i += 1

        def stop(self):
            self.__stop.set()

        def draw_line(self, track, track_color, zl, draw_start_end=True):
            coord_to_screen_f = self.da.coord_to_screen
            def do_draw(ini, end, dist_str=None):
                gtk.threads_enter()
                try:
                    self.da.window.draw_line(self.gc, ini[0], ini[1], end[0], end[1])
                    if dist_str:
                        self.da.write_text(self.gc, end[0], end[1], dist_str, 10)
                finally:
                    gtk.threads_leave()

            def coord_to_screen(c):
                temp = coord_to_screen_f(c.latitude, c.longitude, zl, True)
                cur_coord = coord_to_screen_f(self.base_point[0], self.base_point[1], zl, True)
                return (temp[0] - cur_coord[0], temp[1] - cur_coord[1])

            self.gc.line_width = self.track_width
            self.gc.set_rgb_fg_color(gtk.gdk.color_parse(track_color))
            cur_coord = coord_to_screen_f(self.base_point[0], self.base_point[1], zl, True)

            rect = self.da.get_allocation()
            center = (rect.width / 2, rect.height / 2)
            threshold = 1000  # in pixels
            threshold_x = threshold + center[0]
            threshold_y = threshold + center[1]
            mod_x = cur_coord[0] - center[0]
            mod_y = cur_coord[1] - center[1]

            dist_str = None

            start = time.time()
            # See if track is already in screen_coords
            try:
                self.screen_coords[track]
            except:
                # If not, add it
                self.screen_coords[track] = []

            screen_coords = self.screen_coords[track]
            if len(self.screen_coords[track]) < len(track.points):
                # Calculate screen_coords for points which aren't in it already
                screen_coords.extend(map(coord_to_screen, track.points[len(screen_coords):]))

            for j in range(len(screen_coords) - 1):
                # If update or __stop was set while we're in the loop, break
                if self.update.is_set() or self.update_all.is_set() or self.__stop.is_set():
                    return
                if abs(screen_coords[j][0] + mod_x) < threshold_x \
                  and abs(screen_coords[j][1] + mod_y) < threshold_y:
                    if self.draw_distance:
                        distance = mapUtils.countDistanceFromLatLon(track.points[j].getLatLon(), track.points[j + 1].getLatLon())
                        if self.unit != UNIT_TYPE_KM:
                            distance = mapUtils.convertUnits(UNIT_TYPE_KM, self.unit, distance)
                        dist_str = '%.3f %s' % (distance, DISTANCE_UNITS[self.unit])
                    ini = (screen_coords[j][0] + cur_coord[0], screen_coords[j][1] + cur_coord[1])
                    end = (screen_coords[j + 1][0] + cur_coord[0], screen_coords[j + 1][1] + cur_coord[1])
                    if ini and end:
                        do_draw(ini, end, dist_str)

            if draw_start_end:
                if track.distance:
                    distance = mapUtils.convertUnits(UNIT_TYPE_KM, self.unit, track.distance)
                    text = '%s - %.2f %s' % (track.name, distance, DISTANCE_UNITS[self.unit])
                else:
                    text = track.name
                gtk.threads_enter()     # Precautions to tell GTK that we're drawing from a thread now
                try:
                    self.da.write_text(self.gc, screen_coords[0][0] + cur_coord[0],
                        screen_coords[0][1] + cur_coord[1], '%s (start)' % text)
                    self.da.write_text(self.gc, screen_coords[-1][0] + cur_coord[0],
                        screen_coords[-1][1] + cur_coord[1], '%s (end)' % text)
                finally:
                    gtk.threads_leave()  # And once we are finished, tell that as well...
            print '%.3f' % (time.time() - start)
