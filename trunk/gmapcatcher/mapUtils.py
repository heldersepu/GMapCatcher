# -*- coding: utf-8 -*-
## @package gmapcatcher.mapUtils
# A group of map utilities

import re
import math
from mapConst import *
from widgets.customWidgets import FileChooser, FileSaveChooser
from time import gmtime, strftime
from htmlentitydefs import name2codepoint
from gmapcatcher import gpxpy


def tiles_on_level(zoom_level):
    return 1 << (MAP_MAX_ZOOM_LEVEL - int(zoom_level))


def tile_adjustEx(zoom_level, tile, offset):
    world_tiles = tiles_on_level(zoom_level)

    x = int((tile[0] * TILES_WIDTH + offset[0]) % (world_tiles * TILES_WIDTH))
    y = int((tile[1] * TILES_HEIGHT + offset[1]) % (world_tiles * TILES_HEIGHT))
    tile_coord = (x / int(TILES_WIDTH), y / int(TILES_HEIGHT))
    offset_in_tile = (x % int(TILES_WIDTH), y % int(TILES_HEIGHT))

    return tile_coord, offset_in_tile


def tile_adjust(zoom_level, tile):
    world_tiles = tiles_on_level(zoom_level)
    return (int(tile[0]) % world_tiles, int(tile[1]) % world_tiles)


def mod(x, y):
    r = x % y
    if r < 0:
        r += y
    return r


## Convert from coord(lat, lng, zoom_level) to (tile, offset)
def coord_to_tile(coord):
    world_tiles = tiles_on_level(coord[2])
    x = world_tiles / 360.0 * (coord[1] + 180.0)
    tiles_pre_radian = world_tiles / (2 * math.pi)
    e = math.sin(coord[0] * (1 / 180. * math.pi))
    y = world_tiles / 2 + 0.5 * math.log((1 + e) / (1 - e)) * (-tiles_pre_radian)
    offset = int((x - int(x)) * TILES_WIDTH), \
             int((y - int(y)) * TILES_HEIGHT)
    return (int(x) % world_tiles, int(y) % world_tiles), offset


## Convert from ((tile, offset), zoom_level) to coord(lat, lon, zoom_level)
def tile_to_coord(tile, zoom):
    world_tiles = tiles_on_level(zoom)
    x = (tile[0][0] + 1.0 * tile[1][0] / TILES_WIDTH) / (world_tiles / 2.) - 1  # -1...1
    y = (tile[0][1] + 1.0 * tile[1][1] / TILES_HEIGHT) / (world_tiles / 2.) - 1  # -1...1
    lon = x * 180.0
    y = math.exp(-y * 2 * math.pi)
    e = (y - 1) / (y + 1)
    lat = 180.0 / math.pi * math.asin(e)
    return lat, lon, zoom


## Convert a list (iterable) of coords (lat,lon) into a set of tiles
def coords_to_tilepath(coords, zoom):
    res = set()
    ltile = None
    for lat, lon in coords:
        tile = coord_to_tile((lat, lon, zoom))
        if ltile is None:
            res.add(tile[0])
        elif ltile[0] == tile[0]:
            pass
        else:
            a = ltile[0]
            b = tile[0]
            ### Adds the tile path in between
            if a[0] == b[0]:
                for p in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
                    res.add((a[0], p))
            elif a[1] == b[1]:
                for p in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
                    res.add((p, a[1]))
            else:
                d0 = b[0] - a[0]
                d1 = b[1] - a[1]
                if abs(d0) > abs(d1):  # Horizontal scan
                    for p in range(d0 + 1):
                        res.add((a[0] + p, int(a[1] + float(d1 * p) / float(d0) - 0.5)))
                        res.add((a[0] + p, int(a[1] + float(d1 * p) / float(d0) + 0.5)))
                else:
                    for p in range(d1 + 1):
                        res.add((int(a[0] + float(d0 * p) / float(d1) - 0.5), a[1] + p))
                        res.add((int(a[0] + float(d0 * p) / float(d1) + 0.5), a[1] + p))
            res.add(tile[0])
            #print tile
        ltile = tile
    return res


def tilepath_bulk(tiles, size):
    res = set()
    for x, y in tiles:
        for dx in range(-size, size + 1):
            for dy in range(-size, size + 1):
                res.add((x + dx, y + dy))
    return res


## Find scale of the picture in km per pixel
def km_per_pixel(coord):
    world_tiles = tiles_on_level(coord[2])
    return 2 * math.pi * R_EARTH / world_tiles / TILES_WIDTH * math.cos(coord[0] * math.pi / 180.0)


## should return a tuple of (60 <= pixels <= 125, nice round number of m
#                            [% 1000 = 0 when nice round number of km])
def friendly_scale(zoomlevel):
    km = sig_figs(km_per_pixel((0, 0, zoomlevel)), 4)
    for i in range(0, 65):
        if (abs(km * (125 - i)) <= 0.025):
            return (i, int(km * i * 1000))
    return (100, int(100000 * nice_round(km)))  # currently simplified


## Convert tuple-like string to real tuples
# eg: '((1, 2), (2, 3))' -> ((1, 2), (2, 3))
def str_to_tuple(strCenter):
    strCenter = strCenter.strip()
    strCenter = strCenter.replace('(', '')
    strCenter = strCenter.replace(')', '')
    center = map(int, strCenter.split(','))
    return ((center[0], center[1]),
            (center[2], center[3]))


def nice_round(f):
    return sig_figs(f, 2)


def sig_figs(f, sf):
    n = int(math.log(f, 10))
    return round(f, sf - n)


