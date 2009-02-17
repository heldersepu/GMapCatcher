from threading import Thread

class GetTileThread(Thread):
        def __init__(self,  zl,
                        real_tile_x, real_tile_y,
                        tile_x_pos_inner, tile_y_pos_inner,
                        x_pos, y_pos,
                        draw_width, draw_height,
                        online, force_update, gc, window):
                Thread.__init__(self)
                self.zl = zl
                self.x = real_tile_x
                self.y = real_tile_y
                self.xp = x_pos
                self.yp = y_pos
                self.draw_width = draw_width
                self.draw_height = draw_height
                self.online = online
                self.force_update = force_update
                self.gc = gc
                self.window = window
                self.xi = tile_x_pos_inner
                self.yi = tile_y_pos_inner

        def run(self):
                pixbuf = self.window.ctx_map.get_tile_pixbuf((self.x, self.y, self.zl), self.online, self.force_update)
                gc = self.gc
                self.window.drawing_area.window.draw_pixbuf(gc, pixbuf,
                                                        int(self.xi), int(self.yi),
                                                        int(self.xp), int(self.yp),
                                                        int(self.draw_width), int(self.draw_height))
                return

def do_expose_cb(self, zl, center, rect, online, force_update, style_black_gc, area, tiles_height, tiles_width):

        tl_point = (center[1][0] - rect.width / 2,
                    center[1][1] - rect.height / 2)
        
        tl_tile, tl_offset = self.ctx_map.tile_adjustEx(zl, center[0], tl_point)

        y_pos = 0
        tile_y_pos = tl_tile[1]
        tile_y_pos_inner = tl_offset[1]
        draw_height = tiles_height - tl_offset[1]
        threads = []
        while (y_pos < rect.height):
                tile_x_pos = tl_tile[0]
                tile_x_pos_inner = tl_offset[0]
                draw_width = tiles_width - tl_offset[0]
                x_pos = 0
                while (x_pos < rect.width):
                #############################################
                        real_tile_x, real_tile_y = self.ctx_map.tile_adjust(zl, (tile_x_pos, tile_y_pos))

                        if not (((area.x + area.width < x_pos) or (x_pos + draw_width < area.x)) or \
                                        ((area.y + area.height < y_pos) or (y_pos + draw_height < area.y))):
                                th = GetTileThread(zl, real_tile_x, real_tile_y, tile_x_pos_inner,
                                        tile_y_pos_inner, x_pos, y_pos, draw_width, draw_height, online,
                                        force_update, style_black_gc, self)
                                threads.append(th)
                                th.start()

                        x_pos += draw_width
                        tile_x_pos += 1
                        tile_x_pos_inner = 0
                        draw_width = tiles_width
                        if (x_pos + draw_width > rect.width):
                                draw_width = rect.width - x_pos

                y_pos += draw_height
                tile_y_pos += 1
                tile_y_pos_inner = 0
                draw_height = tiles_height
                if (y_pos + draw_height > rect.height):
                        draw_height = rect.height - y_pos
        for th in threads:
                th.join()
