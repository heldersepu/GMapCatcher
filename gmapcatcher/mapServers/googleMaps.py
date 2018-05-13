# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.googleMaps
# All the interaction with google.com

import re
import json
import urllib
import gmapcatcher.openanything as openanything
from gmapcatcher.mapConst import *

known_layers = {}
map_server_query = ["m", "k", "p", "h"]


## Returns a template URL for the GoogleMaps
def layer_url_template(layer, conf):
    if layer not in known_layers:
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
        return template % (coord[0], coord[1], 17 - coord[2])


## Parse maps.google.com/maps.
#  the return value is a url pattern like this:
#  http://mt%d.google.com/vt/lyrs=t@110&hl=en&x=%i&y=%i&z=%i
def parse_start_page(layer, html, conf):
    end_str = '&src=' + conf.google_src + '&hl=' + conf.language + '&x=%i&y=%i&z=%i'

    # srtPattern = 'https://mts0.googleapis.com/maps/vt?lyrs=m@352000000'
    # p = re.compile(srtPattern)
    # match = p.search(html)
    # if not match:
        # print "Cannot parse result"
        # return None
    if (layer == LAYER_SAT):
        return 'https://khms0.googleapis.com/kh?v=742&hl=en&' + end_str
    return 'https://mts0.googleapis.com/maps/vt?lyrs=%s@352000000' % map_server_query[layer] + end_str


def set_zoom(intZoom):
    if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
        return intZoom
    else:
        return 10


## Search a location in Google
def search_location(location, key='AIzaSyB3d6ZZvE0msnWbh9gX3bAN0bSFf4m8DuE'):
    print 'downloading the following location:', location
    try:
        oa = openanything.fetch('https://maps.googleapis.com/maps/api/geocode/json?key=%s&address=' % key +
            urllib.quote_plus(location), agent="Mozilla/5.0")
    except Exception:
        return 'error=Can not connect to http://maps.googleapis.com', None
    if oa['status'] != 200:
        return 'error=Can not connect to http://maps.googleapis.com', None

    try:
        data = json.loads(oa['data'])["results"][0]
        geo = data["geometry"]["location"]
        location = data["formatted_address"]
        return location, (float(geo['lat']), float(geo['lng']), 8)
    except Exception:
        return 'error=Location %s not found' % location, None
        
