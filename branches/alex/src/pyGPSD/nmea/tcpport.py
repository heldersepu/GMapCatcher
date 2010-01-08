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

import socket

from _port import *


class TcpPort(Port):
    """ TCP instance of the GPS port """

    def __init__(self, host='localhost', port=11000, timeout=3):
        super(TcpPort, self).__init__()
        self.sock = None
        self.address = (host, port)
        self.timeout = timeout
        self.__open()

    def __open(self):
        """ Open the nmea port """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)
        self.sock.settimeout(self.timeout)

    def fileno(self):
        """ Get's the file descriptor associated with this port (compatable with select) """
        return self.sock.fileno()

    def close(self):
        """ Close the nmea port """
        if self.sock:
            self.sock.close()
            self.sock = None

    def read(self, size=1):
        """ Read data from nmea port
        size - number of bytes to read
        return Data read from port
        """
        try:
            return self.sock.recv(size)
        except socket.error:
            return ''

    def write(self, data):
        """ Write data to nmea port
        data - Data to write to port
        """
        return self.sock.send(data)
