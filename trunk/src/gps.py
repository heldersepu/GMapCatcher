#!/usr/bin/env python
# $Id$
#
# gps.py -- Python interface to GPSD.
#
import time, calendar, math, socket, sys, select

api_major_version = 3   # bumped on incompatible changes
api_minor_version = 1   # bumped on compatible changes

NaN = float('nan')
def isnan(x): return str(x) == 'nan'

ONLINE_SET      = 0x00000001
TIME_SET        = 0x00000002
TIMERR_SET      = 0x00000004
LATLON_SET      = 0x00000008
ALTITUDE_SET    = 0x00000010
SPEED_SET       = 0x00000020
TRACK_SET       = 0x00000040
CLIMB_SET       = 0x00000080
STATUS_SET      = 0x00000100
MODE_SET        = 0x00000200
HDOP_SET        = 0x00000400
VDOP_SET        = 0x00000800
PDOP_SET        = 0x00001000
TDOP_SET        = 0x00002000
GDOP_SET        = 0x00004000
HERR_SET        = 0x00008000
VERR_SET        = 0x00010000
PERR_SET        = 0x00020000
SATELLITE_SET   = 0x00040000
SPEEDERR_SET    = 0x00080000
TRACKERR_SET    = 0x00100000
CLIMBERR_SET    = 0x00200000
DEVICE_SET      = 0x00400000
DEVICELIST_SET  = 0x00800000
DEVICEID_SET    = 0x01000000
ERROR_SET       = 0x02000000
CYCLE_START_SET = 0x04000000
FIX_SET         = (TIME_SET|MODE_SET|TIMERR_SET|LATLON_SET|HERR_SET|ALTITUDE_SET|VERR_SET|TRACK_SET|TRACKERR_SET|SPEED_SET|SPEEDERR_SET|CLIMB_SET|CLIMBERR_SET)

STATUS_NO_FIX = 0
STATUS_FIX = 1
STATUS_DGPS_FIX = 2
MODE_NO_FIX = 1
MODE_2D = 2
MODE_3D = 3
MAXCHANNELS = 12
SIGNAL_STRENGTH_UNKNOWN = NaN

# The spec says 82, but some receivers (TN-200, GSW 2.3.2) output 86 characters
NMEA_MAX = 86

GPSD_PORT = 2947

class gpstimings:
    def __init__(self):
        self.sentence_tag = ""
        self.sentence_length = 0
        self.sentence_time = 0.0
        self.d_xmit_time = 0.0
        self.d_recv_time = 0.0
        self.d_decode_time = 0.0
        self.emit_time = 0.0
        self.poll_time = 0.0
        self.c_recv_time = 0.0
        self.c_decode_time = 0.0
    def d_received(self):
        if self.sentence_time:
            return self.d_recv_time + self.sentence_time
        else:
            return self.d_recv_time + self.d_xmit_time
    def collect(self, tag, length, sentence_time, xmit_time, recv_time, decode_time, poll_time, emit_time):
        self.sentence_tag = tag
        self.sentence_length = int(length)
        self.sentence_time = float(sentence_time)
        self.d_xmit_time = float(xmit_time)
        self.d_recv_time = float(recv_time)
        self.d_decode_time = float(decode_time)
        self.poll_time = float(poll_time)
        self.emit_time = float(emit_time)
    def __str__(self):
        return "%s\t%2d\t%2.6f\t%2.6f\t%2.6f\t%2.6f\t%2.6f\t%2.6f\t%2.6f\t%2.6f\n" % (
            self.sentence_tag,
            self.sentence_length,
            self.sentence_time,
            self.d_xmit_time,
            self.d_recv_time,
            self.d_decode_time,
            self.poll_time,
            self.emit_time,
            self.c_recv_time,
            self.c_decode_time
        )

