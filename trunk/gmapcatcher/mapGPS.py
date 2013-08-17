## @package gmapcatcher.mapGPS
# GPS Support

available = True
try:
    import gps
    import serialGPS
    from gmapcatcher.gps import misc
except:
    available = False
import mapConst
import widgets.mapPixbuf as mapPixbuf
from threading import Event, Thread
import time
from datetime import datetime, timedelta


if time.localtime().tm_isdst:
    offset = timedelta(seconds=time.altzone)
else:
    offset = timedelta(seconds=time.timezone)


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
                if self.mode != mapConst.GPS_DISABLED:
                    self.gps_updater.start()
            except:
                # No GPS connected
                available = False
        elif self.type == mapConst.TYPE_SERIAL:
            print 'serial started'
            try:
                self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, serial_port=self.serial_port, baudrate=self.baudrate)
                if self.mode != mapConst.GPS_DISABLED:
                    self.gps_updater.start()
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
                while not self.finished.isSet():
                    self.gps_session.next()
                    if time.time() - self.lastUpdate > self.interval:
                        self.function(self.gps_session.fix)
                        self.lastUpdate = time.time()
            except StopIteration:
                self.gps_session.fix.mode = mapConst.MODE_NO_FIX
                self.function(self.gps_session.fix)
                available = False
                print "GPSD has terminated"
        elif self.gps_type == mapConst.TYPE_SERIAL and self.serial_port and self.baudrate:
            sergps = serialGPS.SerialGPS(self.serial_port, self.baudrate)
            sergps.start()
            while not self.finished.isSet():
                time.sleep(self.interval)
                available = sergps.available
                if not available:
                    break
                self.function(sergps.fix)
            sergps.stop()
        else:
            available = False

    def cancel(self):
        self.finished.set()
        self.join(3)


def makeGPSTime(gps_time, gps_type, use_offset=False):
    d = None
    if gps_type == mapConst.TYPE_GPSD:
        if not isinstance(gps_time, int) and not isinstance(gps_time, float):
            gps_time = misc.isotime(gps_time)
        d = datetime.utcfromtimestamp(gps_time)
    else:
        dNow = datetime.utcnow()
        if '.' in gps_time:
            try:
                d = datetime.strptime(gps_time, '%H%M%S.%f')
            except TypeError:
                return
        else:
            try:
                d = datetime.strptime(gps_time, '%H%M%S')
            except TypeError:
                return
        d = d.replace(year=dNow.year, month=dNow.month, day=dNow.day)
    if use_offset:
        d = d - offset
    return d
