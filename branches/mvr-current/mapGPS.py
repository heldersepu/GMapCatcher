## @package mapGPS
# GPS Support

try:
    import gps
    available = True
except ImportError:
    available = False

from threading import Event, Thread
import os
import gtk
import mapConst

class GPS:
    def __init__(self, center_callback, marker_callback):
        global available
        # GPS Disabled at start
        self.mode = mapConst.GPS_DISABLED
        self.location = None
        self.center_callback = center_callback
        self.marker_callback = marker_callback
        self.pixbuf = self.get_marker_pixbuf()

        try:
            # Open binding to GPS daemon
            self.gps_session = gps.gps()
            self.gps_updater = GPSUpdater(1.0, self.update)
        except:
            # No GPS connected
            available = False

    def stop_all(self):
        self.gps_updater.cancel()

    ## Sets the behaviour of the GPS functionality
    def set_mode(self, mode):
        self.mode = mode
        self.gps_updater.cancel()
        if mode == mapConst.GPS_MARKER:
            self.gps_updater = GPSUpdater(1.0, self.update)
            self.gps_updater.start()
        elif mode == mapConst.GPS_CENTER:
            self.gps_updater = GPSUpdater(1.0, self.update)
            self.gps_updater.start()

    ## Get GPS position
    def get_location(self):
        if self.mode == mapConst.GPS_MARKER or \
           self.mode == mapConst.GPS_CENTER:
            return self.location
        return None

    ## Callback from the GPSUpdater
    def update(self):
        # Make new reading from GPS device
        self.gps_session.query('admosy')
        #print "GPS: Lat/Long: ", self.gps_session.fix.latitude, self.gps_session.fix.longitude
        self.location = (self.gps_session.fix.latitude, self.gps_session.fix.longitude)

        if self.mode == mapConst.GPS_CENTER:
            self.center_callback(self.location)
        if self.mode == mapConst.GPS_MARKER:
            self.marker_callback()

	## Load GPS marker image
    def get_marker_pixbuf(self):
        filename = 'marker_gps.png'
        if (os.path.exists(filename)):
            w = gtk.Image()
            w.set_from_file(filename)
            try:
                return w.get_pixbuf()
            except ValueError:
                print "File corrupted: %s" % filename
				
class GPSUpdater(Thread):
    """Continiously updates GPS coordinates.
    """
    def __init__(self, interval, function):
        Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.finished = Event()
        self.event = Event()

    def run(self):
        while not self.finished.is_set():
            self.event.wait(self.interval)
            if not self.finished.is_set() and not self.event.is_set():
                self.function()

    def cancel(self):
        self.finished.set()
        self.event.set()

