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
    def __init__(self, coord, kmx,kmy, layer):
        def lbl(text):
            l=gtk.Label(text)
            l.set_justify(gtk.JUSTIFY_RIGHT)
            return l
        print "DLWindow(",coord,kmx,kmy,layer,')'
        kmx=nice_round(kmx)
        kmy=nice_round(kmy)
        self.layer=layer
        gtk.Window.__init__(self)
        lat0=coord[0]
        lon0=coord[1]
        zoom0=max(MAP_MIN_ZOOM_LEVEL,coord[2]-3)
        zoom1=min(MAP_MAX_ZOOM_LEVEL,coord[2]+1)

        tbl=gtk.Table(rows=4, columns=4, homogeneous=False)
        tbl.set_col_spacings(10)
        tbl.set_row_spacings(10)

        tbl.attach(lbl("Center latitude:"),0,1,0,1)
        self.e_lat0=gtk.Entry()
        self.e_lat0.set_text("%.6f" % lat0)
        tbl.attach(self.e_lat0, 1,2,0,1)
        tbl.attach(lbl("longitude:"),2,3,0,1)
        self.e_lon0=gtk.Entry()
        self.e_lon0.set_text("%.6f" % lon0)
        tbl.attach(self.e_lon0, 3,4,0,1)

        tbl.attach(lbl("Area width (km):"),0,1,1,2)
        self.e_kmx=gtk.Entry()
        self.e_kmx.set_text("%.6g" % kmx)
        tbl.attach(self.e_kmx, 1,2,1,2)
        tbl.attach(lbl("Area height (km):"),2,3,1,2)
        self.e_kmy=gtk.Entry()
        self.e_kmy.set_text("%.6g" % kmy)
        tbl.attach(self.e_kmy, 3,4,1,2)

        tbl.attach(lbl("Zoom min:"),0,1,2,3)
        a_zoom0=gtk.Adjustment(zoom0,MAP_MIN_ZOOM_LEVEL,MAP_MAX_ZOOM_LEVEL,1)
        self.s_zoom0=gtk.SpinButton(a_zoom0)
        self.s_zoom0.set_digits(0)
        tbl.attach(self.s_zoom0, 1,2,2,3)
        tbl.attach(lbl("max:"),2,3,2,3)
        a_zoom1=gtk.Adjustment(zoom1,MAP_MIN_ZOOM_LEVEL,MAP_MAX_ZOOM_LEVEL,1)
        self.s_zoom1=gtk.SpinButton(a_zoom1)
        self.s_zoom1.set_digits(0)
        tbl.attach(self.s_zoom1, 3,4,2,3)

        self.b_download=gtk.Button(label="Download")
        tbl.attach(self.b_download, 1,2,3,4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=0)
        self.b_download.connect('clicked', self.run)

        self.b_cancel=gtk.Button(stock='gtk-cancel')
        tbl.attach(self.b_cancel, 3,4,3,4, xoptions=gtk.EXPAND|gtk.FILL, yoptions=0)
        self.b_cancel.connect('clicked', self.cancel)
        self.b_cancel.set_sensitive(False)

        self.pbar=gtk.ProgressBar()
        tbl.attach(self.pbar, 0,4,4,5, xoptions=gtk.EXPAND|gtk.FILL, yoptions=0)

        self.add(tbl)

        self.set_title("GMapCatcher download")
        self.set_border_width(10)
        self.set_size_request(600, 300)

        self.complete=[]
        self.processing=False
        self.gmap=None
        self.downloader=None
        self.connect('delete-event', self.on_delete)
        self.show_all()

    def run(self,w):
        if self.processing: return
        try:
            lat0=float(self.e_lat0.get_text())
            lon0=float(self.e_lon0.get_text())
            kmx=float(self.e_kmx.get_text())
            kmy=float(self.e_kmy.get_text())
            zoom0=self.s_zoom0.get_value_as_int()
            zoom1=self.s_zoom1.get_value_as_int()
            layer=self.layer
        except ValueError:
            d=gtk.MessageDialog(self,gtk.DIALOG_MODAL,gtk.MESSAGE_ERROR,gtk.BUTTONS_CLOSE,
                "Some field contain non-numbers")
            d.run()
            d.destroy()
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

