#!/usr/bin/python
# -*- encoding: utf-8 -*-
import serial
from threading import Thread, Event
from math import floor
import platform
from mapConst import MODE_NO_FIX


def serialPortScan():
    """scans for available COM ports."""
    availableSerialPorts = []
    if platform.system() == 'Windows':
        for i in range(256):
            try:
                COMport = serial.Serial(i)
                availableSerialPorts.append(COMport.portstr)
                COMport.close()
            except serial.SerialException:
                pass
        availableSerialPorts.sort()
        return availableSerialPorts
    elif platform.system() == 'Linux':
        import os
        typicalPorts = ['ttyAMA', 'ttyS', 'ttyUSB']
        devs = os.listdir('/dev')
        for port in typicalPorts:
            for dev in devs:
                if dev.startswith(port):
                    availableSerialPorts.append('/dev/%s' % dev)
        availableSerialPorts.sort()
        return availableSerialPorts


class gpsfix:
    """ defines GPSd-compatible gpsfix -module """
    def __init__(self):
        self.mode = MODE_NO_FIX
        self.time = float()
        self.ept = float()
        self.latitude = self.longitude = 0.0
        self.epx = float()
        self.epy = float()
        self.altitude = float()         # Meters
        self.epv = float()
        self.track = float()            # Degrees from true north
        self.speed = float()            # Knots
        self.climb = float()            # Meters per second
        self.epd = float()
        self.eps = float()
        self.epc = float()

    def printFix(self):
        print 'Mode: %i' % self.mode
        print 'Time: %f' % self.time
        print 'Lat/Lon: %f %f' % (self.latitude, self.longitude)
        print 'Speed KN/KM: %f %f' % (self.speed, self.speed * 1.852)
        print 'Heading: %f' % self.track


class SerialGPS(Thread):
    """ Serial port GPS for GMapCatcher """
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
            self.ser.open()
            self.ser.flushInput()
            self.available = True
        except serial.SerialException:
            self.ser = None
            self.fix.mode = MODE_NO_FIX
            self.available = False
            print "Unable to open port"

    def run(self):
        try:
            while not self.__stop.is_set():  # read buffer while stop is called
                if self.ser:  # if the serial port connection exists...
                    self.buf += self.ser.read(20)  # read 20 characters from port to buffer
                    if '\n' in self.buf:  # if the buffer includes row change
                        lines = self.buf.split('\n')  # split the buffer by lines
                        for line in lines[0:-1]:  # and for the lines (except the last one, that is probably not complete)
                            self.dataHandler(line)  # handle data
                        self.buf = lines[-1]  # set the buffer to only include the last line
                else:
                    self.fix.mode == MODE_NO_FIX
                    self.available = False
        except serial.SerialException:
            self.fix.mode = MODE_NO_FIX
            self.available = False
            print "Unable to open port"

    def stop(self):
        self.__stop.set()
        self.join(5)
        self.ser.close()

    def dataHandler(self, line):
        """ data handler for NMEA-data
            only handles $GPRMC, $GPGGA and $GPGSA currently
            accepts only lines with correct amount of values """
        data = line.strip().split(',')
        if data[0] == '$GPRMC' and len(data) == 12:
            self.fix.time = float(data[1])
            if data[4] == 'S':  # if on the southern hemisphere, latitude is negative
                try:
                    self.fix.latitude = -self.convertDegrees(float(data[3]))
                except ValueError:
                    self.fix.latitude = 0.0
            else:
                try:
                    self.fix.latitude = self.convertDegrees(float(data[3]))
                except ValueError:
                    self.fix.latitude = 0.0
            if data[6] == 'W':  # if on the western hemisphere, longitude is negative
                try:
                    self.fix.longitude = -self.convertDegrees(float(data[5]))
                except ValueError:
                    self.fix.longitude = 0.0
            else:
                try:
                    self.fix.longitude = self.convertDegrees(float(data[5]))
                except ValueError:
                    self.fix.longitude = 0.0
            try:
                self.fix.speed = float(data[7])
            except:
                self.fix.speed = 0.0
            try:
                self.fix.track = float(data[8])
            except:
                self.fix.track = 0.0

        elif data[0] == '$GPGGA' and len(data) == 15:
            self.fix.time = float(data[1])
            if data[3] == 'S':  # if on the southern hemisphere, latitude is negative
                try:
                    self.fix.latitude = -self.convertDegrees(float(data[2]))
                except ValueError:
                    self.fix.latitude = 0.0
            else:
                try:
                    self.fix.latitude = self.convertDegrees(float(data[2]))
                except ValueError:
                    self.fix.latitude = 0.0
            if data[5] == 'W':  # if on the western hemisphere, longitude is negative
                try:
                    self.fix.longitude = -self.convertDegrees(float(data[4]))
                except ValueError:
                    self.fix.longitude = 0.0
            else:
                try:
                    self.fix.longitude = self.convertDegrees(float(data[4]))
                except ValueError:
                    self.fix.longitude = 0.0

        elif data[0] == '$GPGSA' and len(data) == 18:
            self.fix.mode = int(data[2])

    def convertDegrees(self, degrees):
        return float(int(floor(degrees / 100)) + (degrees / 100 - int(floor(degrees / 100))) / 60 * 100)

if __name__ == '__main__':
    import time
    print serialPortScan()
    gps = SerialGPS('/dev/ttyUSB0', 4800)
    gps.start()
    time.sleep(10)
    gps.stop()
