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

from datetime import datetime, timedelta
from nmea import *


class Track(object):

    def __init__(self, recordDelay=10, maxSize=3600, ignoreDuplicates=True, duplicateRange=0.0001):
        """ Constructor

        The default values allow for 10 hours worth of data recorded
        at 10 second intervals.

        recordDelay - Delay between recording data points
        maxSize - Maximum number of points to record
        ignoreDuplicates - Ignore entries that are very similar (ie moved a minimal distance)
        duplicateRange - Varience range within a duplicate is detected (adjust to account for
            subtle gps position drift)
        """
        self.recordDelay = recordDelay
        self.maxSize = maxSize
        self.ignoreDuplicates = ignoreDuplicates
        self.duplicateRange = duplicateRange
        self.positions = []
        self.latest = None

    def append(self, position, heading, timeStamp=None):
        """ Append position and heading information """
        if timeStamp is None: timeStamp = datetime.utcnow()

        self.latest = (timeStamp, position, heading)
        if len(self.positions):
            last = self.positions[0]
        else:
            last = None

        # Make sure we re in range
        if last is None or (timeStamp - last[0]).seconds >= self.recordDelay:
            self.positions.insert(0, self.latest)
            self.latest = None

        # Clear extra data
        if len(self.positions) > self.maxSize: pass

    def clear(self):
        """ Clear all items from track """
        self.positions = []
        self.latest = None

    def __len__(self):
        """ Return the length of the track """
        if self.latest is None: return len(self.positions)
        return len(self.positions) + 1

    def __getslice__(self, i, j):
        return self.positions[i:j]

    def __getitem__(self, i):
        return self.positions[i]

    def get_latest(self):
        if self.latest is None and len(self.positions) > 0:
            return self.positions

    def get_by_time(self, timeRange, now=datetime.utcnow()):
        """ Returns the last n items within the time range """
        result = []
        if self.latest is not None: result.append(self.latest)
        for position in self.positions:
            if (now - position[0]).seconds > timeRange: break
            result.append(position)
        return result



# Testing
if __name__ == '__main__':
    track = Track()

    print "Test 1"
    for position, heading in [
        ((12.0001, 123.0001), 0),
        ((12.0001, 123.0301), 0),
        ((12.0001, 123.0501), 0)]:
        track.append(latlng(position), heading)
        print len(track)
    track.clear()

    print "Test 2"
    for position, heading, timeStamp in [
        ((12.0001, 123.0001), 0, datetime(2008, 4, 22, 15, 49, 48)),
        ((12.0001, 123.0301), 0, datetime(2008, 4, 22, 15, 50, 19)),
        ((12.0001, 123.0501), 0, datetime(2008, 4, 22, 15, 50, 33)),
        ((12.0001, 123.0301), 0, datetime(2008, 4, 22, 15, 50, 38)),
        ((12.0001, 123.0301), 0, datetime(2008, 4, 22, 15, 50, 42)),
        ((12.0001, 123.0301), 0, datetime(2008, 4, 22, 15, 50, 45))]:
        track.append(latlng(position), heading, timeStamp)
        print len(track)
    print track.get_by_time(60, datetime(2008, 4, 22, 15, 51, 0))
    track.clear()