##  Convert from ((tile, zoom), rect, center) to screen coordinates
def tile_coord_to_screen(tile_coord, rect, center, getGlobal=False):
    dx = rect.width // 2 - center[1][0] + (tile_coord[0] - center[0][0]) * TILES_WIDTH
    dy = rect.height // 2 - center[1][1] + (tile_coord[1] - center[0][1]) * TILES_HEIGHT

    if getGlobal or (-TILES_WIDTH <= dx <= rect.width and -TILES_HEIGHT <= dy <= rect.height):
        return [(int(dx), int(dy))]
    else:
        return None


## Convert from screen pointer to tile
def pointer_to_tile(rect, pointer, center, zl):
    da_center = (rect.width // 2, rect.height // 2)

    fix_tile = center[0]
    fix_offset = center[1][0] + (pointer[0] - da_center[0]), \
                 center[1][1] + (pointer[1] - da_center[1])

    return tile_adjustEx(zl, fix_tile, fix_offset)


def pointer_to_coord(rect, pointer, center, zl):
    tile = pointer_to_tile(rect, pointer, center, zl)
    return tile_to_coord(tile, zl)


## Convert km to latitude
def km_to_lat(height):
    return height * 180 / math.pi / R_EARTH


## Convert km to longitude
def km_to_lon(width, lat):
    return width * 180 / math.pi / (R_EARTH * math.cos(lat * math.pi / 180))


## Return Date & Time
def timeStamp():
    return strftime(" %d_%b_%Y %H.%M.%S", gmtime())


## Convert altitude (meters) to zoom
def altitude_to_zoom(altitude):
    if int(altitude) <= 0:
        zoom = MAP_MIN_ZOOM_LEVEL + 2
    else:
        zoom = int(math.log(int(altitude)) / math.log(2))
    return min(max(zoom, MAP_MIN_ZOOM_LEVEL + 2), MAP_MAX_ZOOM_LEVEL)


def subs_entity(match):
    entity = match.group(3)
    if match.group(1) == "#":
        if match.group(2) == '':
            return unichr(int(entity))
        elif match.group(2) == 'x':
            return unichr(int('0x' + entity, 16))
    else:
        codepoint = name2codepoint.get(entity, "")
        if codepoint != "":
            return unichr(codepoint)
    return match.group()


def html_decode(string):
    entity_re = re.compile("&(#?)(x?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(subs_entity, string)[0]


def countDistanceFromLatLon(a, b):
    R = 6371  # Mean radius of Earth in km
    dLat = math.radians(a[0] - b[0])
    dLon = math.radians(a[1] - b[1])
    lat1 = math.radians(a[0])
    lat2 = math.radians(b[0])
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.sin(dLon / 2) * math.sin(dLon / 2) * math.cos(lat1) * math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = float(R * c)
    return d


def countBearingFromLatLon(a, b):
    y = math.sin(a[1] - b[1]) * math.cos(b[0])
    x = math.cos(a[0]) * math.sin(b[0]) - \
            math.sin(a[0]) * math.cos(b[0]) * math.cos(a[1] - b[1])
    bearing = (((math.degrees(math.atan2(y, x)) + 360) % 360) + 180) % 360
    return bearing


def saveGPX(trackSegments):
    f_name = FileSaveChooser(getHome(), strTitle="Select File")
    if f_name:
        gpx = gpxpy.gpx.GPX()
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx_track.name = NAME + ' Tracks'
        gpx.tracks.append(gpx_track)
        for trackSegment in trackSegments:
            gpx_segment = gpxpy.gpx.GPXTrackSegment()
            gpx_track.segments.append(gpx_segment)
            for p in trackSegment['coords']:
                gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(p[0], p[1]))
        f = open(f_name, 'w')
        f.write(gpx.to_xml())
        f.close()


def openGPX():
    tracks = None
    f_name = FileChooser(getHome(), strTitle="Select File")
    if f_name:
        f = open(f_name, 'r')
        tracks = list()
        gpx = gpxpy.parse(f)
        i = 1
        for track in gpx.tracks:
            for segment in track.segments:
                track_points = list()
                for point in segment.points:
                    track_points.append((point.latitude, point.longitude))
                if len(track.segments) > 1 or len(gpx.tracks) > 1:
                    tracks.append({'name': '%s - track %i' % (f_name, i), 'coords': track_points})
                    if len(track.segments) > 1:
                        i += 1
                else:
                    tracks.append({'name': '%s - track' % f_name, 'coords': track_points})
            i += 1
        for route in gpx.routes:
            track_points = list()
            for point in route.points:
                track_points.append((point.latitude, point.longitude))
            if len(gpx.routes) > 1:
                tracks.append({'name': '%s - route %i' % (f_name, i), 'coords': track_points})
            else:
                tracks.append({'name': '%s - route' % f_name, 'coords': track_points})
            i += 1
    return tracks


def getHome():
    return os.getenv('USERPROFILE') or os.getenv('HOME')


def convertUnits(unit_from, unit_to, value):
    if unit_from == UNIT_TYPE_KM:
        if unit_to == UNIT_TYPE_MILE:
            return float(value) / 1.609344
        elif unit_to == UNIT_TYPE_NM:
            return float(value) / 1.852
    elif unit_from == UNIT_TYPE_MILE:
        if unit_to == UNIT_TYPE_KM:
            return float(value) * 1.609344
        elif unit_to == UNIT_TYPE_NM:
            return float(value) * 0.868976242
    elif unit_from == UNIT_TYPE_NM:
        if unit_to == UNIT_TYPE_KM:
            return float(value) * 1.852
        elif unit_to == UNIT_TYPE_MILE:
            return float(value) * 1.15077945
    return value
