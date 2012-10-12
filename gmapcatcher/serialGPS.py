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


## Scans available serial ports (COMx on Windows, tty[AMA, S, USB], rfcomm on Linux)
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
            self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
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
            while not self.__stop.is_set():  # read buffer while stop is called
                if self.ser:  # if the serial port connection exists...
                    try:
                        self.buf += self.ser.read(40)  # read 40 characters from port to buffer
                    except TypeError:
                        pass
                    if '\n' in self.buf:  # if the buffer includes row change
                        lines = self.buf.split('\n')  # split the buffer by lines
                        for line in lines[0:-1]:  # and for the lines (except the last one, that is probably not complete)
                            self.dataHandler(line)  # handle data
                        self.buf = lines[-1]  # set the buffer to only include the last line
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
        if data[0] == '$GPRMC':
            try:
                self.fix.time = data[1]
            except:
                pass
            try:
                hemisphere = data[4]
            except:
                hemisphere = None
            if hemisphere == 'S':  # if on the southern hemisphere, latitude is negative
                try:
                    self.fix.latitude = -self.convertDegrees(float(data[3]))
                except:
                    pass
            else:
                try:
                    self.fix.latitude = self.convertDegrees(float(data[3]))
                except:
                    pass
            try:
                hemisphere = data[6]
            except:
                hemisphere = None
            if hemisphere == 'W':  # if on the western hemisphere, longitude is negative
                try:
                    self.fix.longitude = -self.convertDegrees(float(data[5]))
                except:
                    pass
            else:
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

        elif data[0] == '$GPGGA':
            try:
                self.fix.time = data[1]
            except:
                pass
            try:
                hemisphere = data[3]
            except:
                hemisphere = None
            if hemisphere == 'S':  # if on the southern hemisphere, latitude is negative
                try:
                    self.fix.latitude = -self.convertDegrees(float(data[2]))
                except:
                    pass
            else:
                try:
                    self.fix.latitude = self.convertDegrees(float(data[2]))
                except:
                    pass
            try:
                hemisphere = data[5]
            except:
                hemisphere = None
            if hemisphere == 'W':  # if on the western hemisphere, longitude is negative
                try:
                    self.fix.longitude = -self.convertDegrees(float(data[4]))
                except:
                    pass
            else:
                try:
                    self.fix.longitude = self.convertDegrees(float(data[4]))
                except:
                    pass
            try:
                self.fix.altitude = float(data[9])
            except:
                pass

        elif data[0] == '$GPGSA':
            try:
                self.fix.mode = int(data[2])
            except:
                pass

    def convertDegrees(self, degrees):
        return float(int(floor(degrees / 100)) + (degrees / 100 - int(floor(degrees / 100))) / 60 * 100)

if __name__ == '__main__':
    import time
    print serialPortScan()
    gps = SerialGPS('/dev/ttyUSB0', 4800)
    gps.start()
    time.sleep(10)
    gps.stop()
