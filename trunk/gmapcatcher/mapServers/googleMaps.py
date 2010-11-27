# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.googleMaps
# All the interaction with google.com

import re
import urllib
import gmapcatcher.openanything as openanything
from gmapcatcher.mapConst import *

known_layers = {}

## Returns a template URL for the GoogleMaps
def layer_url_template(layer, language):
    if layer not in known_layers:
        map_server_query = {"gmap":"m", "ghyb":"h", "gsat":"k", "gter":"p"}

        oa = openanything.fetch(
            'http://maps.google.com/maps?t=' + map_server_query[MAP_SERVICES[layer]["TextID"]])

        if oa['status'] != 200:
            print "Trying to fetch http://maps.google.com/maps but failed"
            return None
        html = oa['data']

        known_layers[layer] = parse_start_page(layer, html, language)
    return known_layers[layer]

## Returns the URL to the GoogleMaps tile
def get_url(counter, coord, layer, language):
    template = layer_url_template(layer, language)
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
def parse_start_page(layer, html, language):
    end_str = '&hl=' + language + '&x=%i&y=%i&z=%i'   

    # we first check the existence of the baseUrl in insertTiles
    hybrid = ''
    if layer == LAYER_HYBRID:
        hybrid = 'Hybrid'    
    uPattern = 'insertTiles.e."inlineTiles' + hybrid + '.*zoom,."(.*?)",'
    p = re.compile(uPattern)
    match = p.search(html)
    if match:
        baseUrl = json_dumps(match.group(1))
        baseUrl = baseUrl.replace('&hl=en&', '', 1)
        baseUrl = baseUrl.replace('0.', '%d.', 1)
        baseUrl = baseUrl.replace('"', '')
        return baseUrl + end_str

    # List of patterns add more as needed
    paList = ['http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v=([a-z0-9.]+)&',
              'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]lyrs=([a-z@0-9.]+)&',
              'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v\\\\x3d([a-z0-9.]+)\\\\x26']
    for srtPattern in paList:
        p = re.compile(srtPattern)
        match = p.search(html)
        if match: break
    if not match:
        print "Cannot parse result"
        return None

    return 'http://%s%%d.google.com/%s/v=%s' % tuple(match.groups()) + end_str


def set_zoom(intZoom):
    if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
        return intZoom
    else:
        return 10

## Search a location in Google
def search_location(location):
    print 'downloading the following location:', location
    try:
#        print 'url http://maps.google.com/maps?q=' + \
#               urllib.quote_plus(location)
        oa = openanything.fetch( 'http://maps.google.com/maps?q=' +
            urllib.quote_plus(location) )
    except Exception:
        return 'error=Can not connect to http://maps.google.com', None
    if oa['status']!=200:
        return 'error=Can not connect to http://maps.google.com', None

    match = 0
    html = oa['data']
#    print html
    if html.find('We could not understand the location') < 0:
        encpa = 'charset[ ]?= ?([^ ]+)"'
        p = re.compile(encpa, re.IGNORECASE)
        match = p.search(html)
        if match:
            encoding = match.group(1)
