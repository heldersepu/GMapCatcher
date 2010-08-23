#!/usr/bin/python
'''
xgps -- test client for gpsd

usage: xgps [-D level] [-hV?] [-l degmfmt] [-u units] [server[:port[:device]]]
'''

gui_about = '''\
This is xgps, a test client for the gpsd daemon.

By Eric S. Raymond for the GPSD project, December 2009
'''
#
# This file is Copyright (c) 2010 by the GPSD project
# BSD terms apply: see the file COPYING in the distribution root for details.

import sys, os, re, math, time, exceptions, getopt, socket

import gobject, pygtk
pygtk.require('2.0')
import gtk

import gps, helper

class unit_adjustments:
    "Encapsulate adjustments for unit systems."
    def __init__(self, units=None):
        self.altfactor = gps.METERS_TO_FEET
        self.altunits = "ft"
        self.speedfactor = gps.MPS_TO_MPH
        self.speedunits = "mph"
        if units is None:
            units = helper.gpsd_units()
        if units in (helper.UNSPECIFIED, helper.IMPERIAL, "imperial", "i"):
            pass
        elif units in (helper.NAUTICAL, "nautical", "n"):
            self.altfactor = gps.METERS_TO_FEET
            self.altunits = "ft"
            self.speedfactor = gps.MPS_TO_KNOTS
            self.speedunits = "knots"
        elif units in (helper.METRIC, "metric", "m"):
            self.altfactor = 1
            self.altunits = "m"
            self.speedfactor = gps.MPS_TO_KPH
            self.speedunits = "kph"
        else:
            raise ValueError	# Should never happen