class gpsfix:
    def __init__(self):
        self.mode = MODE_NO_FIX
        self.time = NaN
        self.ept = NaN
        self.latitude = self.longitude = 0.0
        self.eph = NaN
        self.altitude = NaN         # Meters
        self.epv = NaN
        self.track = NaN            # Degrees from true north
        self.speed = NaN            # Knots
        self.climb = NaN            # Meters per second
        self.epd = NaN
        self.eps = NaN
        self.epc = NaN

class gpsdata:
    "Position, track, velocity and status information returned by a GPS."

    class satellite:
        def __init__(self, PRN, elevation, azimuth, ss, used=None):
            self.PRN = PRN
            self.elevation = elevation
            self.azimuth = azimuth
            self.ss = ss
            self.used = used
        def __repr__(self):
            return "PRN: %3d  E: %3d  Az: %3d  Ss: %3d  Used: %s" % (
                self.PRN, self.elevation, self.azimuth, self.ss, "ny"[self.used]
            )

    def __init__(self):
        # Initialize all data members 
        self.online = 0                 # NZ if GPS on, zero if not

        self.valid = 0
        self.fix = gpsfix()

        self.status = STATUS_NO_FIX
        self.utc = ""

        self.satellites_used = 0        # Satellites used in last fix
        self.pdop = self.hdop = self.vdop = self.tdop = self.gdop = 0.0

        self.epe = 0.0

        self.satellites = []            # satellite objects in view
        self.await = self.parts = 0

        self.gps_id = None
        self.driver_mode = 0
        self.profiling = False
        self.timings = gpstimings()
        self.baudrate = 0
        self.stopbits = 0
        self.cycle = 0
        self.mincycle = 0
        self.device = None
        self.devices = []

    def __repr__(self):
        st = "Time:     %s (%s)\n" % (self.utc, self.fix.time)
        st += "Lat/Lon:  %f %f\n" % (self.fix.latitude, self.fix.longitude)
        if isnan(self.fix.altitude):
            st += "Altitude: ?\n"
        else:
            st += "Altitude: %f\n" % (self.fix.altitude)
        if isnan(self.fix.speed):
            st += "Speed:    ?\n"
        else:
            st += "Speed:    %f\n" % (self.fix.speed)
        if isnan(self.fix.track):
            st += "Track:    ?\n"
        else:
            st += "Track:    %f\n" % (self.fix.track)
        st += "Status:   STATUS_%s\n" % ("NO_FIX", "FIX", "DGPS_FIX")[self.status]
        st += "Mode:     MODE_%s\n" % ("ZERO", "NO_FIX", "2D", "3D")[self.fix.mode]
        st += "Quality:  %d p=%2.2f h=%2.2f v=%2.2f t=%2.2f g=%2.2f\n" % \
              (self.satellites_used, self.pdop, self.hdop, self.vdop, self.tdop, self.gdop)
        st += "Y: %s satellites in view:\n" % len(self.satellites)
        for sat in self.satellites:
          st += "    %r\n" % sat
        return st

