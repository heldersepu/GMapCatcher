import gtk
import math
import mapMark
from mapConst import *
from threading import Thread

marker = mapMark.MyMarkers()

def do_draw_pix(myTuple):
    da = myTuple[12].drawing_area.window
    pixbuf = myTuple[12].ctx_map.get_tile_pixbuf(
            (myTuple[1], myTuple[2], myTuple[0]), myTuple[9], myTuple[10])

    da.draw_pixbuf(myTuple[11], pixbuf,
                    myTuple[3], myTuple[4], myTuple[5],
                    myTuple[6], myTuple[7], myTuple[8])

    if (myTuple[0] < MAP_MAX_ZOOM_LEVEL - 2):
        for str in marker.positions.keys():
            coord = marker.positions[str]
            myCenter = coord_to_tile(coord)
            if (myTuple[1] == myCenter[0][0] and myTuple[2] == myCenter[0][1]):
                da.draw_pixbuf(myTuple[11], marker.pixbuf,
                        myTuple[3], myTuple[4], myTuple[5],
                        myTuple[6], myTuple[7], myTuple[8])

class GetTileThread(Thread):
    def __init__(self, myTuple):
        Thread.__init__(self)
        self.myTuple = myTuple

    def run(self):
        do_draw_pix(self.myTuple)
        return

def do_expose_cb(self, zl, center, rect, online,
                 force_update, style_black_gc, area):

    tl_point = (center[1][0] - rect.width / 2,
                center[1][1] - rect.height / 2)

    tl_tile, tl_offset = tile_adjustEx(zl, center[0], tl_point)

    y_pos = 0
    tile_y_pos = tl_tile[1]
    tile_y_pos_inner = tl_offset[1]
    draw_height = TILES_HEIGHT - tl_offset[1]
    threads = []
    while (y_pos < rect.height):
        tile_x_pos = tl_tile[0]
        tile_x_pos_inner = tl_offset[0]
        draw_width = TILES_WIDTH - tl_offset[0]
        x_pos = 0
        while (x_pos < rect.width):
        #############################################
            real_tile_x, real_tile_y = tile_adjust(zl, (tile_x_pos, tile_y_pos))

            if not (((area.x + area.width < x_pos) or \
                     (x_pos + draw_width < area.x)) or \
                    ((area.y + area.height < y_pos) or
                     (y_pos + draw_height < area.y))):
                myTuple = (zl, real_tile_x, real_tile_y,
                        tile_x_pos_inner, tile_y_pos_inner, x_pos, y_pos,
                        draw_width, draw_height, online,
                        force_update, style_black_gc, self)
                if online:
                    th = GetTileThread(myTuple)
                    threads.append(th)
                    th.start()
                else:
                    do_draw_pix(myTuple)

            x_pos += draw_width
            tile_x_pos += 1
            tile_x_pos_inner = 0
            draw_width = TILES_WIDTH
            if (x_pos + draw_width > rect.width):
                draw_width = rect.width - x_pos

        y_pos += draw_height
        tile_y_pos += 1
        tile_y_pos_inner = 0
        draw_height = TILES_HEIGHT
        if (y_pos + draw_height > rect.height):
            draw_height = rect.height - y_pos
    if online:
        for th in threads:
            th.join()

def tile_adjustEx(zoom_level, tile, offset):
    world_tiles = int(2 ** (MAP_MAX_ZOOM_LEVEL - zoom_level))

    x = int((tile[0] * TILES_WIDTH + offset[0]) % (world_tiles * TILES_WIDTH))
    y = int((tile[1] * TILES_HEIGHT + offset[1]) % (world_tiles * TILES_HEIGHT))
    tile_coord = (x / int(TILES_WIDTH), y / int(TILES_HEIGHT))
    offset_in_tile = (x % int(TILES_WIDTH), y % int(TILES_HEIGHT))

    return tile_coord, offset_in_tile

def tile_adjust(zoom_level, tile):
    world_tiles = int(2 ** (MAP_MAX_ZOOM_LEVEL - zoom_level))
    return (int(tile[0]) % world_tiles, int(tile[1]) % world_tiles)

# convert from coord(lat, lng, zoom_level) to (tiles, offset)
def coord_to_tile(coord):
    world_tiles = int(2 ** (MAP_MAX_ZOOM_LEVEL - coord[2]))
    x = world_tiles / 360.0 * (coord[1] + 180.0)
    tiles_pre_radian = world_tiles / (2 * math.pi)
    e = math.sin(coord[0] * (1/180.*math.pi))
    y = world_tiles/2 + 0.5*math.log((1+e)/(1-e)) * (-tiles_pre_radian)
    offset = int((x - int(x)) * TILES_WIDTH), \
             int((y - int(y)) * TILES_HEIGHT)
    return (int(x) % world_tiles, int(y) % world_tiles), offset
    
def force_repaint():
    while gtk.events_pending():
        gtk.main_iteration_do(False) 