class SkyView(gtk.DrawingArea):
    "Satellite skyview, encapsulates pygtk's draw-on-expose behavior."
    # See <http://faq.pygtk.org/index.py?req=show&file=faq18.008.htp>
    HORIZON_PAD = 20	# How much whitespace to leave around horizon
    SAT_RADIUS = 5	# Diameter of satellite circle
    GPS_PRNMAX = 32	# above this number are SBAS satellites
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.set_size_request(400, 400)
        self.gc = None  # initialized in realize-event handler
        self.width  = 0 # updated in size-allocate handler
        self.height = 0 # updated in size-allocate handler
        self.connect('size-allocate', self.on_size_allocate)
        self.connect('expose-event',  self.on_expose_event)
        self.connect('realize',       self.on_realize)
        self.pangolayout = self.create_pango_layout("")
        self.satellites = []

    def on_realize(self, widget):
        self.gc = widget.window.new_gc()
        self.gc.set_line_attributes(1, gtk.gdk.LINE_SOLID,
                                    gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)

    def on_size_allocate(self, widget, allocation):
        self.width = allocation.width
        self.height = allocation.height
        self.diameter = min(self.width, self.height) - SkyView.HORIZON_PAD

    def set_color(self, spec):
        "Set foreground color for draweing."
        self.gc.set_rgb_fg_color(gtk.gdk.color_parse(spec))

    def draw_circle(self, widget, x, y, diam, filled=False):
        "Draw a circle centered on the specified midpoint."
        widget.window.draw_arc(self.gc, filled,
                               x - diam / 2, y - diam / 2,
                               diam, diam, 0, 360 * 64)

    def draw_line(self, widget, x1, y1, x2, y2):
        "Draw a line between specified points."
        widget.window.draw_lines(self.gc, [(x1, y1), (x2, y2)])

    def draw_square(self, widget, x, y, diam, filled=False):
        "Draw a square centered on the specified midpoint."
        widget.window.draw_rectangle(self.gc, filled,
                                     x - diam / 2, y - diam / 2,
                                     diam, diam)

    def draw_string(self, widget, x, y, letter, centered=True):
        "Draw a letter on the skyview."
        self.pangolayout.set_text(letter)
        if centered:
            (w, h) = self.pangolayout.get_pixel_size()
            x -= w/2
            y -= h/2
        self.window.draw_layout(self.gc, x, y, self.pangolayout)

    def pol2cart(self, az, el):
        "Polar to Cartesian coordinates within the horizon circle."
	az *= (math.pi/180)	# Degrees to radians
        # Exact spherical projection would be like this:
	# el = sin((90.0 - el) * DEG_2_RAD);
        el = ((90.0 - el) / 90.0);
        xout = int((self.width / 2) + math.sin(az) * el * (self.diameter / 2))
        yout = int((self.height / 2) - math.cos(az) * el * (self.diameter / 2))
        return (xout, yout)

    def on_expose_event(self, widget, event):
        self.set_color("white")
        widget.window.draw_rectangle(self.gc, True, 0,0, self.width,self.height)
        # The zenith marker
        self.set_color("gray")
        self.draw_circle(widget, self.width / 2, self.height / 2, 6)
        # The circle corresponding to 45 degrees elevation.
        # There are two ways we could plot this.  Projecting the sphere
        # on the display plane, the circle would have a diameter of
        # sin(45) ~ 0.7.  But the naive linear mapping, just splitting
        # the horizon diameter in half, seems to work better visually.
        self.draw_circle(widget, self.width / 2, self.height / 2,
                         int(self.diameter * 0.5))
        self.set_color("black")
        # The horizon circle
        self.draw_circle(widget, self.width / 2, self.height / 2,
                         self.diameter)
        self.set_color("gray")
        (x1, y1) = self.pol2cart(0, 0)
        (x2, y2) = self.pol2cart(180, 0)
        self.draw_line(widget, x1, y1, x2, y2)
        (x1, y1) = self.pol2cart(90, 0)
        (x2, y2) = self.pol2cart(270, 0)
        self.draw_line(widget, x1, y1, x2, y2)
        # The compass-point letters
        self.set_color("black")
        (x, y) = self.pol2cart(0, 0)
        self.draw_string(widget, x, y+10, "N")
        (x, y) = self.pol2cart(90, 0)
        self.draw_string(widget, x-10, y, "E")
        (x, y) = self.pol2cart(180, 0)
        self.draw_string(widget, x, y-10, "S")
        (x, y) = self.pol2cart(270, 0)
        self.draw_string(widget, x+10, y, "W")
        # The satellites
        for sat in self.satellites:
            (x, y) = self.pol2cart(sat.az, sat.el)
            if sat.ss < 10:
                self.set_color("Black")
            elif sat.ss < 30:
                self.set_color("Red")
            elif sat.ss < 35:
                self.set_color("Yellow");
            elif sat.ss < 40:
                self.set_color("Green3");
            else:
                self.set_color("Green1");
            if sat.PRN > SkyView.GPS_PRNMAX:
                self.draw_square(widget,
                                 x-SkyView.SAT_RADIUS, y-SkyView.SAT_RADIUS,
                                 2 * SkyView.SAT_RADIUS + 1, sat.used);
            else:
                self.draw_circle(widget,
                                 x-SkyView.SAT_RADIUS, y-SkyView.SAT_RADIUS,
                                 2 * SkyView.SAT_RADIUS + 1, sat.used);
            self.set_color("Black")
            self.draw_string(widget, x, y, str(sat.PRN), centered=False)
    def redraw(self, satellites):
        "Redraw the skyview."
        self.satellites = satellites
        self.queue_draw()

