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


class PortError(Exception):
    pass


class StreamBuffer(object):

    def __init__(self, terminator='\r\n'):
        self.terminator = terminator
        self.__buffer = ''

    def append(self, data):
        """ Append data to buffer, returns an array seperated by the terminator. """
        if len(data) == 0:
            return []

        segments = []
        buffer = self.__buffer + data
        terminator = self.terminator

        while True:
            pos = buffer.find(terminator)
            if pos == -1:
                break
            segments.append(buffer[:pos])
            buffer = buffer[pos + len(terminator):]

        self.__buffer = buffer
        return segments


class Port(object):
    """ ABS class for a nmea port """
    def __init__(self):
        self.__buffer = None

    def fileno(self):
        """ Get's the file descriptor associated with this port (compatable with select) """
        raise NotImplementedError

    def close(self):
        """ Close the nmea port """
        raise NotImplementedError

    def read(self, size=1):
        """ Read data from nmea port
        size - number of bytes to read
        return Data read from port
        """
        raise NotImplementedError

    def read_buffered(self, size=64):
        """ Read data from the nmea port into a buffer.
        return List of lines that where read
        """
        if not self.__buffer:
            self.__buffer = StreamBuffer()
        return self.__buffer.append(self.read(size))

    def read_line(self):
        """ Read a line from a nmea port
        return Line from the nmea port
        """
        line = ''
        while True:
            c = self.read()
            if not c: break # Timeout
            while c == '\r':
                c = self.read()
            if c == '\n': break
            line += c
        return line

    def write(self, data):
        """  Write data to nmea port
        data - Data to write to port
        """
        raise NotImplementedError

    def write_line(self, line):
        """ Write a line to the nmea port
        line - Line to write to the nmea port
        """
        self.write(line + '\r\n')
