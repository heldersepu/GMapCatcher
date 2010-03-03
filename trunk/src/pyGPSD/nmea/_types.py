# -*- coding: utf-8 -*-
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

import decimal
import math


def to_dms(value, absolute=False):
    """ Split a float value into DMS (degree, minute, second) parts
    value - Float value to split
    absolute - Obtain the absolute value
    return tupple containing DMS values
    """
    invert = not absolute and value < 0
    value = abs(value)
    degree = int(math.floor(value))
    value = (value - degree) * 60
    minute = int(math.floor(value))
    second = (value - minute) * 60
    if invert: return (-degree, minute, second)
    else: return (degree, minute, second)


def to_dm(value, absolute=False):
    """ Split a float value into DM (degree, minute) parts
    value - Float value to split
    absolute - Obtain the absolute value
    return tupple containing DM values
    """
    invert = not absolute and value < 0
    value = abs(value)
    degree = int(math.floor(value))
    minute = (value - degree) * 60
    if invert: return (-degree, minute)
    else: return (degree, minute)


class latitude(float):
    """ Latitude value """

    __slots__ = []

    def __new__(cls, value=None):
        if value is None:
            return float.__new__(cls, 0.0)
        if isinstance(value, float):
            if value <= 90.0 and value >= -90.0:
                return float.__new__(cls, value)
            raise ValueError("Value %d out of range(-90.0, 90.0)" % value)
        raise ValueError("Expected type float or latitude")

    def __repr__(self):
        return "%02.3f" % self

    def __str__(self):
        result = "%02i°%02i'%02f\"" % to_dms(self, True)
        if self < 0: return result + 'S'
        else: return result + 'N'


class longitude(float):
    """ Longitude value """

    __slots__ = []

    def __new__(cls, value=None):
        if value is None:
            return float.__new__(cls, 0.0)
        if isinstance(value, float):
            if value <= 180.0 and value >= -180.0:
                return float.__new__(cls, value)
            raise ValueError("Value %d out of range(-180.0, 180.0)" % value)
        raise ValueError("Expected type float or longitude")

    def __repr__(self):
        return "%03.3f" % self

    def __str__(self):
        result = "%03i°%02i\'%02f\"" % to_dms(self, True)
        if self < 0: return result + 'W'
        else: return result + 'E'


class latlng(object):
    """ Latitude/Longitude pair """

    __slots__ = ['lat', 'lng'] # Define available parameters

    def __init__(self, value):
        if isinstance(value, tuple) and len(value) == 2:
            (lat, lng) = value
            self.lat = latitude(lat)
            self.lng = longitude(lng)
        elif isinstance(value, latlng):
            self.lat = latitude(value.lat)
            self.lng = longitude(value.lng)
        else:
            raise ValueError

    def __eq__(self, other):
        if not isinstance(other, self.__class__): raise TypeError
        return self.lat == other.lat and self.lng == other.lng

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "Latitude %s; Longitude %s" % (str(self.lat), str(self.lng))

    def get_value(self):
        """ Returns tuple lat/lng pair """
        return (self.lat, self.lng)


class satellite(object):
    """ Satellite value """

    __slots__ = ['prn', 'elevation', 'azimuth', 'snr', 'in_use']

    def __init__(self, value=None):
        if value is not None: self.update(value)
        self.in_use = False

    def __str__(self):
        return "PRN: %s; Elevation: %02d°; Azimuth: %03d°; SNR: %02ddB; In Use: %s;" % \
            (self.prn, self.elevation, self.azimuth, self.snr, str(self.in_use))

    def update(self, value):
        if isinstance(value, tuple):
            (prn, elevation, azimuth, snr) = value
            self.prn = prn
            self.elevation = elevation
            self.azimuth = azimuth
            self.snr = snr
        elif isinstance(value, satellite):
            self.prn = value.prn
            self.elevation = value.elevation
            self.azimuth = value.azimuth
            self.snr = value.snr
        else:
            raise ValueError

    def get_value(self):
        """ Return data as tuple """
        return (self.prn, self.elevation, self.azimuth, self.snr)


class velocity(float):
    """ Speed value (default is knots to match nmea spec) """

    def knots(self):
        """ value in knots """
        return self

    def kilometers_per_hour(self):
        """ value in kilometers per hour """
        return self * 1.852
    kmph = kilometers_per_hour

    def meters_per_second(self):
        """ value in meters per second """
        return self * 0.514444444

    def miles_per_hour(self):
        """ value in miles per hour """
        return self * 1.15077945
    mph = miles_per_hour

