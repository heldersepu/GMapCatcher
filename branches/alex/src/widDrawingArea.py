## @package src.widDrawingArea
# DrawingArea widget used to display the map

import gtk
from src.mapConst import *
from mapUtils import tile_adjustEx, pointer_to_tile

## This widget is where the map is drawn
class DrawingArea(gtk.DrawingArea):
    center = ((0,0),(128,128))
    draging_start = (0, 0)

    def __init__(self, scale):
        self.scale = scale
        super(DrawingArea, self).__init__()

        self.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.connect('button-press-event', self.da_button_press)

        self.add_events(gtk.gdk.BUTTON_RELEASE_MASK)
        self.connect('button-release-event', self.da_button_release)

    ## Change the mouse cursor over the drawing_area
    def da_set_cursor(self, dCursor = gtk.gdk.HAND1):
        cursor = gtk.gdk.Cursor(dCursor)
        self.window.set_cursor(cursor)

    ## Handles left (press click) event in the drawing_area
    def da_button_press(self, w, event):
        if (event.button == 1):
            self.draging_start = (event.x, event.y)
            self.da_set_cursor(gtk.gdk.FLEUR)

    ## Handles left (release click) event in the drawing_area
    def da_button_release(self, w, event):
        if (event.button == 1):
            self.da_set_cursor()

    ## Jumps in the drawing_area
    def da_jump(self, intDirection, zoom, doBigJump=False):
        # Left  = 1  Up   = 2
        # Right = 3  Down = 4
        intJump = 10
        if doBigJump:
            intJump = intJump * 10

        self.draging_start = (intJump * (intDirection == 3),
                              intJump * (intDirection == 4))
        self.da_move(intJump * (intDirection == 1),
                     intJump * (intDirection == 2), zoom)

    ## Move the drawing_area
    def da_move(self, x, y, zoom):
        rect = self.get_allocation()
        if (0 <= x <= rect.width) and (0 <= y <= rect.height):
            center_offset = (self.center[1][0] + (self.draging_start[0] - x),
                             self.center[1][1] + (self.draging_start[1] - y))
            self.center = tile_adjustEx(zoom, self.center[0], center_offset)
            self.draging_start = (x, y)
            self.repaint()

    def do_scale(self, zoom, current_zoom_level, doForce, dPointer):
        if (zoom == current_zoom_level) and not doForce:
            return

        rect = self.get_allocation()
        da_center = (rect.width // 2, rect.height // 2)
        if dPointer:
            fix_tile, fix_offset = pointer_to_tile(
                rect, dPointer, self.center, current_zoom_level
            )        
        else:
            fix_tile, fix_offset = self.center
            

        scala = 2 ** (current_zoom_level - zoom)
        x = int((fix_tile[0] * TILES_WIDTH  + fix_offset[0]) * scala)
        y = int((fix_tile[1] * TILES_HEIGHT + fix_offset[1]) * scala)
        if dPointer and not doForce:
            x = x - (dPointer[0] - da_center[0])
            y = y - (dPointer[1] - da_center[1])

        self.center = (x / TILES_WIDTH, y / TILES_HEIGHT), \
                      (x % TILES_WIDTH, y % TILES_HEIGHT)
        self.repaint()

    def repaint(self):
        self.queue_draw()
