import math
from bisect import bisect_left

import pygtk
pygtk.require('2.0')
import gtk

from mapConst import *
from mapDownloader import MapDownloader
import googleMaps
import mapUtils
from gtkThread import *

NICE_GRADES=[ 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8 ]
def nice_round(f):
    n=math.ceil(math.log(f,10))
    p=f/10**n
    p=NICE_GRADES[bisect_left(NICE_GRADES,p)]
    return p*10**n

class DLWindow(gtk.Window):
    def __init__(self, coord, kmx, kmy, layer):
        # Validate the text on all the "input" widgets
        def insert_text(entry, text, length, position, max, isInt=True):
            # generate what the new text will be
            text = text[:length]
            pos = entry.get_position()
            old = entry.get_text()
            new_text = old[:pos] + text + old[pos:]

            # Allow the minus as the first char
            if new_text == "-":
                return
            # Allow a maximum number of chars
            elif (len(new_text) > max):
                entry.stop_emission('insert-text')
            else:
                # If an exception is raised the text is not good
                try:
                    if isInt:
                        int(new_text)
                    else:
                        float(new_text)
                except Exception:
                    entry.stop_emission('insert-text')

        def lbl(text):
            l = gtk.Label(text)
            l.set_justify(gtk.JUSTIFY_RIGHT)
            return l

        def _frame(strName, container, spacing = 5):
            frame = gtk.Frame(strName)
            vbox = gtk.VBox(False, spacing)
            vbox.set_border_width(spacing)
            vbox.pack_start(container)
            frame.add(vbox)
            return frame

        def _zoom(zoom0, zoom1):
            out_hbox = gtk.HBox(False, 50)
            out_hbox.set_border_width(10)
            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("min:"), False)
            a_zoom0 = gtk.Adjustment(zoom0, MAP_MIN_ZOOM_LEVEL,
                                     MAP_MAX_ZOOM_LEVEL, 1)
            self.s_zoom0 = gtk.SpinButton(a_zoom0)
            self.s_zoom0.connect('insert-text', insert_text, 2)
            self.s_zoom0.set_digits(0)
            in_hbox.pack_start(self.s_zoom0)
            out_hbox.pack_start(in_hbox)

            in_hbox = gtk.HBox(False, 20)
            in_hbox.pack_start(lbl("max:"), False)
            a_zoom1 = gtk.Adjustment(zoom1, MAP_MIN_ZOOM_LEVEL,
                                     MAP_MAX_ZOOM_LEVEL, 1)
            self.s_zoom1 = gtk.SpinButton(a_zoom1)
            self.s_zoom1.connect('insert-text', insert_text, 2)
            self.s_zoom1.set_digits(0)
            in_hbox.pack_start(self.s_zoom1)
            out_hbox.pack_start(in_hbox)
            hbox = gtk.HBox()
            hbox.set_border_width(10)
            hbox.pack_start(_frame(" Zoom ", out_hbox, 0))
            return hbox

        def _center(lat0, lon0):
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("latitude:"))
            self.e_lat0 = gtk.Entry()
            self.e_lat0.set_text("%.6f" % lat0)
            self.e_lat0.connect('insert-text', insert_text, 15, False)
            hbox.pack_start(self.e_lat0, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("longitude:"))
            self.e_lon0 = gtk.Entry()
            self.e_lon0.set_text("%.6f" % lon0)
            self.e_lon0.connect('insert-text', insert_text, 15, False)
            hbox.pack_start(self.e_lon0, False)
            vbox.pack_start(hbox)
            return _frame(" Center ", vbox)

        def _area(kmx, kmy):
            vbox = gtk.VBox(False, 5)
            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("width:"))
            self.e_kmx = gtk.Entry()
            self.e_kmx.set_text("%.6g" % kmx)
            self.e_kmx.connect('insert-text', insert_text, 10)
            hbox.pack_start(self.e_kmx, False)
            vbox.pack_start(hbox)

            hbox = gtk.HBox(False, 10)
            hbox.pack_start(lbl("height:"))
            self.e_kmy = gtk.Entry()
            self.e_kmy.set_text("%.6g" % kmy)
            self.e_kmy.connect('insert-text', insert_text, 10)
            hbox.pack_start(self.e_kmy, False)
            vbox.pack_start(hbox)
            return _frame(" Area (km) ", vbox)

        def _buttons():
            hbbox = gtk.HButtonBox()
            hbbox.set_border_width(10)
            hbbox.set_layout(gtk.BUTTONBOX_SPREAD)
            self.b_download = gtk.Button(stock=gtk.STOCK_HARDDISK)
            self.b_download.connect('clicked', self.run)
            hbbox.pack_start(self.b_download)

            self.b_cancel = gtk.Button(stock='gtk-cancel')
            self.b_cancel.connect('clicked', self.cancel)
            self.b_cancel.set_sensitive(False)
            hbbox.pack_start(self.b_cancel)
            return hbbox

        print "DLWindow(", coord, kmx, kmy, layer, ')'
        kmx = nice_round(kmx)
        kmy = nice_round(kmy)
        self.layer = layer
        gtk.Window.__init__(self)
        lat0 = coord[0]
        lon0 = coord[1]
        zoom0 = max(MAP_MIN_ZOOM_LEVEL, coord[2]-3)
        zoom1 = min(MAP_MAX_ZOOM_LEVEL, coord[2]+1)

        vbox = gtk.VBox(False)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(_center(lat0, lon0))
        hbox.pack_start(_area(kmx, kmy))
        vbox.pack_start(hbox)
        vbox.pack_start(_zoom(zoom0, zoom1))
        vbox.pack_start(_buttons())

        self.pbar = gtk.ProgressBar()
        self.pbar.set_text(" ")
        vbox.pack_start(self.pbar)
        self.add(vbox)

        self.set_title("GMapCatcher download")
        self.set_border_width(10)

        self.complete=[]
        self.processing=False
        self.gmap=None
        self.downloader=None
        self.connect('delete-event', self.on_delete)
        self.show_all()

    def run(self,w):
        if self.processing: return
        try:
            lat0 = float(self.e_lat0.get_text())
            lon0 = float(self.e_lon0.get_text())
            kmx = float(self.e_kmx.get_text())
            kmy = float(self.e_kmy.get_text())
            zoom0 = self.s_zoom0.get_value_as_int()
            zoom1 = self.s_zoom1.get_value_as_int()
            layer = self.layer
        except ValueError:
            d = gtk.MessageDialog(self, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
                    gtk.BUTTONS_CLOSE, "Some field contain non-numbers")
            d.run()
            d.destroy()
            return
        self.b_cancel.set_sensitive(True)
        self.b_download.set_sensitive(False)
        print ("lat0=%g lon0=%g kmx=%g kmy=%g zoom0=%d zoom1=%d layer=%d"
            % (lat0, lon0, kmx, kmy, zoom0, zoom1, layer))
        dlon=kmx*180/math.pi/(R_EARTH*math.cos(lat0*math.pi/180))
        dlat=kmy*180/math.pi/R_EARTH
        self.gmap=googleMaps.GoogleMaps() # creating our own gmap
        self.complete=[]
        self.downloader=MapDownloader(self.gmap)
        if zoom0>zoom1:
            zoom0,zoom1=zoom1,zoom0
        self.all_placed=False
        self.processing=True
        for zoom in xrange(zoom1, zoom0-1,-1):
            self.downloader.query_region_around_location(
                lat0,lon0,dlat,dlon,
                zoom,layer,
                gui_callback(self.tile_received))
        if self.downloader.qsize()==0:
            self.download_complete()
        self.all_placed=True

    def tile_received(self, coord, layer, filename):
        print "tile_received(", coord, layer, self.processing, self.downloader!=None,")"
        self.complete.append((coord, layer))
        ncomplete=len(self.complete)
        nqueued=self.downloader.qsize() if self.downloader else 0
        if nqueued==0 and self.all_placed:
            self.download_complete()
            return
        self.update_pbar("x=%d y=%d zoom=%d" % coord, ncomplete, ncomplete+nqueued)

    def update_pbar(self, text, pos, maxpos):
        self.pbar.set_text(text)
        self.pbar.set_fraction(float(pos)/maxpos)

    def download_complete(self):
        if self.downloader: self.downloader.stop_all()
        self.downloader=None
        self.processing=False
        self.b_cancel.set_sensitive(False)
        self.b_download.set_sensitive(True)
        self.update_pbar("Complete",0,1);

    def cancel(self,w):
        if self.downloader: self.downloader.stop_all()
        self.downloader=None
        self.processing=False
        self.b_cancel.set_sensitive(False)
        self.b_download.set_sensitive(True)
        self.update_pbar("Canceled",0,1);

    def on_delete(self,*params):
        if self.downloader: self.downloader.stop_all()
        return False

