# NMEA Toolkit
# Copyright (C) 2008 Tim Savage
#
# This file is part of the NMEA Toolkit.
#
# The NMEA Toolkit is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your option)
# any later version.
#
# The NMEA Toolkit is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# the NMEA Toolkit.  If not, see <http://www.gnu.org/licenses/>.

import serial

from _port import *


class SerialPort(Port):
    """ Serial instance of the NMEA port """

    def __init__(self, device='/dev/gps', baud=4800, timeout=3):
        super(SerialPort, self).__init__()
        self.ser = None
        self.device = device
        self.baud = baud
        self.timeout = timeout
        self.__open()

    def __open(self):
        """ Open the nmea port """
        try:
            self.ser = serial.Serial(
                port=self.device,
                baudrate=self.baud,
                timeout=self.timeout)
            self.ser.flush()
        except serial.SerialException: raise PortError("Unable to open port")

    def fileno(self):
        """ Get's the file descriptor associated with this port (compatable with select) """
        return self.ser.fileno()

    def close(self):
        """ Close the nmea port """
        if self.ser:
            self.ser.close()
            self.ser = None

    def read(self, size=1):
        """ Read data from nmea port
        size - number of bytes to read
        return Data read from port
        """
        return self.ser.read(size)

    def write(self, data):
        """ Write data to nmea port
        data - Data to write to port
        """
        return self.ser.write(data)