class AISView:
    "Encapsulate store and view objects for watching AIS data." 
    AIS_ENTRIES = 10
    DWELLTIME = 360
    def __init__(self, deg_type):
        "Initialize the store and view."
        self.deg_type = deg_type
        self.name_to_mmsi = {}
        self.named = {}
        self.store = gtk.ListStore(str,str,str,str,str,str)
        self.widget = gtk.ScrolledWindow()
        self.widget.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.view = gtk.TreeView(model=self.store)
        self.widget.set_size_request(-1, 300)
        self.widget.add_with_viewport(self.view)

        for (i, label) in enumerate(('#', 'Name:','Callsign:','Destination:', "Lat/Lon:", "Information")):
            column = gtk.TreeViewColumn(label)
            renderer = gtk.CellRendererText()
            column.pack_start(renderer)
            column.add_attribute(renderer, 'text', i)
            self.view.append_column(column)

    def enter(self, ais, name):
        "Add a named object (ship or station) to the store."
        if ais.mmsi in self.named:
            return False
        else:
            ais.entry_time = time.time()
            self.named[ais.mmsi] = ais
            self.name_to_mmsi[name] = ais.mmsi
            # Garbage-collect old entries
            try:
                for i in range(len(self.store)):
                    here = self.store.get_iter(i)
                    name = self.store.get_value(here, 1)
                    mmsi = self.name_to_mmsi[name]
                    if self.named[mmsi].entry_time < time.time() - AISView.DWELLTIME:
                        del self.named[mmsi]
                        if name in self.name_to_mmsi:
                            del self.name_to_mmsi[name]
                        self.store.remove(here)
            except (ValueError, KeyError):	# Invalid TreeIters throw these
                pass
            return True

    def latlon(self, lat, lon):
        "Latitude/longitude display in nice format."
        if lat < 0:
            latsuff = "S"
        elif lat > 0:
            latsuff = "N"
        else:
            latsuff = ""
        lat = abs(lat)
        lat = helper.deg_to_str(self.deg_type, lat)
        if lon < 0:
            lonsuff = "W"
        elif lon > 0:
            lonsuff = "E"
        else:
            lonsuff = ""
        lon = abs(lon)
        lon = helper.deg_to_str(helper.DEG_ddmmss, lon)
        return lat + latsuff + "/" + lon + lonsuff

    def update(self, ais):
        "Update the AIS data fields."
        if ais.type in (1, 2, 3, 18):
            if ais.mmsi in self.named:
                for i in range(len(self.store)):
                    here = self.store.get_iter(i)
                    name = self.store.get_value(here, 1)
                    if name in self.name_to_mmsi:
                        mmsi = self.name_to_mmsi[name]
                        if mmsi == ais.mmsi:
                            latlon = self.latlon(ais.lat, ais.lon)
                            self.store.set_value(here, 4, latlon)
        elif ais.type == 4:
            if self.enter(ais, ais.mmsi):
                where = self.latlon(ais.lat, ais.lon)
                self.store.prepend(
                    (ais.type, ais.mmsi, "(shore)", ais.timestamp, where, ais.epfd))
        elif ais.type == 5:
            if self.enter(ais, ais.shipname):
                self.store.prepend(
                    (ais.type, ais.shipname, ais.callsign, ais.destination, "", ais.shiptype))
        elif ais.type == 12:
            sender = ais.mmsi
            if sender in self.named:
                sender = self.named[sender].shipname
            recipient = ais.dest_mmsi
            if recipient in self.named and hasattr(self.named[recipient], "shipname"):
                recipient = self.named[recipient].shipname
            self.store.prepend(
                (ais.type, sender, "", recipient, "", ais.text))
        elif ais.type == 14:
            sender = ais.mmsi
            if sender in self.named:
                sender = self.named[sender].shipname
            self.store.prepend(
                (ais.type, sender, "", "(broadcast)", "", ais.text))
        elif ais.type in (19, 24):
            if self.enter(ais, ais.shipname):
                self.store.prepend(
                    (ais.type, ais.shipname, "(class B)", "", "", ais.shiptype))
        elif ais.type == 21:
            if self.enter(ais, ais.name):
                where = self.latlon(ais.lat, ais.lon)
                self.store.prepend(
                    (ais.type, ais.name, "(%s navaid)" % ais.epfd, "", where, ais.aid_type))
                    
