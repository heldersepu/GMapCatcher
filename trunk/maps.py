#!/usr/bin/env python
import os
import gobject
import pygtk
pygtk.require('2.0')
import gtk
import googleMaps
import threading
from threading import Thread

class GetTileThread(Thread):
        def __init__(self,
                        zl,
                        real_tile_x,
                        real_tile_y,
                        tile_x_pos_inner,
                        tile_y_pos_inner,
                        x_pos,
                        y_pos,
                        draw_width,
                        draw_height,
                        online,
                        gc,
                        window):
                Thread.__init__(self)
                self.zl = zl
                self.x = real_tile_x
                self.y = real_tile_y
                self.xp = x_pos
                self.yp = y_pos
                self.draw_width = draw_width
                self.draw_height = draw_height
                self.online = online
                self.gc = gc
                self.window = window
                self.xi = tile_x_pos_inner
                self.yi = tile_y_pos_inner

        def run(self):
                pixbuf = self.window.ctx_map.get_tile_pixbuf(self.zl, (self.x, self.y), self.online)
                gc = self.gc
                self.window.drawing_area.window.draw_pixbuf(gc, pixbuf,
                                                        int(self.xi),
                                                        int(self.yi),
                                                        int(self.xp), int(self.yp),
                                                        int(self.draw_width), int(self.draw_height))
                return

class MainWindow(gtk.Window):
        center = ((0,0),(128,128))
        draging = False
        draging_start = (0, 0)
        current_zoom_level = googleMaps.MAP_MAX_ZOOM_LEVEL
        queue = None
        threads = []



        def do_scale(self, pos, pointer=None, force=False):
                pos = round(pos, 0)
                scale = self.scale
                if (pos == round(scale.get_value(), 0)) and not force:
                        return
                scale.set_value(pos)

                if (pointer == None):
                        fix_tile, fix_offset = self.center
                else:
                        da = self.drawing_area
                        rect = da.get_allocation()
                        da_center = (rect.width / 2, rect.height / 2)

                        fix_tile = self.center[0]
                        fix_offset = self.center[1][0] + (pointer[0] - da_center[0]), \
                                        self.center[1][1] + (pointer[1] - da_center[1])
                        fix_tile, fix_offset = self.ctx_map.tile_adjustEx(self.current_zoom_level,
                                        fix_tile, fix_offset)

                        
                scala = 2 ** (self.current_zoom_level - pos)
                x = (fix_tile[0] * googleMaps.TILES_WIDTH + fix_offset[0]) * scala
                y = (fix_tile[1] * googleMaps.TILES_HEIGHT + fix_offset[1]) * scala
                if (pointer != None):
                        x = x - (pointer[0] - da_center[0])
                        y = y - (pointer[1] - da_center[1])

                new_center_tile = (int(x) / int(googleMaps.TILES_WIDTH),int(y) / int(googleMaps.TILES_HEIGHT))
                new_center_offset = (int(x) % int(googleMaps.TILES_WIDTH),int(y) % int(googleMaps.TILES_HEIGHT))
                self.center = new_center_tile, new_center_offset
                
                self.current_zoom_level = pos
                self.drawing_area.queue_draw()

        def get_zoom_level(self):
                return int(self.scale.get_value())

        def set_completion(self):
                completion = gtk.EntryCompletion()
                self.entry.set_completion(completion)
                completion_model = self.__create_completion_model()
                completion.set_model(completion_model)
                completion.set_text_column(0)
                self.completion = completion

        def confirm_clicked(self, button):
                location = self.entry.get_text()
                if (0 == len(location)):
                        print ("Need location")
                        return
                locations = self.ctx_map.get_locations()
                if (not location in locations.keys()):
                        if (not self.cb_offline.get_active()):
                                l = self.ctx_map.search_location(location)
                                if (False == l):
                                        print "Can't find %s in google map" % location
                                        self.entry.set_text("")
                                        return
                                location = l;
                                self.entry.set_text(l)
                                self.set_completion()
                                coord = self.ctx_map.get_locations()[location]
                        else:
                                print "Offline mode, cannot do search"
                                return
                else:
                        coord = locations[location]
                print "%s at %f, %f" % (location, coord[0], coord[1])

                self.center = (self.ctx_map.coord_to_tile(10, coord[0], coord[1]), (0,0))
                self.current_zoom_level = 10
                self.do_scale(10, force=True)

        def __create_completion_model(self):
                store = gtk.ListStore(gobject.TYPE_STRING)
                locations = self.ctx_map.get_locations().keys()

                for str in locations:
                        iter = store.append()
                        store.set(iter, 0, str)
                return store

        def __create_top_paned(self):
                frame = gtk.Frame("Query")
                hbox = gtk.HBox(False, 10)
                entry = gtk.Entry()
                bbox = gtk.HButtonBox()
                button = gtk.Button(stock='gtk-ok')
                button.connect('clicked', self.confirm_clicked)
                bbox.add(button)
                hbox.pack_start(entry)
                hbox.pack_start(bbox)

                self.cb_offline = gtk.CheckButton("Off line")
                vbox = gtk.VBox(False, 10)
                vbox.pack_start(hbox)
                vbox.pack_start(self.cb_offline)
                self.cb_offline.set_active(True)
                frame.add(vbox)
                self.entry = entry
                return frame

        def __create_left_paned(self):
                scale = gtk.VScale()
                scale.set_range(googleMaps.MAP_MIN_ZOOM_LEVEL, googleMaps.MAP_MAX_ZOOM_LEVEL)
