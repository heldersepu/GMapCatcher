#! /usr/bin/env python

# Scan for serial ports.

# Part of pySerial (http://pyserial.sf.net)
# (C) 2002-2003 <cliechti@gmx.net>

# The scan function of this module tries to open each port number
# from 0 to 255 and it builds a list of those ports where this was
# successful.


import nmea.serial as serial

DEFAULT_BAUD = 4800

## Scan for available ports. return a list of tuples (num, name, NMEA)
def scan(baudrate):
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i, baudrate)
            intCount = 0
            # Test if the port has an NMEA device attached
            # NMEA sentence can be as long as 82 characters
            # NMEA sentence start with '$GP'
            NMEA = '$GP'
            for j in range(90):
                byte = s.read(1)
                if byte == NMEA[intCount]:
                    intCount += 1
                    if intCount == 3:
                        break
                else:
                    intCount = 0

            available.append((i, s.portstr, intCount == 3))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available

if __name__=='__main__':
    print "Found ports:"
    print "  #,  Name,  NMEA"
    print "--------------------"
    for n,s,b in scan(DEFAULT_BAUD):
        print "  %d,  %s,  %s" % (n,s,b)
