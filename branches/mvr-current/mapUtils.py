import math
import mapMark
from mapConst import *

marker = mapMark.MyMarkers()

def tiles_on_level(zoom_level):
    return 1<<(MAP_MAX_ZOOM_LEVEL-int(zoom_level))

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

def mod(x,y):
    r=x%y
    if r<0: r+=y
    return r

# convert from coord(lat, lng, zoom_level) to (tile, offset)
def coord_to_tile(coord):
    world_tiles = tiles_on_level(coord[2])
    x = world_tiles / 360.0 * (coord[1] + 180.0)
    tiles_pre_radian = world_tiles / (2 * math.pi)
    e = math.sin(coord[0] * (1/180.*math.pi))
    y = world_tiles/2 + 0.5*math.log((1+e)/(1-e)) * (-tiles_pre_radian)
    offset = int((x - int(x)) * TILES_WIDTH), \
             int((y - int(y)) * TILES_HEIGHT)
    return (int(x) % world_tiles, int(y) % world_tiles), offset

# convert ((tile, offset), zoom_level) to (lat, lon, zoom_level)
def tile_to_coord(tile, zoom):
    world_tiles = tiles_on_level(zoom)
    x = ( tile[0][0] + 1.0*tile[1][0]/TILES_WIDTH ) / (world_tiles/2.) - 1 # -1...1
    y = ( tile[0][1] + 1.0*tile[1][1]/TILES_HEIGHT) / (world_tiles/2.) - 1 # -1...1
    lon = x * 180.0
    y = math.exp(-y*2*math.pi)
    e = (y-1)/(y+1)
    lat = 180.0/math.pi * math.asin(e)
    return lat, lon, zoom

# Find scale of the picture in km per pixel
def km_per_pixel(coord):
    world_tiles = tiles_on_level(coord[2])
    return 2*math.pi*R_EARTH/world_tiles/TILES_WIDTH * math.cos(coord[0]*math.pi/180.0)