#               scale.set_inverted(True)
                scale.set_property("update-policy", gtk.UPDATE_DISCONTINUOUS)
                scale.set_size_request(30, -1)
                scale.set_increments(1,1)
                scale.set_digits(0)
                scale.set_value(googleMaps.MAP_MAX_ZOOM_LEVEL)
                scale.connect("change-value", self.scale_change_value)
                scale.show()
                self.scale = scale
                return scale

        def __create_right_paned(self):
                da = gtk.DrawingArea()
                self.drawing_area = da
                da.connect("expose_event", self.expose_cb)
                da.add_events(gtk.gdk.SCROLL_MASK)
                da.connect("scroll-event", self.scroll_cb)

                da.add_events(gtk.gdk.BUTTON_PRESS_MASK)
                da.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
                da.add_events(gtk.gdk.BUTTON1_MOTION_MASK)

                da.connect('button-press-event', self.da_button_press)
                da.connect('button-release-event', self.da_button_release)
                da.connect('motion-notify-event', self.da_motion)
                da.show()
                return self.drawing_area

        def da_button_press(self, w, event):
                if (event.button != 1):
                        return
                self.draging = True
                #print "left-button-press at (%d, %d)" % (event.x, event.y)
                self.draging_start = (event.x, event.y)

        def da_button_release(self, w, event):
                if (event.button != 1):
                        return
                #print "left-button-release"
                self.draging = False

        def da_motion(self, w, event):
                x = event.x
                y = event.y
                if (x < 0):
                        return
                if (y < 0):
                        return
                rect = self.drawing_area.get_allocation()
                if (x > rect.width):
                        return
                if (y > rect.height):
                        return
                #print "mouse move: (%d, %d)" % (x, y)

                center_tile = self.center[0]
                self.center[1]
                
                center_offset = self.center[1][0] + (self.draging_start[0] - x), self.center[1][1] + (self.draging_start[1] - y)
                self.center = self.ctx_map.tile_adjustEx(self.get_zoom_level(),
                                center_tile, center_offset)
                self.draging_start = (x, y)
                self.drawing_area.queue_draw()
