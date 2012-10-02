## @package gmapcatcher.mapGPS
# GPS Support

available = True
try:
    import gps
    import serialGPS
except:
    available = False
import mapConst
import widgets.mapPixbuf as mapPixbuf
from threading import Event, Thread
import time
import mapUtils


class GPS:
    def __init__(self, gps_callback, conf):
        global available
        # GPS Disabled at start
        self.conf = conf
        self.mode = conf.gps_mode
        self.type = conf.gps_type
        self.location = None
        self.gps_callback = gps_callback
        self.pixbuf = self.get_marker_pixbuf()
        self.update_rate = float(conf.gps_update_rate)
        self.serial_port = conf.gps_serial_port
        self.baudrate = conf.gps_serial_baudrate
        self.gps_updater = None
        self.gpsfix = None
        self.gps_points = list()
        if self.mode != mapConst.GPS_DISABLED:
            self.startGPS()

    def startGPS(self):
        global available
        available = True
        if self.type == mapConst.TYPE_GPSD:
            try:
                # Open binding to GPS daemon
                self.gps_session = gps.gps()
                self.gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
                self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, gps_session=self.gps_session)
                if self.conf.gps_mode != mapConst.GPS_DISABLED:
                    self.gps_updater.start()
                    self.set_mode(self.conf.gps_mode)
            except:
                # No GPS connected
                available = False
        elif self.type == mapConst.TYPE_SERIAL:
            print 'serial started'
            try:
                self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, serial_port=self.serial_port, baudrate=self.baudrate)
                if self.conf.gps_mode != mapConst.GPS_DISABLED:
                    self.gps_updater.start()
                    self.set_mode(self.conf.gps_mode)
            except:
                available = False
        else:
            available = False

    def stop_all(self):
        try:
            self.gps_updater.cancel()
        except:
            pass

    ## Sets the behaviour of the GPS functionality
    def set_mode(self, mode):
        self.mode = mode
        if self.gps_updater:
            if mode == mapConst.GPS_DISABLED:
                self.gps_updater.cancel()
            elif not self.gps_updater.is_alive():
                self.startGPS()
        elif mode != mapConst.GPS_DISABLED:
            self.startGPS()

    ## Get GPS position
    def get_location(self):
        if self.mode != mapConst.GPS_DISABLED and self.gpsfix.latitude and self.gpsfix.longitude:
            return (self.gpsfix.latitude, self.gpsfix.longitude)
        return None

    ## Callback from the GPSUpdater
    def update(self, fix):
        self.gpsfix = fix
        # if distance between points is greater than defined in config or first point, append to gps_points
        if fix.mode != mapConst.MODE_NO_FIX and \
          (len(self.gps_points) == 0 or
          mapUtils.countDistanceFromLatLon(self.gps_points[-1], (fix.latitude, fix.longitude)) > (float(self.conf.gps_track_interval) / 1000)):
            self.gps_points.append((fix.latitude, fix.longitude))
        self.gps_callback()

    ## Load GPS marker image
    def get_marker_pixbuf(self):
        return mapPixbuf.getImage('marker_gps.png', 48, 48)


## Continuously updates GPS coordinates.
class GPSUpdater(Thread):
    def __init__(self, gps_type, interval, function, gps_session=None, serial_port=None, baudrate=None):
        global available
        Thread.__init__(self)
        self.gps_type = gps_type
        self.interval = interval
        self.function = function

        self.gps_session = gps_session
        self.serial_port = serial_port
        self.baudrate = baudrate

        self.finished = Event()
        self.event = Event()
        self.lastUpdate = time.time()

    def run(self):
        global available
        if self.gps_type == mapConst.TYPE_GPSD and self.gps_session:
            try:
                while not self.finished.is_set():
                    self.gps_session.next()
                    if time.time() - self.lastUpdate > self.interval:
                        self.function(self.gps_session.fix)
                        self.lastUpdate = time.time()
            except StopIteration:
                available = False
                print "GPSD has terminated"
        elif self.gps_type == mapConst.TYPE_SERIAL and self.serial_port and self.baudrate:
            sergps = serialGPS.SerialGPS(self.serial_port, self.baudrate)
            sergps.start()
            while not self.finished.is_set():
                time.sleep(self.interval)
                available = sergps.available
                self.function(sergps.fix)
            sergps.stop()
        else:
            available = False

    def cancel(self):
        self.finished.set()
        self.join(3)