class Base:
    gpsfields = (
        # First column
        ("Time", lambda s, r: s.update_time(r)),
        ("Latitude", lambda s, r: s.update_latitude(r)),
        ("Longitude", lambda s, r: s.update_longitude(r)),
        ("Altitude", lambda s, r: s.update_altitude(r)),
        ("Speed", lambda s, r: s.update_speed(r)),
        ("Climb", lambda s, r: s.update_climb(r)),
        ("Track", lambda s, r: s.update_track(r)),
        # Second column
        ("Status", lambda s, r: s.update_status(r)),
        ("EPX", lambda s, r: s.update_err(r, "epx")),
        ("EPY", lambda s, r: s.update_err(r, "epy")),
        ("EPV", lambda s, r: s.update_err(r, "epv")),
        ("EPS", lambda s, r: s.update_err(r, "eps")),
        ("EPC", lambda s, r: s.update_err(r, "epc")),
        ("EPD", lambda s, r: s.update_err(r, "epd")),
        )
    def __init__(self, deg_type):
        self.deg_type = deg_type
        self.conversions = unit_adjustments()
        self.saved_mode = -1
        self.ais_latch = False
  
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("xgps")
        self.window.connect("delete_event", self.delete_event)
        self.window.set_resizable(False)

        vbox = gtk.VBox(False, 0)
        self.window.add(vbox)

        self.window.connect("destroy", lambda w: gtk.main_quit())

        self.uimanager = gtk.UIManager()
        self.accelgroup = self.uimanager.get_accel_group()
        self.window.add_accel_group(self.accelgroup)
        self.actiongroup = gtk.ActionGroup('xgps')
        self.actiongroup.add_actions(
            [('Quit', gtk.STOCK_QUIT, '_Quit', None,
              'Quit the Program', lambda w: gtk.main_quit()),
             ('File', None, '_File'),
             ('View', None, '_View'),
             ('Units', None, '_Units')])
        self.actiongroup.add_toggle_actions(
            [('Skyview', None, '_Skyview', '<Control>s',
              'Enable Skyview', lambda a: self.view_toggle(a)),
             ('Responses', None, '_Responses', '<Control>r',
              'Enable Response Reports', lambda a: self.view_toggle(a)),
             ('GPS', None, '_GPS Data', '<Control>g',
              'Enable GPS Data', lambda a: self.view_toggle(a)),
             ('AIS', None, '_AIS Data', '<Control>a',
              'Enable AIS Data', lambda a: self.view_toggle(a)),
             ])
        self.actiongroup.add_radio_actions(
            [('Imperial', None, '_Imperial', '<Control>i',
              'Imperial units', 0),
             ('Nautical', None, '_Nautical', '<Control>n',
              'Nautical units', 1),
             ('Metric', None, '_Metric', '<Control>m',
              'Metric Units', 2),
             ], 0, lambda a, v: self.set_units(['i', 'n', 'm'][a.get_current_value()]))
        self.uimanager.insert_action_group(self.actiongroup, 0)
        self.uimanager.add_ui_from_string('''
<ui>
    <menubar name="MenuBar">
      <menu action="File">
        <menuitem action="Quit"/>
      </menu>
      <menu action="View">
        <menuitem action="Skyview"/>
        <menuitem action="Responses"/>
        <menuitem action="GPS"/>
        <menuitem action="AIS"/>
      </menu>
      <menu action="Units">
        <menuitem action="Imperial"/>
        <menuitem action="Nautical"/>
        <menuitem action="Metric"/>
      </menu>
    </menubar>
</ui>
''')
        self.uimanager.get_widget('/MenuBar/View/Skyview').set_active(True)
        self.uimanager.get_widget('/MenuBar/View/Responses').set_active(True)
        self.uimanager.get_widget('/MenuBar/View/GPS').set_active(True)
        self.uimanager.get_widget('/MenuBar/View/AIS').set_active(True)
        menubar = self.uimanager.get_widget('/MenuBar')
        vbox.pack_start(menubar, False)

        self.satbox = gtk.HBox(False, 0)
        vbox.add(self.satbox)

        skyframe = gtk.Frame(label="Satellite List")
        self.satbox.add(skyframe)

        self.satlist = gtk.ListStore(str,str,str,str,str)
        view = gtk.TreeView(model=self.satlist)

        for (i, label) in enumerate(('PRN:','Elev:','Azim:','SNR:','Used:')):
            column = gtk.TreeViewColumn(label)
            renderer = gtk.CellRendererText()
            column.pack_start(renderer)
            column.add_attribute(renderer, 'text', i)
            view.append_column(column)

        self.row_iters = []
        for i in range(gps.MAXCHANNELS):
            self.satlist.append(["", "", "", "", ""])
            self.row_iters.append(self.satlist.get_iter(i))

        skyframe.add(view)

        viewframe = gtk.Frame(label="Skyview")
        self.satbox.add(viewframe)
        self.skyview = SkyView()
        viewframe.add(self.skyview)

        self.rawdisplay = gtk.Entry()
        self.rawdisplay.set_editable(False)
        vbox.add(self.rawdisplay)

        self.dataframe = gtk.Frame(label="GPS data")
        datatable = gtk.Table(7, 4, False)
        self.dataframe.add(datatable)
        gpswidgets = []
        for i in range(len(Base.gpsfields)):
            if i < len(Base.gpsfields) / 2:
                colbase = 0
            else:
                colbase = 2
            label = gtk.Label(Base.gpsfields[i][0] + ": ")
            # Wacky way to force right alignment 
            label.set_alignment(xalign=1, yalign=0.5)
            datatable.attach(label, colbase, colbase+1, i % 7, i % 7 + 1)
            entry = gtk.Entry()
            datatable.attach(entry, colbase+1, colbase+2, i % 7, i % 7 + 1)
            gpswidgets.append(entry)
        vbox.add(self.dataframe)

        self.aisbox = gtk.HBox(False, 0)
        vbox.add(self.aisbox)

        aisframe = gtk.Frame(label="AIS Data")
        self.aisbox.add(aisframe)

        self.aisview = AISView(self.deg_type)
        aisframe.add(self.aisview.widget)

        self.window.show_all()
        # Hide the AIS window util user selects it.
        self.uimanager.get_widget('/MenuBar/View/AIS').set_active(False)
        self.aisbox.hide()

        self.view_name_to_widget = \
                                 {"Skyview": self.satbox,
                                  "Responses": self.rawdisplay,
                                  "GPS": self.dataframe,
                                  "AIS": self.aisbox}

        # Discard field labels and associate data hooks with their widgets
        Base.gpsfields = map(lambda ((label, hook), widget): (hook, widget),
                             zip(Base.gpsfields, gpswidgets))

    def view_toggle(self, action):
        #print "View toggle:", action.get_active(), action.get_name()
        if hasattr(self, 'view_name_to_widget'):
            if action.get_active():
                self.view_name_to_widget[action.get_name()].show()
            else:
                self.view_name_to_widget[action.get_name()].hide()
        # The effect we're after is to make the top-level window
        # resize itself to fit when we show or hide widgets.
        # This is undocumented magic to do that.
        self.window.resize(1, 1)

    def set_satlist_field(self, row, column, value):
        "Set a specified field in the satellite list."
        try:
            self.satlist.set_value(self.row_iters[row], column, value)
        except IndexError:
            sys.stderr.write("xgps: channel = %d, MAXCHANNELS = %d\n" % (row, gps.MAXCHANNELS))

    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    # State updates

    def update_time(self, data):
        if hasattr(data, "time"):
            return gps.isotime(data.time)
        else:
            return "n/a"

    def update_latitude(self, data):
        if data.mode >= gps.MODE_2D:
            lat = helper.deg_to_str(self.deg_type, abs(data.lat))
            if data.lat < 0:
                ns = 'S'
            else:
                ns = 'N'
            return "%s %s" % (lat, ns)
        else:
            return "n/a"

    def update_longitude(self, data):
        if data.mode >= gps.MODE_2D:
            lon = helper.deg_to_str(self.deg_type, abs(data.lon))
            if data.lon < 0:
                ew = 'W'
            else:
                ew = 'E'
            return "%s %s" % (lon, ew)
        else:
            return "n/a"

    def update_altitude(self, data):
        if data.mode >= gps.MODE_3D:
            return "%.3f %s" % (
                data.alt * self.conversions.altfactor,
                self.conversions.altunits)
        else:
            return "n/a"

    def update_speed(self, data):
        if hasattr(data, "speed"):
            return "%.3f %s" % (
                data.speed * self.conversions.speedfactor,
                self.conversions.speedunits)
        else:
            return "n/a"

    def update_climb(self, data):
        if hasattr(data, "climb"):
            return "%.3f %s" % (
                data.climb * self.conversions.speedfactor,
                self.conversions.speedunits)
        else:
            return "n/a"

    def update_track(self, data):
        if hasattr(data, "track"):
            return helper.deg_to_str(self.deg_type, abs(data.track))
        else:
            return "n/a"

    def update_err(self, data, errtype):
        if hasattr(data, errtype):
            return "%.3f %s" % (
                getattr(data, errtype) * self.conversions.altfactor,
                self.conversions.altunits)
        else:
            return "n/a"

    def update_status(self, data):
        if data.mode == gps.MODE_2D:
            status = "2D FIX"
        elif data.mode == gps.MODE_3D:
            status = "3D FIX"
        else:
            status = "NO FIX"
        if data.mode != self.saved_mode:
            self.last_transition = time.time()
            self.saved_mode = data.mode
        return status + " (%d secs)" % (time.time() - self.last_transition)

    def update_gpsdata(self, tpv):
        "Update the GPS data fields."
        for (hook, widget) in Base.gpsfields:
            if hook:	# Remove this guard when we have all hooks 
                widget.set_text(hook(self, tpv))

    def update_skyview(self, data):
        "Update the satellite list and skyview."
        satellites = data.satellites
        for (i, satellite) in enumerate(satellites): 
            self.set_satlist_field(i, 0, satellite.PRN)
            self.set_satlist_field(i, 1, satellite.el)
            self.set_satlist_field(i, 2, satellite.az)
            self.set_satlist_field(i, 3, satellite.ss)
            yesno = 'N'
            if satellite.used:
                yesno = 'Y'
            self.set_satlist_field(i, 4, yesno)
        for i in range(len(satellites), gps.MAXCHANNELS):
            for j in range(0, 5):
                self.set_satlist_field(i, j, "")
        self.skyview.redraw(satellites)

    # Preferences

    def set_units(self, system):
        "Change the display units."
        self.conversions = unit_adjustments(system)

    # I/O monitoring and gtk housekeeping

    def watch(self, daemon, device):
        "Set up monitoring of a daemon instance."
        self.daemon = daemon
        self.device = device
        gobject.io_add_watch(daemon.sock, gobject.IO_IN, self.handle_response)
        gobject.io_add_watch(daemon.sock, gobject.IO_ERR, self.handle_hangup)
        gobject.io_add_watch(daemon.sock, gobject.IO_HUP, self.handle_hangup)

    def handle_response(self, source, condition):
        "Handle ordinary I/O ready condition from the daemon."
        if self.daemon.poll() == -1:
            self.handle_hangup(source, condition)
        if self.daemon.valid & gps.PACKET_SET:
            if self.device and self.device != self.daemon.data["device"]:
                return True
            self.rawdisplay.set_text(self.daemon.response.strip())
            if self.daemon.data["class"] == "SKY":
                self.update_skyview(self.daemon.data)
            elif self.daemon.data["class"] == "TPV":
                self.update_gpsdata(self.daemon.data)
            elif self.daemon.data["class"] == "AIS":
                self.aisview.update(self.daemon.data)
                if self.ais_latch == False:
                    self.ais_latch = True
                    self.uimanager.get_widget('/MenuBar/View/AIS').set_active(True)
                    self.aisbox.show()
                    
        return True

    def handle_hangup(self, source, condition):
        "Handle hangup condition from the daemon."
        w = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                              flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                              buttons=gtk.BUTTONS_CANCEL)
        w.connect("destroy", lambda w: gtk.main_quit())
        w.set_markup("gpsd has stopped sending data.")
        w.run()
        gtk.main_quit()
        return True

    def main(self):
        gtk.main()

