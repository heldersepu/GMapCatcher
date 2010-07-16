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
    def nmea_test(self, *args):
        NMEA = '$GP'
        try:
            port = args[0]
            baudrate = args[1]
            s_port = serial.Serial(port, baudrate, timeout=0.5)
            s_port_read = s_port.read(90)
            isNMEA = s_port_read.find(NMEA) > -1
            self.available.append((port, s_port.portstr, isNMEA))
            s_port.close()  # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass

    ## Initialise the scan
    def __init__(self, baudrate):
        self.available = []
        self.threads =  []
        for i in range(256):
            # Start the nmea_test in a thread with a 5 second timeout
            myThread = threading.Thread(target=self.nmea_test,
                                        args=(i, baudrate))
            self.threads.append(myThread)
            myThread.start()

    ## returns a list of tuples (num, name, NMEA)
    def found(self):
        for myThread in self.threads:
            myThread.join(5)
        return self.available


if __name__=='__main__':
    print "Found ports:"
    print "  #,  Name,  NMEA"
    print "--------------------"
    port_scan = PortScan(DEFAULT_BAUD)
    for n,s,b in port_scan.found():
        print "  %d,  %s,  %s" % (n,s,b)
    print "+------------------+"
