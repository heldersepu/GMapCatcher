# -*- coding: utf-8 -*-
## @package gmapcatcher.widDrawingArea
# DrawingArea widget used to display the map

import gtk
import pango
import mapUtils
from mapConst import *

## This widget is where the map is drawn
class DrawingArea(gtk.DrawingArea):
    center = ((0,0),(128,128))
    draging_start = (0, 0)

    def __init__(self, scale):
        self.scale = scale
        super(DrawingArea, self).__init__()

        self.visualdl_gc = False

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.da_button_press)

        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.connect('button-release-event', self.da_button_release)

    ## Change the mouse cursor over the drawing_area
    def da_set_cursor(self, dCursor = gtk.gdk.HAND1):
        cursor = gtk.gdk.Cursor(dCursor)
        self.window.set_cursor(cursor)

    ## Handles left (press click) event in the drawing_area
    def da_button_press(self, w, event):
        if (event.button == 1):
            self.draging_start = (event.x, event.y)
            self.da_set_cursor(gtk.gdk.FLEUR)

    ## Handles left (release click) event in the drawing_area
    def da_button_release(self, w, event):
        if (event.button == 1):
            self.da_set_cursor()

    ## Jumps in the drawing_area
    def da_jump(self, intDirection, zoom, doBigJump=False):
        # Left  = 1  Up   = 2
        # Right = 3  Down = 4
        intJump = 10
        if doBigJump:
            intJump = intJump * 10

        self.draging_start = (intJump * (intDirection == 3),
                              intJump * (intDirection == 4))
        self.da_move(intJump * (intDirection == 1),
                     intJump * (intDirection == 2), zoom)

    ## Move the drawing_area
    def da_move(self, x, y, zoom):
        rect = self.get_allocation()
        if (0 <= x <= rect.width) and (0 <= y <= rect.height):
            offset = (self.center[1][0] + (self.draging_start[0] - x),
                      self.center[1][1] + (self.draging_start[1] - y))
            self.center = mapUtils.tile_adjustEx(zoom, self.center[0], offset)
            self.draging_start = (x, y)
            self.repaint()

    ## Scale in the drawing area (zoom in or out)
    def do_scale(self, zoom, current_zoom_level, doForce, dPointer):
        if (zoom == current_zoom_level) and not doForce:
            return

        rect = self.get_allocation()
        da_center = (rect.width // 2, rect.height // 2)
        if dPointer:
            fix_tile, fix_offset = mapUtils.pointer_to_tile(
                rect, dPointer, self.center, current_zoom_level
            )
        else:
            fix_tile, fix_offset = self.center


        scala = 2 ** (current_zoom_level - zoom)
        x = int((fix_tile[0] * TILES_WIDTH  + fix_offset[0]) * scala)
        y = int((fix_tile[1] * TILES_HEIGHT + fix_offset[1]) * scala)
        if dPointer and not doForce:
            x = x - (dPointer[0] - da_center[0])
            y = y - (dPointer[1] - da_center[1])

        self.center = (x / TILES_WIDTH, y / TILES_HEIGHT), \
                      (x % TILES_WIDTH, y % TILES_HEIGHT)
        self.repaint()

    ## Repaint the drawing area
    def repaint(self):
        self.queue_draw()

    ## Draw the second layer of elements
    def draw_overlay(self, zl, conf, crossPixbuf, dlpixbuf, 
                    downloading=False, visual_dlconfig = {},
                    marker=None, locations={}, entry_name="",
                    showMarkers=False, gps=None):
        def draw_image(imgPos, img, width, height):
            mct = mapUtils.coord_to_tile((imgPos[0], imgPos[1], zl))
            xy = mapUtils.tile_coord_to_screen(
                (mct[0][0], mct[0][1], zl), rect, self.center
            )
            if xy:
                for x,y in xy:
                    self.window.draw_pixbuf(
                        self.style.black_gc, img, 0, 0,
                        x + mct[1][0] - width/2,
                        y + mct[1][1] - height/2,
                        width, height
                    )

        rect = self.get_allocation()
        middle = (rect.width / 2, rect.height / 2)
        full = (rect.width, rect.height)
        # Draw cross in the center
        if conf.show_cross:
            self.window.draw_pixbuf(
                self.style.black_gc, crossPixbuf, 0, 0,
                rect.width/2 - 6, rect.height/2 - 6, 12, 12
            )

        # Draw the selected location
        if (entry_name in locations.keys()):
            pixDim = marker.get_pixDim(zl)
            coord = locations[entry_name]
            img = marker.get_marker_pixbuf(zl, 'marker1.png')
            draw_image(coord, img, pixDim, pixDim)
        else:
            coord = (None, None, None)

        # Draw the markers
        if showMarkers:
            pixDim = marker.get_pixDim(zl)
            img = marker.get_marker_pixbuf(zl)
            for string in marker.positions.keys():
                mpos = marker.positions[string]
                if zl <= mpos[2] and (mpos[0],mpos[1]) != (coord[0],coord[1]):
                    draw_image(mpos, img, pixDim, pixDim)

        # Draw GPS position
        if gps is not None:
            location = gps.get_location()
            if location is not None and (zl <= conf.max_gps_zoom):
                img = gps.pixbuf
                draw_image(location, img, GPS_IMG_SIZE[0], GPS_IMG_SIZE[1])

        if downloading:
            self.window.draw_pixbuf(
                self.style.black_gc, dlpixbuf, 0, 0, 0, 0, -1, -1)
                
        sz = visual_dlconfig.get("sz", 4)

        if visual_dlconfig.get("active", False):
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
            thegc = self.visualdl_gc
            thezl = str(zl + visual_dlconfig.get("zl", -2))
            self.visualdl_lo.set_text(thezl)
            self.window.draw_rectangle(thegc, False, middle[0] - full[0] / (sz * 2),
                    middle[1] - full[1] / (sz * 2), full[0] / sz, full[1] / sz)
            self.window.draw_layout(thegc,
                    middle[0] + full[0] / (sz * 2) - len(thezl) * 10,
                    middle[1] - full[1] / (sz * 2),
                    self.visualdl_lo)

        if visual_dlconfig.get('qd', 0) > 0:
            self.visualdl_lo.set_text(
                    str(visual_dlconfig.get('recd', 0)) + "/" +
                    str(visual_dlconfig.get('qd', 0)))
            if sz == 1:
                ypos = -15
            else:
                ypos = 0
            self.window.draw_layout(self.visualdl_gc,
                    middle[0],
                    middle[1] + full[1] / (sz * 2) + ypos, self.visualdl_lo)
                
