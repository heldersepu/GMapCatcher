## @package gmapcatcher.mapGPS
# GPS Support

import gps
import serialGPS
import mapConst
import mapPixbuf
from threading import Event, Thread
import time

TYPE_GPSD = 0
TYPE_SERIAL = 1
MODE_NO_FIX = 1
MODE_2D = 2
MODE_3D = 3

available = True


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
        if self.mode != mapConst.GPS_DISABLED:
            self.startGPS()

    def startGPS(self):
        global available
        if self.type == TYPE_GPSD:
            try:
                # Open binding to GPS daemon
                self.gps_session = gps.gps()
                self.gps_session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
                self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, gps_session=self.gps_session)
                if self.conf.gps_mode != mapConst.GPS_DISABLED:
                    self.set_mode(self.conf.gps_mode)
                    self.gps_updater.start()
            except:
                # No GPS connected
                available = False
        elif self.type == TYPE_SERIAL:
            try:
                self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, serial_port=self.serial_port, baudrate=self.baudrate)
                if self.conf.gps_mode != mapConst.GPS_DISABLED:
                    self.set_mode(self.conf.gps_mode)
                    self.gps_updater.start()
            except:
                available = False

    def stop_all(self):
        self.gps_updater.cancel()

    ## Sets the behaviour of the GPS functionality
    def set_mode(self, mode):
        self.mode = mode
        if mode == mapConst.GPS_DISABLED:
            self.gps_updater.cancel()
        elif not self.gps_updater.is_alive():
            self.startGPS()
        # self.gps_updater.cancel()
        # if mode != mapConst.GPS_DISABLED:
        #     if self.type == TYPE_GPSD:
        #         self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, gps_session=self.gps_session)
        #     elif self.type == TYPE_SERIAL:
        #         self.gps_updater = GPSUpdater(self.type, self.update_rate, self.update, serial_port=self.serial_port, baudrate=self.baudrate)
        #     self.gps_updater.start()

    ## Get GPS position
    def get_location(self):
        if self.mode != mapConst.GPS_DISABLED:
            return self.location
        return None

    ## Callback from the GPSUpdater
    def update(self, fix):
        if fix.mode > MODE_NO_FIX and \
                (fix.latitude is not None) and (fix.longitude is not None):
            # Store location
            self.location = (fix.latitude, fix.longitude)
            self.gps_callback(self.location, self.mode, True)
        else:
            self.location = (fix.latitude, fix.longitude)
            self.gps_callback(self.location, self.mode, False)

    ## Load GPS marker image
    def get_marker_pixbuf(self):
        return mapPixbuf.getImage('marker_gps.png', 48, 48)


## Continuously updates GPS coordinates.
class GPSUpdater(Thread):
    def __init__(self, type, interval, function, gps_session=None, serial_port=None, baudrate=None):
        global available
        Thread.__init__(self)
        self.gps_type = type
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
        if self.gps_type == TYPE_GPSD and self.gps_session:
            try:
                while not self.finished.is_set():
                    self.gps_session.next()
                    if time.time() - self.lastUpdate > self.interval:
                        self.function(self.gps_session.fix)
                        self.lastUpdate = time.time()
            except StopIteration:
                available = False
                print "GPSD has terminated"
        elif self.gps_type == TYPE_SERIAL and self.serial_port and self.baudrate:
            print 'serial started'
            sergps = serialGPS.SerialGPS(self.serial_port, self.baudrate)
            sergps.start()
            while not self.finished.is_set():
                available = sergps.available
                self.function(sergps.fix)
                time.sleep(self.interval)
            sergps.stop()

    def cancel(self):
        self.finished.set()
        self.join(3)
