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
        encpa = 'charset[ ]?= ?([^ ]+)'
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
#        print "unicode", location
        return location, (float(match.group('lat')), float(match.group('lng')), int(zoom))
    else:
        return 'error=Unable to get latitude and longitude of %s ' % location
