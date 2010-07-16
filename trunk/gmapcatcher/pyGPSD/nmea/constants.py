# NMEA Toolkit
# Copyright (C) 2008 Tim Savage
#
# This file is part of the NMEA Toolkit.
#
# The NMEA Toolkit is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your option
# any later version.
#
# The NMEA Toolkit is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# the NMEA Toolkit.  If not, see <http://www.gnu.org/licenses/>.


FIXMODE_UNKNOWN = ''
FIXMODE_AUTO   = 'A'
FIXMODE_MANUAL = 'M'

FIXTYPE_NA = 1  # Fix not available
FIXTYPE_2D = 2  # 2D Fix
FIXTYPE_3D = 3  # 3D Fix

FIXQUALITY_NA   = 0  # Not available/invalid
FIXQUALITY_GPS  = 1  # GPS Fix
FIXQUALITY_DIFF = 2  # Differential GPS fix
