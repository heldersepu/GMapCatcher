## @package gmapcatcher.mapServers.googleMapMaker
# All the interaction with Google Map Maker

import re
import gmapcatcher.openanything as openanything

known_layers = {}


## Returns a template URL for the Google Map Maker
def layer_url_template(layer):
    if layer not in known_layers:
        known_layers[layer] = 'http://gt%d.google.com/mt/n=404&v=gwm.' + \
                                parse_page() + '&x=%i&y=%i&zoom=%i'
    return known_layers[layer]


## Returns the URL to the Google Map Maker tile
def get_url(counter, coord):
    return layer_url_template('gwm') % \
        (counter, coord[0], coord[1], coord[2] + 1)


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