class gps(gpsdata):
    "Client interface to a running gpsd instance."
    def __init__(self, host="127.0.0.1", port="2947", verbose=0):
        gpsdata.__init__(self)
        self.sock = None        # in case we blow up in connect
        self.eof = False
        self.buf = ''
        self.connect(host, port)
        self.verbose = verbose
        self.raw_hook = None

    def connect(self, host, port):
        """Connect to a host on a given port.

        If the hostname ends with a colon (`:') followed by a number, and
        there is no port specified, that suffix will be stripped off and the
        number interpreted as the port number to use.
        """
        if not port and (host.find(':') == host.rfind(':')):
            i = host.rfind(':')
            if i >= 0:
                host, port = host[:i], host[i+1:]
            try: port = int(port)
            except ValueError:
                raise socket.error, "nonnumeric port"
        if not port: port = GPSD_PORT
        #if self.debuglevel > 0: print 'connect:', (host, port)
        msg = "getaddrinfo returns an empty list"
        self.sock = None
        for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                #if self.debuglevel > 0: print 'connect:', (host, port)
                self.sock.connect(sa)
            except socket.error, msg:
                #if self.debuglevel > 0: print 'connect fail:', (host, port)
                self.close()
                continue
            break
        if not self.sock:
            raise socket.error, msg

    def set_raw_hook(self, hook):
        self.raw_hook = hook

    def close(self):
        if self.sock:
            self.sock.close()
        self.sock = None

    def __del__(self):
        self.close()

    def __unpack(self, buf):
        """Unpack a daemon response into the instance members"""
        self.fix.time = 0.0
        fields = buf.strip().split(",")
        if fields[0] == "GPSD":
            for field in fields[1:]:
                if not field or field[1] != '=':
                    continue
                cmd = field[0].upper()
                data = field[2:]
                if data[0] == "?":
                    continue
                if cmd == 'A':
                    self.fix.altitude = float(data)
                    self.valid |= ALTITUDE_SET
                elif cmd == 'B':
                    parts = data.split()
                    self.baudrate = int(parts[0])
                    self.stopbits = int(parts[3])
                elif cmd == 'C':
                    parts = data.split()
                    if len(parts) == 2:
                        (self.cycle, self.mincycle) = map(float, parts)
                    else:
                        self.mincycle = self.cycle = float(data)
                elif cmd == 'D':
                    self.utc = data
                    self.fix.time = isotime(self.utc)
                    self.valid |= TIME_SET
                elif cmd == 'E':
                    parts = data.split()
                    (self.epe, self.fix.eph, self.fix.epv) = map(float, parts)
                    self.valid |= HERR_SET | VERR_SET | PERR_SET
                elif cmd == 'F':
                    self.device = data
                elif cmd == 'I':
                    self.gps_id = data
                elif cmd == 'K':
                    self.devices = data[1:].split()
                elif cmd == 'M':
                    self.fix.mode = int(data)
                    self.valid |= MODE_SET
                elif cmd == 'N':
                    self.driver_mode = int(data)
                elif cmd == 'O':
                    fields = data.split()
                    if fields[0] == '?':
                        self.fix.mode = MODE_NO_FIX
                    else:
                        self.timings.sentence_tag = fields[0]
                        def default(i, vbit=0, cnv=float):
                            if fields[i] == '?':
                                return NaN
                            else:
                                try:
                                    value = cnv(fields[i])
                                except ValueError:
                                    return NaN
                                self.valid |= vbit
                                return value
                        # clear all valid bits that might be set again below
                        self.valid &= ~(
                            TIME_SET | TIMERR_SET | LATLON_SET | ALTITUDE_SET |
                            HERR_SET | VERR_SET | TRACK_SET | SPEED_SET |
                            CLIMB_SET | SPEEDERR_SET | CLIMBERR_SET | MODE_SET
                        )
                        self.utc = fields[1]
                        self.fix.time = default(1, TIME_SET)
                        if not isnan(self.fix.time):
                            self.utc = isotime(self.fix.time)
                        self.fix.ept = default(2, TIMERR_SET)
                        self.fix.latitude = default(3, LATLON_SET)
                        self.fix.longitude = default(4)
                        self.fix.altitude = default(5, ALTITUDE_SET)
                        self.fix.eph = default(6, HERR_SET)
                        self.fix.epv = default(7, VERR_SET)
                        self.fix.track = default(8, TRACK_SET)
                        self.fix.speed = default(9, SPEED_SET)
                        self.fix.climb = default(10, CLIMB_SET)
                        self.fix.epd = default(11)
                        self.fix.eps = default(12, SPEEDERR_SET)
                        self.fix.epc = default(13, CLIMBERR_SET)
                        if len(fields) > 14:
                            self.fix.mode = default(14, MODE_SET, int)
                        else:
                            if self.valid & ALTITUDE_SET:
                                self.fix.mode = MODE_2D
                            else:
                                self.fix.mode = MODE_3D
                            self.valid |= MODE_SET
                elif cmd == 'P':
                    (self.fix.latitude, self.fix.longitude) = map(float, data.split())
                    self.valid |= LATLON_SET
                elif cmd == 'Q':
                    parts = data.split()
                    self.satellites_used = int(parts[0])
                    (self.pdop, self.hdop, self.vdop, self.tdop, self.gdop) = map(float, parts[1:])
                    self.valid |= HDOP_SET | VDOP_SET | PDOP_SET | TDOP_SET | GDOP_SET
                elif cmd == 'S':
                    self.status = int(data)
                    self.valid |= STATUS_SET
                elif cmd == 'T':
                    self.fix.track = float(data)
                    self.valid |= TRACK_SET
                elif cmd == 'U':
                    self.fix.climb = float(data)
                    self.valid |= CLIMB_SET
                elif cmd == 'V':
                    self.fix.speed = float(data)
                    self.valid |= SPEED_SET
                elif cmd == 'X':
                    self.online = float(data)
                    self.valid |= ONLINE_SET
                elif cmd == 'Y':
                    satellites = data.split(":")
                    prefix = satellites.pop(0).split()
                    self.timings.sentence_tag = prefix.pop(0)
                    self.timings.sentence_time = prefix.pop(0)
                    if self.timings.sentence_time != "?":
                        self.timings.sentence_time = float(self.timings.sentence_time)
                    d1 = int(prefix.pop(0))
                    newsats = []
                    for i in range(d1):
                        newsats.append(gps.satellite(*map(int, satellites[i].split())))
                    self.satellites = newsats
                    self.valid |= SATELLITE_SET
                elif cmd == 'Z':
                    self.profiling = (data[0] == '1')
                elif cmd == '$':
                    self.timings.collect(*data.split())
        if self.raw_hook:
            self.raw_hook(buf);

    def waiting(self):
        """Return True if data is ready for the client."""
        try:
            (winput, woutput, wexceptions) = select.select([self.sock], [], [], 0)
        except select.error, socket.error:
            self.eof = True
            return False
        return len(winput) > 0

    def readlines(self):
        """Yield the next few complete lines. If no data is available,
        return an empty string."""
        if self.eof or not self.waiting():
            yield ''
        while self.waiting():
            buf = self.sock.recv(512)
            if buf:
                self.buf += buf
            else:
                self.eof = True
                break
        lines = self.buf.split('\r\n')
        for l in lines[:]:
            if l:
                yield l
                del lines[0]
        self.buf = '\r\n'.join(lines)

    def readstanzas(self):
        """Read a possibly multi-line response.
        Currently used for RTCM2 H responses."""
        stanza = []
        for frag in self.readlines():
            if self.eof:
                yield ''
            if frag:
                stanza.append(frag)
                if stanza[0][0] not in 'H' or '=' in stanza[0]:
                    yield frag
                    stanza = []
                if frag == '.':
                    yield '\r\n'.join(stanza)
                    stanza = []

    def poll(self):
        """Wait for and read data being streamed from gpsd.
        Return values: -1 on EOF, 1 on no more data, 0 otherwise"""
        for self.response in self.readstanzas():
            if self.eof:
                return -1
            if not self.response:
                return 1
            if self.verbose:
                sys.stderr.write("GPS DATA %r\n" % self.response)
            self.timings.c_recv_time = time.time()
            self.__unpack(self.response)
            if self.profiling:
                if self.timings.sentence_time != '?':
                    basetime = self.timings.sentence_time
                else:
                    basetime = self.timings.d_xmit_time
                self.timings.c_decode_time = time.time() - basetime
                self.timings.c_recv_time -= basetime
        return 0

    def send(self, commands):
        """Ship commands to the daemon."""
        if not commands.endswith("\n"):
            commands += "\n"
        self.sock.send(commands)

    def query(self, commands):
        """Send a command, get back a response."""
        self.send(commands)
        return self.poll()

