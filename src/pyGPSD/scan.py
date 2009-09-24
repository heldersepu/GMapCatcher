#! /usr/bin/env python

# Scan for serial ports.

# Part of pySerial (http://pyserial.sf.net)
# (C) 2002-2003 <cliechti@gmx.net>

# The scan function of this module tries to open each port number
# from 0 to 255 and it builds a list of those ports where this was
# successful.


import nmea.serial as serial
import threading

DEFAULT_BAUD = 4800

## Scan for available ports.
class PortScan:
    ## Test if the port has an NMEA device attached
    # NMEA sentence can be as long as 82 characters
    # NMEA sentence start with '$GP'
    def nmea_test(self, serial_port):
        NMEA = '$GP'
        intCount = 0
        for j in range(90):
            byte = serial_port.read(1)
            if byte == NMEA[intCount]:
                intCount += 1
                if intCount == 3:
                    break
            else:
                intCount = 0
        self.isNMEA = intCount == 3

    ## Initialise the scan
    def __init__(self, baudrate):
        self.available = []
        for i in range(256):
            try:
                self.isNMEA = False
                s = serial.Serial(i, baudrate)
                # Start the nmea_test in a thread with a 5 second timeout
                myThread = threading.Thread(self.nmea_test(s))
                myThread.setDaemon(1)
                myThread.start()
                myThread.join(5)
                self.available.append((i, s.portstr, self.isNMEA))
                s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass

    ## returns a list of tuples (num, name, NMEA)
    def found(self):
        return self.available

if __name__=='__main__':
    port_scan = PortScan(DEFAULT_BAUD)
    print "Found ports:"
    print "  #,  Name,  NMEA"
    print "--------------------"
    for n,s,b in port_scan.found():
        print "  %d,  %s,  %s" % (n,s,b)
    print "+------------------+"
