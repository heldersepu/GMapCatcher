# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.googleMaps
# All the interaction with google.com

import re
import urllib
import gmapcatcher.openanything as openanything
from gmapcatcher.mapConst import *

known_layers = {}


## Returns a template URL for the GoogleMaps
def layer_url_template(layer, conf):
    if layer not in known_layers:
        map_server_query = ["m", "k", "p", "h"]

        oa = openanything.fetch(
            'http://maps.google.com/maps?t=' + map_server_query[layer])

        if oa['status'] != 200:
            print "Trying to fetch http://maps.google.com/maps but failed"
            return None
        html = oa['data']

        known_layers[layer] = parse_start_page(layer, html, conf)
    return known_layers[layer]


## Returns the URL to the GoogleMaps tile
def get_url(counter, coord, layer, conf):
    template = layer_url_template(layer, conf)
    if template:
        return template % (counter, coord[0], coord[1], 17 - coord[2])


## The json.dumps is desired but not required
def json_dumps(string):
    try:
        import json
        return json.dumps(string)
    except:
        return string


## Parse maps.google.com/maps.
#  the return value is a url pattern like this:
#  http://mt%d.google.com/vt/lyrs=t@110&hl=en&x=%i&y=%i&z=%i
def parse_start_page(layer, html, conf):
    end_str = '&src=' + conf.google_src + '&hl=' + conf.language + '&x=%i&y=%i&z=%i'

    hybrid = ''
    if layer == LAYER_HYB:
        hybrid = 'Hybrid'

    # List of patterns add more as needed
    paList = [
        '<div id=inlineTiles' + hybrid + ' dir=ltr>' +
        '<img src="http://([a-z]{2,3})[0-9].google.com/(.+?)&'
    ]
    for srtPattern in paList:
        p = re.compile(srtPattern)
        match = p.search(html)
        if match:
            break
    if not match:
        print "Cannot parse result"
        return None

    return 'http://%s%%d.google.com/%s' % tuple(match.groups()) + end_str


def set_zoom(intZoom):
    if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
        return intZoom
    else:
        return 10


## Search a location in Google
def search_location(location):
    print 'downloading the following location:', location
    try:
        oa = openanything.fetch('http://maps.google.com/maps?q=' +
            urllib.quote_plus(location), agent="Mozilla/5.0")
    except Exception:
        return 'error=Can not connect to http://maps.google.com', None
    if oa['status'] != 200:
        return 'error=Can not connect to http://maps.google.com', None

    match = 0
    html = oa['data']

    if html.find('We could not understand the location') < 0 and \
       html.find('Did you mean:') < 0:
        encpa = 'charset[ ]?= ?([^ ]+)"'
        p = re.compile(encpa, re.IGNORECASE)
        match = p.search(html)
        if match:
            encoding = match.group(1)
        else:
            encoding = "ASCII"
        # List of patterns to look for the location name
        paList = ["laddr:'([^']+)'",
                  "daddr:'([^']+)'",
                  'laddr:"([^"]+)"',
                  'daddr:"([^"]+)"']
        for srtPattern in paList:
            p = re.compile(srtPattern)
            match = p.search(html)
            if match:
                break

    if match:
        location = match.group(1)
    else:
        return 'error=Location %s not found' % location, None

    # List of patterns to look for the latitude & longitude
    paList = [
        'var zoom = (?P<zoom>[0-9]+);.*insertTiles.*,(?P<lat>[0-9.-]+),(?P<lng>[0-9.-]+),zoom',
        'center:{lat:(?P<lat>[0-9.-]+),lng:(?P<lng>[0-9.-]+)}.*zoom:(?P<zoom>[0-9.-]+)',
        'markers:.*lat:(?P<lat>[0-9.-]+),lng:(?P<lng>[0-9.-]+).*laddr:',
        'dtlsUrl:.*x26sll=(?P<lat>[0-9.-]+),(?P<lng>[0-9.-]+).*x26sspn',
    ]

    for srtPattern in paList:
        p = re.compile(srtPattern)
        match = p.search(html)
        if match:
            break

    if match:
        zoom = 10
        try:
            zoom = set_zoom(MAP_MAX_ZOOM_LEVEL - int(match.group('zoom')))
        except IndexError:
            p = re.compile('center:.*zoom:([0-9.-]+).*mapType:')
            m2 = p.search(html)
            if m2:
                zoom = set_zoom(MAP_MAX_ZOOM_LEVEL - int(m2.group(1)))
        location = unicode(location, encoding, errors='ignore')
        if encoding.upper() == "ISO-8859-1":
            location = _fix_iso_8859_1_issues(location)
        return location, (float(match.group('lat')), float(match.group('lng')), int(zoom))
    else:
        return 'error=Unable to get latitude and longitude of %s ' % location