# some multipliers for interpreting GPS output
METERS_TO_FEET  = 3.2808399
METERS_TO_MILES = 0.00062137119
KNOTS_TO_MPH    = 1.1507794

# EarthDistance code swiped from Kismet and corrected
# (As yet, this stuff is not in the libgps C library.)

def Deg2Rad(x):
    "Degrees to radians."
    return x * (math.pi/180)

def Rad2Deg(x):
    "Radians to degress."
    return x * (180/math.pi)

def CalcRad(lat):
    "Radius of curvature in meters at specified latitude."
    a = 6378.137
    e2 = 0.081082 * 0.081082
    # the radius of curvature of an ellipsoidal Earth in the plane of a
    # meridian of latitude is given by
    #
    # R' = a * (1 - e^2) / (1 - e^2 * (sin(lat))^2)^(3/2)
    #
    # where a is the equatorial radius,
    # b is the polar radius, and
    # e is the eccentricity of the ellipsoid = sqrt(1 - b^2/a^2)
    #
    # a = 6378 km (3963 mi) Equatorial radius (surface to center distance)
    # b = 6356.752 km (3950 mi) Polar radius (surface to center distance)
    # e = 0.081082 Eccentricity
    sc = math.sin(Deg2Rad(lat))
    x = a * (1.0 - e2)
    z = 1.0 - e2 * sc * sc
    y = pow(z, 1.5)
    r = x / y

    r = r * 1000.0      # Convert to meters
    return r

