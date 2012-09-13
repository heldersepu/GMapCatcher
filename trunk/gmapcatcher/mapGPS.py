## @package gmapcatcher.mapGPS
# GPS Support

try:
    import gps
    available = True
except ImportError:
    available = False

import mapConst
import mapPixbuf
from threading import Event, Thread
import time


class GPS:
    def __init__(self, gps_callback, update_rate, gps_mode):
        global available
        # GPS Disabled at start
        self.mode = gps_mode
        self.location = None
        self.gps_callback = gps_callback
        self.pixbuf = self.get_marker_pixbuf()
        self.update_rate = float(update_rate)

        try:
            # Open binding to GPS daemon
            self.gps_session = gps.gps()
            self.gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
            self.gps_updater = GPSUpdater(self.gps_session, self.update_rate, self.update)
            if gps_mode != mapConst.GPS_DISABLED:
                self.set_mode(gps_mode)
        except:
            # No GPS connected
            available = False

    def stop_all(self):
        self.gps_updater.cancel()

    ## Sets the behaviour of the GPS functionality
    def set_mode(self, mode):
        self.mode = mode
        self.gps_updater.cancel()
        if mode != mapConst.GPS_DISABLED:
            self.gps_updater = GPSUpdater(self.gps_session, self.update_rate, self.update)
            self.gps_updater.start()

    ## Get GPS position
    def get_location(self):
        if self.mode != mapConst.GPS_DISABLED:
            return self.location
        return None

    ## Callback from the GPSUpdater
    def update(self, fix):
        if fix.mode > gps.MODE_NO_FIX and \
                (fix.latitude is not None) and (fix.longitude is not None):
            # Store location
            self.location = (fix.latitude, fix.longitude)
            self.gps_callback(self.location, self.mode)

    ## Load GPS marker image
    def get_marker_pixbuf(self):
        return mapPixbuf.getImage('marker_gps.png', 48, 48)


## Continuously updates GPS coordinates.
class GPSUpdater(Thread):
    def __init__(self, gps_session, interval, function):
        Thread.__init__(self)
        self.gps_session = gps_session
        self.interval = interval
        self.function = function
        self.finished = Event()
        self.event = Event()
        self.lastUpdate = 0

    def run(self):
        try:
            while not self.finished.is_set():
                self.gps_session.next()
                if time.time() - self.lastUpdate > self.interval:
                    self.function(self.gps_session.fix)
                    self.lastUpdate = time.time()
        except StopIteration:
            print "GPSD has terminated"

    def cancel(self):
        self.finished.set()
