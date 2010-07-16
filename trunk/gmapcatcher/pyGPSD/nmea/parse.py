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

import array
import datetime

from _types import *
from constants import *


class ParseError(StandardError):
    pass


class CheckSumError(ParseError):
    def __init__(self, sentence, sum):
        ParseError.__init__(self, "Checksum failed (%s != %s)" % (sentence, sum))


class UTC(datetime.tzinfo):
    """ UTC Date time """

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)
utc = UTC()


class Sentence(object):
    """ Nmea sentence """

    __slots__ = ['_words','source','message'] # Define available parameters

    def __init__(self, sentence):
        if not sentence.startswith('$'):
            raise ParseError("Missing sentence prefix")

        # Find delimiter
        end = sentence.rfind('*')
        if end == -1: raise ParseError("Checksum delimiter not found")

        # Split the result
        checksum = sentence[end+1:]
        sentence = sentence[1:end]

        # Test the checksum
        csr = self.calculate_check_sum(sentence)
        if not checksum == csr:
            raise CheckSumError(sentence, csr)

        # Split the string
        self._words = sentence.split(',')
        source = self._words.pop(0)
        self.source = source[:2]
        self.message = source[2:]

    def __getitem__(self, indexOrSlice):
        """ Get a single item or slice """
        try:
            return self._words[indexOrSlice]
        except TypeError:
            return self._words[indexOrSlice.start:indexOrSlice.stop]

#    def __iter__(self):
#        """ Get iterator (ie for word in sentence: ) """
#        return iter(self._words)

    def __len__(self):
        """ Get length of sentence """
        return len(self._words)

    def calculate_check_sum(self, sentence):
        """ Calculate checksum of a nmea sentence (xor'd) """
        bytes = array.array('b', sentence)
        result = bytes[0]
        for i in xrange(1, len(bytes)):
            result ^= bytes[i]
        return "%02X" % result

    def get(self, index, default=None):
        """ Get an string item """
        return self._words[index]

    def get_int(self, index, default=None):
        """ Get an int item """
        value = self._words[index]
        if len(value) == 0: return default
        try:
            return int(value)
        except ValueError:
            raise ParseError("Word is not an int")

    def get_float(self, index, default=None):
        """ Get an float item """
        value = self._words[index]
        if len(value) == 0: return default
        try:
            return float(value)
        except ValueError:
            raise ParseError("Word is not a float")

    def get_velocity(self, index, default=None):
        """ Get a velocity item """
        return velocity(self.get_float(index, default))

    def get_latlng(self, startIndex):
        """ Get a latlng value, startIndex (covers 4 words) """
        # Parse Latitude
        lat = 0.0
        try:
            value = self._words[startIndex]
            lat = float(value[:2]) + float(value[2:]) / 60
            if self._words[startIndex + 1] == 'S': lat *= -1
        except ValueError:
            raise ParseError("Words are not a latitude")

        # Parse Longitude
        lng = 0.0
        try:
            value = self._words[startIndex + 2]
            lng = float(value[:3]) + float(value[3:]) / 60
            if self._words[startIndex + 3] == 'W': lng *= -1
        except ValueError:
            raise ParseError("Words are not a longitude")

        return latlng((lat, lng))

    def get_satellite(self, startIndex):
        """ Get a satellite info collection (covers 4 words) """
        prn = self.get(startIndex)
        elevation = self.get_int(startIndex+1, 0)
        azimuth = self.get_int(startIndex+2, 0)
        snr = self.get_int(startIndex+3, 0)
        return satellite((prn, elevation, azimuth, snr))

    def get_time(self, index, default=None):
        """ Get a time value """
        value = self.get(index)
        if len(value) < 6: return default
        try:
            hour = int(value[0:2])
            minute = int(value[2:4])
            second = int(value[4:6])
            if len(value) > 7:
                fraction = float(value[6:])
            else:
                fraction = 0
        except ValueError:
            raise ParseError("Word is not a valid time")
        return datetime.time(hour, minute, second, int(1000000 * fraction), utc)

    def get_date(self, index, default=None):
        """ Get a date value """
        value = self.get(index)
        if len(value) != 6: return default
        try:
            day = int(value[0:2])
            month = int(value[2:4])
            # Assume after the year 2000
            year = 2000 + int(value[4:6])
        except ValueError:
            raise ParseError("Word is not a valid date")
        return datetime.date(year, month, day)

    def get_list(self, startIndex, length):
        """ Get a list of values """
        return self._words[startIndex:startIndex+length]

