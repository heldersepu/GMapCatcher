## @package gmapcatcher.mapServers.googleMapMaker
# All the interaction with Google Map Maker

import re
import gmapcatcher.openanything as openanything

known_layers = {}


## Returns a template URL for the Google Map Maker
def layer_url_template(layer):
    if layer not in known_layers:
        known_layers[layer] = 'http://mt%d.google.com/vt/hl=x-local&source=mapmaker&x=%i&y=%i&z=%i'
    return known_layers[layer]


## Returns the URL to the Google Map Maker tile
def get_url(counter, coord, layer, conf):
    return layer_url_template('gwm') % \
        (counter, coord[0], coord[1], 17 - coord[2])


## Parse http://www.google.com/mapmaker.
#  the return value is a number
def parse_page():
    gwmNum = '1170'
    oa = openanything.fetch('http://www.google.com/mapmaker')
    if oa['status'] != 200:
        print "Trying to fetch Google Map Maker but failed"
    else:
        html = oa['data']
        p = re.compile('gwm.([0-9]+)')
        m = p.search(html)
        if m:
            gwmNum = m.group(1)
    return gwmNum
