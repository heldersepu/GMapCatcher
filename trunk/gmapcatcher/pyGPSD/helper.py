# -*- coding: utf-8 -*-

import os

UNSPECIFIED=0
IMPERIAL=1
NAUTICAL=2
METRIC=3

DEG_dd = 0
DEG_ddmm = 1
DEG_ddmmss = 2

def gpsd_units():
    if os.environ.get('GPSD_UNITS', "") != "":
        if os.environ['GPSD_UNITS'] == "imperial":
            return IMPERIAL
        elif os.environ['GPSD_UNITS'] == 'nautical':
            return NAUTICAL
        else:
            return METRIC
    elif os.environ.get('MEASUREMENT', "") != "":
        if os.environ ['MEASUREMENT'] == "en_US":
            return IMPERIAL
        else:
            return METRIC
    elif os.environ.get('LANG', "") != "":
        if os.environ['LANG'] == "en_US":
            return IMPERIAL
        else:
            return METRIC
    else:
        return UNSPECIFIED

def deg_to_str(fmat, angle):
    if angle < 0 or angle > 360:
        return "nan"
    deg = int(angle)
    frac_deg = (angle - deg) * 1000000
    mins = int((angle - deg) * 60)
    sec = ((((angle - deg) * 60) - mins) * 60)
    if (fmat == DEG_dd):
        return "%3d.%06ld" % (deg, frac_deg)
    elif (fmat == DEG_ddmm):
        return "%3d° %02d%.4f'" % (deg, mins, sec / 60)
    elif (fmat == DEG_ddmmss):
        return "%3d° %02d' %.3f\"" % (deg, mins, sec)


    