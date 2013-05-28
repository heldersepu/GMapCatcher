#!/usr/bin/python
# -*- encoding: utf-8 -*-
available = True
try:
    import serial
except:
    available = False
from threading import Thread, Event
from math import floor
import platform
from mapConst import MODE_NO_FIX

BAUDRATES = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]


## Scans available serial ports
## (COMx on Windows, tty[AMA, S, USB], rfcomm on Linux)
def serialPortScan():
    availableSerialPorts = ['none']
    if platform.system() == 'Windows':
        for i in range(256):
            try:
                COMport = serial.Serial(i)
                availableSerialPorts.append(COMport.portstr)
                COMport.close()
            except:
                pass
    elif platform.system() == 'Linux':
        import os
        typicalPorts = ['ttyAMA', 'ttyS', 'ttyUSB', 'rfcomm']
        devs = os.listdir('/dev')
        for port in typicalPorts:
            for dev in devs:
                if dev.startswith(port):
                    availableSerialPorts.append('/dev/%s' % dev)
    return availableSerialPorts


## GPSd-compatible gpsfix
class gpsfix:
    def __init__(self):
        self.mode = MODE_NO_FIX
        self.time = None
        self.ept = None
        self.latitude = self.longitude = None
        self.epx = None
        self.epy = None
        self.altitude = None         # Meters
        self.epv = None
        self.track = None            # Degrees from true north
        self.speed = None            # Knots
        self.climb = None            # Meters per second
        self.epd = None
        self.eps = None
        self.epc = None
        self.satellites = 0          # Not in GPSd


## Serial port GPS -module for mapGPS.py
class SerialGPS(Thread):
    def __init__(self, port='/dev/ttyS0', baudrate=9600, timeout=3):
        Thread.__init__(self)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.buf = ''
        self.dataToProcess = list()
        self.fix = gpsfix()
        self.__stop = Event()
        self.available = False
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout)
            self.ser.flushInput()
            self.available = True
        except serial.SerialException:
            self.__stop.set()
            self.ser = None
            self.fix.mode = MODE_NO_FIX
            self.available = False
            print "Unable to open port"

    def run(self):
        try:
            # read buffer while stop is called
            while not self.__stop.is_set():
                # if the serial port connection exists...
                if self.ser:
                    try:
                        # read 40 characters from port to buffer
                        self.buf += self.ser.read(40)
                    except TypeError:
                        pass
                    # if the buffer includes row change
                    if '\n' in self.buf:
                        # split the buffer by lines
                        lines = self.buf.split('\n')
                        # and for the lines
                        # (except the last one, that is probably not complete)
                        for line in lines[0:-1]:
                            # handle data
                            self.dataHandler(line)
                        # set the buffer to only include the last line
                        self.buf = lines[-1]
                else:
                    self.__stop.set()
                    self.fix.mode == MODE_NO_FIX
                    self.available = False
                    self.stop()
        except serial.SerialException:
            self.fix.mode = MODE_NO_FIX
            self.available = False
            print "Unable to open port"
            self.stop()

    def stop(self):
        self.__stop.set()
        if self.ser:
            self.ser.close()

    ## Data handler for NMEA-data
    # currently handles $GPRMC, $GPGGA and $GPGSA
    def dataHandler(self, line):
        # print line  # for debug
        data = line.strip().split(',')

        # $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
        # 1: Fix taken time, UTC
        # 2: Status A=active or V=Void
        # 3: Latitude
        # 4: Latitude hemisphere
        # 5: Longitude
        # 6: Longitude hemisphere
        # 7: Speed over the ground in knots
        # 8: Track angle in degrees True
        # 9: Date DDMMYY
        # 10-11: Magnetic Variation
        if data[0] == '$GPRMC':
            try:
                self.fix.time = data[1]
            except:
                pass
            try:
                if data[2] == 'V':  # If data is VOID, report as NO_FIX
                    self.fix.mode = MODE_NO_FIX
            except:
                pass
            try:
                hemisphere = data[4]
            except:
                hemisphere = None
            # if on the southern hemisphere, latitude is negative
            if hemisphere == 'S':
                try:
                    self.fix.latitude = -self.convertDegrees(float(data[3]))
                except:
                    pass
            elif hemisphere:
                try:
                    self.fix.latitude = self.convertDegrees(float(data[3]))
                except:
                    pass
            try:
                hemisphere = data[6]
            except:
                hemisphere = None
            # if on the western hemisphere, longitude is negative
            if hemisphere == 'W':
                try:
                    self.fix.longitude = -self.convertDegrees(float(data[5]))
                except:
                    pass
            elif hemisphere:
                try:
                    self.fix.longitude = self.convertDegrees(float(data[5]))
                except:
                    pass
            try:
                self.fix.speed = float(data[7])
            except:
                pass
            try:
                self.fix.track = float(data[8])
            except:
                pass

        # $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
        # 1: Fix taken time, UTC
        # 2: Latitude
        # 3: Latitude hemisphere
        # 4: Longitude
        # 5: Longitude hemisphere
        # 6: Fix quality: 0 = invalid, 1 = GPS fix (SPS), 2 = DGPS fix
        # 7: Number of satellites being tracked
        # 8: Horizontal dilution of position
        # 9-10: Altitude, Meters, above mean sea level
        # 11-12: Height of geoid (mean sea level) above WGS84 ellipsoid
        # 13: time in seconds since last DGPS update
        # 14: DGPS station ID number
        elif data[0] == '$GPGGA':
            try:
                self.fix.time = data[1]
            except:
                pass
            try:
                hemisphere = data[3]
            except:
                hemisphere = None
            # if on the southern hemisphere, latitude is negative
            if hemisphere == 'S':
                try:
                    self.fix.latitude = -self.convertDegrees(float(data[2]))
                except:
                    pass
            elif hemisphere:
                try:
                    self.fix.latitude = self.convertDegrees(float(data[2]))
                except:
                    pass
            try:
                hemisphere = data[5]
            except:
                hemisphere = None
            # if on the western hemisphere, longitude is negative
            if hemisphere == 'W':
                try:
                    self.fix.longitude = -self.convertDegrees(float(data[4]))
                except:
                    pass
            elif hemisphere:
                try:
                    self.fix.longitude = self.convertDegrees(float(data[4]))
                except:
                    pass
            try:
                if int(data[6]) == 0:
                    self.fix.mode = MODE_NO_FIX
            except:
                pass
            try:
                self.fix.satellites = int(data[7])
            except:
                pass
            try:
                self.fix.altitude = float(data[9])
            except:
                pass

        # $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
        # 1: Auto selection of 2D or 3D fix (M = manual)
        # 2: 3D fix - values include: 1 = no fix, 2 = 2D fix, 3 = 3D fix
        # 3-14: PRNs of satellites used for fix (space for 12)
        # 15: PDOP (dilution of precision)
        # 16: Horizontal dilution of precision (HDOP)
        # 17: Vertical dilution of precision (VDOP)
        # 18: the checksum data, always begins with *
        elif data[0] == '$GPGSA':
            try:
                self.fix.mode = int(data[2])
            except:
                pass

    def convertDegrees(self, degrees):
        return float(
            int(floor(degrees / 100)) +
            (degrees / 100 - int(floor(degrees / 100))) / 60 * 100)

if __name__ == '__main__':
    import time
    print serialPortScan()
    gps = SerialGPS('/dev/ttyUSB0', 4800)
    gps.start()
    time.sleep(10)
    gps.stop()