def EarthDistance((lat1, lon1), (lat2, lon2)):
    "Distance in meters between two points specified in degrees."
    x1 = CalcRad(lat1) * math.cos(Deg2Rad(lon1)) * math.sin(Deg2Rad(90-lat1))
    x2 = CalcRad(lat2) * math.cos(Deg2Rad(lon2)) * math.sin(Deg2Rad(90-lat2))
    y1 = CalcRad(lat1) * math.sin(Deg2Rad(lon1)) * math.sin(Deg2Rad(90-lat1))
    y2 = CalcRad(lat2) * math.sin(Deg2Rad(lon2)) * math.sin(Deg2Rad(90-lat2))
    z1 = CalcRad(lat1) * math.cos(Deg2Rad(90-lat1))
    z2 = CalcRad(lat2) * math.cos(Deg2Rad(90-lat2))
    a = (x1*x2 + y1*y2 + z1*z2)/pow(CalcRad((lat1+lat2)/2), 2)
    # a should be in [1, -1] but can sometimes fall outside it by
    # a very small amount due to rounding errors in the preceding
    # calculations (this is prone to happen when the argument points
    # are very close together).  Thus we constrain it here.
    if abs(a) > 1: a = 1
    elif a < -1: a = -1
    return CalcRad((lat1+lat2) / 2) * math.acos(a)

def MeterOffset((lat1, lon1), (lat2, lon2)):
    "Return offset in meters of second arg from first."
    dx = EarthDistance((lat1, lon1), (lat1, lon2))
    dy = EarthDistance((lat1, lon1), (lat2, lon1))
    if lat1 < lat2: dy *= -1
    if lon1 < lon2: dx *= -1
    return (dx, dy)

def isotime(s):
    "Convert timestamps in ISO8661 format to and from Unix time."
    if type(s) == type(1):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s))
    elif type(s) == type(1.0):
        date = int(s)
        msec = s - date
        date = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(s))
        return date + "." + `msec`[2:]
    elif type(s) == type(""):
        if s[-1] == "Z":
            s = s[:-1]
        if "." in s:
            (date, msec) = s.split(".")
        else:
            date = s
            msec = "0"
        # Note: no leap-second correction! 
        return calendar.timegm(time.strptime(date, "%Y-%m-%dT%H:%M:%S")) + float("0." + msec)
    else:
        raise TypeError

if __name__ == '__main__':
    import readline
    args = sys.argv[1:]
    if len(args) > 2:
        print 'Usage: gps.py [host [port]]'
        sys.exit(1)
    print "This is the exerciser for the Python gps interface."
    session = gps(*args)
    session.set_raw_hook(lambda s: sys.stdout.write(s + "\n"))
    try:
        while True:
            commands = raw_input("> ")
            session.query(commands+"\n")
            print session
    except EOFError:
        print "Goodbye!"
    del session

# gps.py ends here
