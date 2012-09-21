# -*- coding: utf-8 -*-
## @package gmapcatcher.mapServers.seznam
# All the interaction with mapy.cz (mapy.seznam.cz)

from gmapcatcher.mapConst import MAP_MAX_ZOOM_LEVEL
"""
A bit of theory:
Mapy.cz is a web service which provides very detailed coverage of Czech republic
and an average coverage of Europe. It is provided by company seznam.cz and
is available on address mapy.cz or mapy.seznam.cz
('mapy' means maps, so I will use plural when talking about mapy.cz)
---------------------------------------------------------------------------------
Map tiles:
The tiles' URL has a form
http://<server>.mapserver.mapy.cz/<layer name>/<zoom>_<x coord>_<y coord>
where:
    server is one of m1, m2, m3, m4
    layer names are: base-n, ophoto,  turist, ophoto0203, army2, hybrid, relief-l, ttur, tcyklo
        meanings are given below
    zoom is a number from 3 to 16; in case of some very detailed ortophotomaps, it is up to 18 (e.g ortophoto map of Prague). Zoom 1 to 2 are not supported by mapy.cz
        The higher number, the more detiled map (in contary to GMapCatcher app).
    x_coord and y_coord are internal coordinates of the bottom left corner of the tile -
        - 7 digit hexadecimal numbers, they will be discussed below

Examples:
http://m1.mapserver.mapy.cz/base-n/3_8000000_8000000
(This tile contains piece of Czech republic, Poland, Ukraine, Belarus, Lithuania, Latvia, Estonia,
Russia and Sweden). The zeros at the end of the numbers are important, something like
http://m1.mapserver.mapy.cz/base-n/3_8000000_800000 or
http://m1.mapserver.mapy.cz/base-n/3_800000_8000000
won't work.
On the other hand prepending the coordinates with zeros works (at least for now), e.g.:
http://m1.mapserver.mapy.cz/base-n/0003_00008000000_0x00008000000


---------------------------------------------------------------------------------
Layers:
Mapy.cz have 5 base layers and 4 additional semitransparent layers which can be combined with the base layers.
It is possible to use more semitransparent layer at once. Not all layers are available for all zooms.
The base layers are as follows:
Layer name  |  Meaning
base-n         normal map
turist         hiking map (but without hiking routes)
ophoto         satellite map, in higher zoom ortophotomap is used
ophoto0203     older ophoto map (from 2002/2003)
army2          old historic map from 1836-52

The semitransparent additional layers are as follows
Layer name  |  Meaning
relief-l       shading, or if you want, terrain, relief
ttur           hiking routes
tcyklo         cyclo routes
hybrid         labels and main routes for ophoto

In the web gui, the base layers can be combined with more semitransparent layers
Base layer  |  applicable semitransparent layers (you can apply more than one)
base-n         relief-l,
turist         relief-l, ttur, tcyklo
ophoto         relief-l, ttur, tcyklo, hybrid
ophoto0203     relief-l, ttur, tcyklo, hybrid
army2          relief-l, hybrid

---------------------------------------------------------------------------------

Coordinates:
Mapy.cz use its own internal coordinates to address the map tiles.
The internal coordinates are integers and can be quite easily transformed from/to
UTM coordinates. Mapy.cz use the following formula to recompute the coordinates:
Consider that UTM and Internal are Python objects with attributes x and y,
Internal.x and Internal.y are integers
UTM.x = Internal.x / 32 - 3700000
UTM.y = Internal.y / 32 + 1300000
In the opposite direction
Internal.x = ( int(round(UTM.x)) + 3700000) * 32
Internal.y = ( int(round(UTM.y)) - 1300000) * 32

The ratio 32 is probably used to allow for fine resolution of the internal (integer)
coordinates (1/32 meter).
The origin of the offsets is not known to me. I guess that it is connected with fact
that the internal coordinates are always 7 digit hexadecimal number (and not less).

The zone in UTM coordinates is hardwired to 33 (where Czech republic lies), it is not
very clear to me, how the recomputations work for points which are in a different UTM zone.

The source code of the transformation can be found in http://api.mapy.cz/js/api_3.utf-8.js?59,
look for ppToUTM, utmToPP, the internal coordinates are refered as pp
(the file is a bit obfuscated, use some tool to tidy it up)

The direction of the y axis is "up" (Google uses down)
It seems that the tiles cannot be aligned with Google maps, the position of tiles and zoom don't match.

The values of both x or y internal coordinates are roughly between 2000000 and e000000 (both in hex)

The admissible values for the coordinates differ according to the actual zoom.
The following rules are valid both for x and y
In zoom 3, the corrdinates are even number (2,…, 8, a, c) followed by 6 zeros (in binary the number ends with  25 zeros)
In zoom 4, the corrdinates end with 6 zeros (in binary 24 zeros)
etc.
In zoom 16, the corrdinates end with 3 zeros (in binary 12 zeros)
Theoretically in zoom 27 the number ends with one zero in binary, in zoom 28 the value is not limited to particular pattern and zoom 29 has no sense. The number 28 occurs in the source code below - the coordinate is a multiple of 2^(28-zoom)
 """


def layer_url_template(layername):
    #~ layer names are:
    #~ base layers:  base-n, ophoto,  turist, ophoto0203, army2
    #~ semitransparent:  hybrid, relief-l, ttur, tcyklo,
    return 'http://m%i.mapserver.mapy.cz/' + layername + '/%i_%x_%x'


def get_url(counter, coord, layer, conf):
    layer_names = ["base-n", "ophoto", "relief-l", "hybrid"]
    return get_url_internal(counter, coord, layer_names[layer])


def get_url_internal(counter, coord, layername):
#The recomputation of the coordinates gives bad results, but at least the whole
#range of maps from mapy.cz can be displayed and thus the tiles can be downloaded.
#Hope somebody can fix it properly
#I tried to position the map such that the geographical center of Czech Republic (Číhošť)
#is displayed on the same tile as in Google maps. Because the scale of tiles is different
#in mapy.cz and google maps (cca by ratio of 1.5 ), the rest of the map is displayed badly.

#I found out on which tiles is displayed the geographical center of Czech republic in mapy.cz
#and google maps and computed the offsets below. Remember that they are pure experimental.
#if you select another point as "the centre of universe" you get different offsets.
    offsets_x = [0, 0, 0, 4, 9, 18, 37, 74, 149, 298, 596, 1191, 2383, 4765, 9530, 19059, 38117, 76235, 152470]
    offsets_y = [0, 0, 0, 6, 13, 26, 52, 104, 209, 419, 838, 1675, 3349, 6698, 13395, 26791, 53582, 107165, 214331]

    zoom = MAP_MAX_ZOOM_LEVEL - coord[2] - 1  # the highest zoom is 18
    y_max = 1 << (zoom + 1)  # maximum value which should occur in this zoom level
    #~ x_max = 1 << (zoom  + 1)  # maximum value which should occur in this zoom level
    x = int((coord[0] - offsets_x[zoom]) << (28 - zoom))
    #in computation of y, there is additional term -1, which helps to keep the center
    #in the center when zooming. It is connected with fact that e.g. Google coordinate refers to the
    #upper left corner of the tile, while in mapy.cz is lower left corner
    y = int((y_max - coord[1] - offsets_y[zoom] - 1) << (28 - zoom))
    return layer_url_template(layername) % (counter + 1, zoom, x, y)
