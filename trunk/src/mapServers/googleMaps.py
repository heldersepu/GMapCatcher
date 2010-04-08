## @package src.mapServers.googleMaps
# All the interaction with google.com

import re
import urllib
import src.openanything as openanything
from src.mapConst import MAP_MAX_ZOOM_LEVEL, MAP_MIN_ZOOM_LEVEL, MAP_SERVICES

known_layers = {}

## Returns a template URL for the GoogleMaps
def layer_url_template(layer, language):
    if layer not in known_layers:
        map_server_query = {"gmap":"", "gsat":"h", "gter":"p"}
        layers_name = {"gmap":"m", "gsat":"s", "gter":"t"}

        oa = openanything.fetch(
            'http://maps.google.com/maps?t=' + map_server_query[ MAP_SERVICES[layer]["TextID"]  ])

        if oa['status'] != 200:
            print "Trying to fetch http://maps.google.com/maps but failed"
            return None
        html = oa['data']

        known_layers[layer] = parse_start_page(layers_name[ MAP_SERVICES[layer]["TextID"] ], html, language)
    return known_layers[layer]

## Returns the URL to the GoogleMaps tile
def get_url(counter, coord, layer, language):
    template = layer_url_template(layer, language)
    if template:
        return template % (counter, coord[0], coord[1], 17 - coord[2])


## Parse maps.google.com/maps.
#  google always change this page and map api, we use a specific
#  method to do the parser work.
#  the return value is a url pattern like this:
#  http://mt%d.google.com/vt/lyrs=t@110&hl=en&x=%i&y=%i&z=%i
def parse_start_page(layer, html, language):
    # first, we check the uniform url pattern.
    # after Oct. 10, 2009, google use a uniform url:
    #
    # http://mt%d.google.com/vt/lyrs=??@110&hl=en&x=%i&y=%i&z=%i
    #
    # to fetch map, satellite and terrain tiles, where
    # ?? is 'm' for map, 's' for satellite and 't' for terrain.
    # google also use an 'h' layer for its route and labels.
    #
    # However, google actually uses:
    # http://mt0.google.com/vt/v=w2p.110&hl=en&x=%i&y=%i&z=%i
    # for terrain.
    #  although the uniform URL pattern still works, the result
    # from it is different from google map's web. the later contains
    # more labels and routes. see Issue 94, comment 2
    match_str = '&hl=' + language + '&x=%i&y=%i&z=%i'

    # we first check the existence of the uniform URL pattern,
    # if not, we fall back to the old method.
    if layer != 't':
        upattern = 'http://mt[0-9].google.com/vt/lyrs\\\\x3dm@([0-9]+)'
        p = re.compile(upattern)
        m = p.search(html)

        ## if exist, we use upattern to form the retval
        if m:
            head_str = 'http://mt%d.google.com/vt/lyrs='
            layer_str = layer + '@' + m.group(1)
            return head_str + layer_str + match_str

    # List of patterns add more as needed
    paList = ['http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v=([a-z0-9.]+)&',
              'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]lyrs=([a-z@0-9.]+)&',
              'http://([a-z]{2,3})[0-9].google.com/([a-z]+)[?/]v\\\\x3d([a-z0-9.]+)\\\\x26']
    for srtPattern in paList:
        p = re.compile(srtPattern)
        m = p.search(html)
        if m: break
    if not m:
        print "Cannot parse result"
        return None

    return 'http://%s%%d.google.com/%s/v=%s' % tuple(m.groups()) + match_str


def set_zoom(intZoom):
    if (MAP_MIN_ZOOM_LEVEL <= intZoom <= MAP_MAX_ZOOM_LEVEL):
        return intZoom
    else:
        return 10

## Search a location in Google
def search_location(location):
    print 'downloading the following location:', location
    try:
        oa = openanything.fetch( 'http://maps.google.com/maps?q=' +
            urllib.quote_plus(location) )
    except Exception:
        return 'error=Can not connect to http://maps.google.com', None
    if oa['status']!=200:
        return 'error=Can not connect to http://maps.google.com', None

    m = 0
    html = oa['data']
    if html.find('We could not understand the location') < 0:
        # List of patterns to look for the location name
        paList = ['laddr:"([^"]+)"',
                  'daddr:"([^"]+)"']
        for srtPattern in paList:
            p = re.compile(srtPattern)
            m = p.search(html)
            if m: break

    if m:
        location = m.group(1)
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
        m = p.search(html)
        if m:
		break

    if m:
        zoom = 10
	try:
		zoom = m.group('zoom')
	except IndexError:
		p = re.compile('center:.*zoom:([0-9.-]+).*mapType:')
		m2 = p.search(html)
		if m2:
			zoom = set_zoom(MAP_MAX_ZOOM_LEVEL - int(m2.group(1)))
	location = unicode(location, errors='ignore')
	return location, (float(m.group('lat')), float(m.group('lng')), int(zoom))
    else:
        return 'error=Unable to get latitude and longitude of %s ' % location