if __name__ == "__main__":
    (options, arguments) = getopt.getopt(sys.argv[1:], "D:hl:u:V?",
                                         ['verbose'])
    debug = 0
    degreefmt = 'd'
    unit_system = None
    for (opt, val) in options:
        if opt in '-D':
            debug = int(val)
        elif opt == '-l':
            degreeformat = val
        elif opt == '-u':
            unit_system = val
        elif opt in ('-?', '-h', '--help'):
            print __doc__
            sys.exit(0)
        elif opt == 'V':
            sys.stderr.write("xgps 1.0\n")
            sys.exit(0)

    degreefmt = {'d':helper.DEG_dd,
                 'm':helper.DEG_ddmm,
                 's':helper.DEG_ddmmss}[degreefmt]

    (host, port, device) = ("localhost", "2947", None)
    if len(arguments):
        args = arguments[0].split(":")
        if len(args) >= 1:
            host = args[0]
        if len(args) >= 2:
            port = args[1]
        if len(args) >= 3:
            device = args[2]

    base = Base(deg_type=degreefmt)
    base.set_units(unit_system)
    try:
        daemon = gps.gps(host=host,
                         port=port,
                         mode=gps.WATCH_ENABLE|gps.WATCH_JSON|gps.WATCH_SCALED,
                         verbose=debug)
        base.watch(daemon, device)
        base.main()
    except socket.error:
        w = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                              flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                              buttons=gtk.BUTTONS_CANCEL)
        w.set_markup("gpsd is not running.")
        w.run()
        w.destroy()