#            print "encoding", encoding
        else:
            encoding = "ASCII"
        # List of patterns to look for the location name
        paList = ['laddr:"([^"]+)"',
                  'daddr:"([^"]+)"']
        for srtPattern in paList:
            p = re.compile(srtPattern)
            match = p.search(html)
            if match: break

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
#        print "location from html", location
        location = unicode(location, encoding, errors='ignore')
        
        print encoding
        # following translations should be processed only if encoding is iso-8859-1.
        # when http headers will be solved move it to 'if encoding.upeer() == "ISO-8859-1":' 
            
        # Replace bad characters with the proper ones.
        # It would be better to use 'translate' instead of multiple 'replace' here,
        # but it didn't work for me (some problem with unicode strings).
        
        # characters defined in ISO-8859-1: http://en.wikipedia.org/wiki/ISO/IEC_8859-1 (Unicode: 0x31)
        # to be complete we should to translate missing chats 7f(127) - 9f(159) (Unicode: 0x29)
        # and maybe some others? I don't think so.
        
        location = location.replace(u"\u0080", u"\u20AC") # <control> (U+0080) -> € (Unicode: 0x20AC)
        # location = location.replace(u"\u0081", u"\uFFFD") # <control> (U+0081) -> � (Unicode: 0xFFFD)
        location = location.replace(u"\u0082", u"\u201A") # BREAK PERMITTED HERE (U+0082) -> ‚ (Unicode: 0x201A)
        location = location.replace(u"\u0083", u"\u0192") # NO BREAK HERE (U+0083) -> ƒ (Unicode: 0x192)
        location = location.replace(u"\u0084", u"\u201E") # <control> (U+0084) -> „ (Unicode: 0x201E)
        location = location.replace(u"\u0085", u"\u2026") # NEXT LINE (NEL) (U+0085) -> … (Unicode: 0x2026)
        location = location.replace(u"\u0086", u"\u2020") # START OF SELECTED AREA (U+0086) -> † (Unicode: 0x2020)
        location = location.replace(u"\u0087", u"\u2021") # END OF SELECTED AREA (U+0087) -> ‡ (Unicode: 0x2021)
        location = location.replace(u"\u0088", u"\u02C6") # CHARACTER TABULATION SET (U+0088) -> ˆ (Unicode: 0x2C6)
        location = location.replace(u"\u0089", u"\u2030") # CHARACTER TABULATION WITH JUSTIFICATION (U+0089) -> ‰ (Unicode: 0x2030)
        location = location.replace(u"\u008A", u"\u0160") # LINE TABULATION SET (U+008A) -> Š (Unicode: 0x160)
        location = location.replace(u"\u008B", u"\u2039") # PARTIAL LINE FORWARD (U+008B) -> ‹ (Unicode: 0x2039)
        location = location.replace(u"\u008C", u"\u0152") # PARTIAL LINE BACKWARD (U+008C) -> Œ (Unicode: 0x152)
        # location = location.replace(u"\u008D", u"\uFFFD") # REVERSE LINE FEED (U+008D) -> � (Unicode: 0xFFFD)
        location = location.replace(u"\u008E", u"\u017D") # SINGLE SHIFT TWO (U+008E) -> Ž (Unicode: 0x17D)
        # location = location.replace(u"\u008F", u"\uFFFD") # SINGLE SHIFT THREE (U+008F) -> � (Unicode: 0xFFFD)
        # location = location.replace(u"\u0090", u"\uFFFD") # DEVICE CONTROL STRING (U+0090) -> � (Unicode: 0xFFFD)
        location = location.replace(u"\u0091", u"\u2018") # PRIVATE USE ONE (U+0091) -> ‘ (Unicode: 0x2018)
        location = location.replace(u"\u0092", u"\u2019") # PRIVATE USE TWO (U+0092) -> ’ (Unicode: 0x2019)
        location = location.replace(u"\u0093", u"\u201C") # SET TRANSMIT STATE (U+0093) -> “ (Unicode: 0x201C)
        location = location.replace(u"\u0094", u"\u201D") # CANCEL CHARACTER (U+0094) -> ” (Unicode: 0x201D)
        location = location.replace(u"\u0095", u"\u2022") # MESSAGE WAITING (U+0095) -> • (Unicode: 0x2022)
        location = location.replace(u"\u0096", u"\u2013") # START OF GUARDED AREA (U+0096) -> – (Unicode: 0x2013)
        location = location.replace(u"\u0097", u"\u2014") # END OF GUARDED AREA (U+0097) -> — (Unicode: 0x2014)
        location = location.replace(u"\u0098", u"\u02DC") # START OF STRING (U+0098) -> ˜ (Unicode: 0x2DC)
        location = location.replace(u"\u0099", u"\u2122") # <control> (U+0099) -> ™ (Unicode: 0x2122)
        location = location.replace(u"\u009A", u"\u0161") # SINGLE CHARACTER INTRODUCER (U+009A) -> š (Unicode: 0x161)
        location = location.replace(u"\u009B", u"\u203A") # CONTROL SEQUENCE INTRODUCER (U+009B) -> › (Unicode: 0x203A)
        location = location.replace(u"\u009C", u"\u0153") # STRING TERMINATOR (U+009C) -> œ (Unicode: 0x153)
        # location = location.replace(u"\u009D", u"\uFFFD") # OPERATING SYSTEM COMMAND (U+009D) -> � (Unicode: 0xFFFD)
        location = location.replace(u"\u009E", u"\u017E") # PRIVACY MESSAGE (U+009E) -> ž (Unicode: 0x17E)
        location = location.replace(u"\u009F", u"\u0178") # APPLICATION PROGRAM COMMAND (U+009F) -> Ÿ (Unicode: 0x178)

#        print "unicode", location
        return location, (float(match.group('lat')), float(match.group('lng')), int(zoom))
    else:
        return 'error=Unable to get latitude and longitude of %s ' % location