def _fix_iso_8859_1_issues(location):
    # characters defined in ISO-8859-1: http://www.fileformat.info/info/charset/ISO-8859-1/list.htm
    # to be complete we should translate missing chars 7f(127) - 9f(159)
    # and maybe some others? I don't think so.
    translationTable = {
        # 0x7F: 0x007F,  # DELETE (U+007F) ->  (Unicode: 0x7F)
        0x80: 0x20AC,  # <control> (U+0080) -> € (Unicode: 0x20AC)
        # 0x81: 0xFFFD,  # <control> (U+0081) -> � (Unicode: 0xFFFD)
        0x82: 0x201A,  # BREAK PERMITTED HERE (U+0082) -> ‚ (Unicode: 0x201A)
        0x83: 0x0192,  # NO BREAK HERE (U+0083) -> ƒ (Unicode: 0x192)
        0x84: 0x201E,  # <control> (U+0084) -> „ (Unicode: 0x201E)
        0x85: 0x2026,  # NEXT LINE (NEL) (U+0085) -> … (Unicode: 0x2026)
        0x86: 0x2020,  # START OF SELECTED AREA (U+0086) -> † (Unicode: 0x2020)
        0x87: 0x2021,  # END OF SELECTED AREA (U+0087) -> ‡ (Unicode: 0x2021)
        0x88: 0x02C6,  # CHARACTER TABULATION SET (U+0088) -> ˆ (Unicode: 0x2C6)
        0x89: 0x2030,  # CHARACTER TABULATION WITH JUSTIFICATION (U+0089) -> ‰ (Unicode: 0x2030)
        0x8A: 0x0160,  # LINE TABULATION SET (U+008A) -> Š (Unicode: 0x160)
        0x8B: 0x2039,  # PARTIAL LINE FORWARD (U+008B) -> ‹ (Unicode: 0x2039)
        0x8C: 0x0152,  # PARTIAL LINE BACKWARD (U+008C) -> Œ (Unicode: 0x152)
        # 0x8D: 0xFFFD,  # REVERSE LINE FEED (U+008D) -> � (Unicode: 0xFFFD)
        0x8E: 0x017D,  # SINGLE SHIFT TWO (U+008E) -> Ž (Unicode: 0x17D)
        # 0x8F: 0xFFFD,  # SINGLE SHIFT THREE (U+008F) -> � (Unicode: 0xFFFD)
        # 0x90: 0xFFFD,  # DEVICE CONTROL STRING (U+0090) -> � (Unicode: 0xFFFD)
        0x91: 0x2018,  # PRIVATE USE ONE (U+0091) -> ‘ (Unicode: 0x2018)
        0x92: 0x2019,  # PRIVATE USE TWO (U+0092) -> ’ (Unicode: 0x2019)
        0x93: 0x201C,  # SET TRANSMIT STATE (U+0093) -> “ (Unicode: 0x201C)
        0x94: 0x201D,  # CANCEL CHARACTER (U+0094) -> ” (Unicode: 0x201D)
        0x95: 0x2022,  # MESSAGE WAITING (U+0095) -> • (Unicode: 0x2022)
        0x96: 0x2013,  # START OF GUARDED AREA (U+0096) -> – (Unicode: 0x2013)
        0x97: 0x2014,  # END OF GUARDED AREA (U+0097) -> — (Unicode: 0x2014)
        0x98: 0x02DC,  # START OF STRING (U+0098) -> ˜ (Unicode: 0x2DC)
        0x99: 0x2122,  # <control> (U+0099) -> ™ (Unicode: 0x2122)
        0x9A: 0x0161,  # SINGLE CHARACTER INTRODUCER (U+009A) -> š (Unicode: 0x161)
        0x9B: 0x203A,  # CONTROL SEQUENCE INTRODUCER (U+009B) -> › (Unicode: 0x203A)
        0x9C: 0x0153,  # STRING TERMINATOR (U+009C) -> œ (Unicode: 0x153)
        # 0x9D: 0xFFFD,  # OPERATING SYSTEM COMMAND (U+009D) -> � (Unicode: 0xFFFD)
        0x9E: 0x017E,  # PRIVACY MESSAGE (U+009E) -> ž (Unicode: 0x17E)
        0x9F: 0x0178,  # APPLICATION PROGRAM COMMAND (U+009F) -> Ÿ (Unicode: 0x178)
    }
    return location.translate(translationTable)