#               print "new draging_start: (%d, %d)" % self.draging_start
#               print "center: %d, %d, %d, %d" % (self.center[0][0],
#                               self.center[0][1],
#                               self.center[1][0],
#                               self.center[1][1])

        def expose_cb(self, drawing_area, event):
                online = not self.cb_offline.get_active()
                area = event.area
                #print "expose_cb: area x=%d, y=%d, width=%d, height=%d" % (area.x, area.y, area.width, area.height)
                rect = drawing_area.get_allocation()
                #print "canvas: x=%d, y=%d, w=%d, h=%d" % (rect.x, rect.y, rect.width, rect.height)

                area_center = (rect.width / 2, rect.height / 2)
                tl_point = (self.center[1][0] - area_center[0],
                                self.center[1][1] - area_center[1])
                #print "tl_point: (%d,%d)" % tl_point
                zl = self.get_zoom_level()
                tl_tile, tl_offset = self.ctx_map.tile_adjustEx(zl, self.center[0],
                                tl_point)

                x_pos = 0
                y_pos = 0
                tile_y_pos = tl_tile[1]
                tile_y_pos_inner = tl_offset[1]
                draw_height = googleMaps.TILES_HEIGHT - tl_offset[1]
                threads = []
                while (y_pos < rect.height):
                        tile_x_pos = tl_tile[0]
                        tile_x_pos_inner = tl_offset[0]
                        draw_width = googleMaps.TILES_WIDTH - tl_offset[0]
                        x_pos = 0
                        while (x_pos < rect.width):
                        #############################################
                                real_tile_x, real_tile_y = self.ctx_map.tile_adjust(self.get_zoom_level(), 
                                                (tile_x_pos, tile_y_pos))
                                if not (((area.x + area.width < x_pos) or (x_pos + draw_width < area.x)) or \
                                                ((area.y + area.height < y_pos) or (y_pos + draw_height < area.y))):
                                        th = GetTileThread(zl, real_tile_x, real_tile_y, tile_x_pos_inner,
                                                tile_y_pos_inner, x_pos, y_pos, draw_width, draw_height, online, 
                                                self.drawing_area.style.black_gc, self)
                                        threads.append(th)
                                        th.start()

                                x_pos += draw_width
                                tile_x_pos += 1
                                tile_x_pos_inner = 0
                                draw_width = googleMaps.TILES_WIDTH
                                if (x_pos + draw_width > rect.width):
                                        draw_width = rect.width - x_pos

                        y_pos += draw_height
                        tile_y_pos += 1
                        tile_y_pos_inner = 0
                        draw_height = googleMaps.TILES_HEIGHT
                        if (y_pos + draw_height > rect.height):
                                draw_height = rect.height - y_pos
                for th in threads:
                        th.join()

        def scroll_cb(self, widget, event):
                value = self.scale.get_value()
                if (event.direction == gtk.gdk.SCROLL_UP):
                        if ((value - 1) >= googleMaps.MAP_MIN_ZOOM_LEVEL):
                                self.do_scale(value - 1, self.drawing_area.get_pointer())
                else:
                        if ((value + 1) <= googleMaps.MAP_MAX_ZOOM_LEVEL):
                                self.do_scale(value + 1, self.drawing_area.get_pointer())

        def scale_change_value(self, range, scroll, value):
                if (value <= googleMaps.MAP_MAX_ZOOM_LEVEL) and (value >= googleMaps.MAP_MIN_ZOOM_LEVEL):
                        self.do_scale(value)
                return

        def __init__(self, parent=None):
                self.draging = False

                self.ctx_map = googleMaps.GoogleMaps()
                gtk.Window.__init__(self)
                try:
                        self.set_screen(parent.get_screen())
                except AttributeError:
                        self.connect("destroy", lambda *w: gtk.main_quit())

                vpaned = gtk.VPaned()
                hpaned = gtk.HPaned()

                vpaned.pack1(self.__create_top_paned(), False, False)
                hpaned.pack1(self.__create_left_paned(), False, False)
                hpaned.pack2(self.__create_right_paned(), True, True)
                vpaned.add2(hpaned)

                self.add(vpaned)
                self.set_border_width(10)
                self.set_size_request(450, 400)
                self.set_completion()
                self.show_all()

def main():
        MainWindow()
        gtk.main()

if __name__ == "__main__":
        main()

