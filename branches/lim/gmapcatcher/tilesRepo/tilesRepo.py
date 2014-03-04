## This modul provides filebased tile repository functions
#
# Usage:
#
# base class for tile repository
#
# - constructor requires MapServ instance, because method
#  'get_tile_from_coord' is provided in the MapServ
#
# - this module is not used directly. It is used via MapServ() methods:
#     - get_file()
#     - load_pixbuf()
# - module is finalized from MapServ.finish() method


class NotImplementedException(Exception):
    pass


class TilesRepository:

    def __init__(self, MapServ_inst, conf):
        self.finished = False
        self.configpath = conf.init_path

    def finish(self):
        self.finished = True

    def is_finished(self):
        return self.finished

    def load_pixbuf(self, coord, layer, force_update):
        raise NotImplementedException()

    def get_plain_tile(self, coord, layer):
        raise NotImplementedException()

    def store_plain_tile(self, coord, layer, tiledata):
        raise NotImplementedException()

    #def get_tile(self, tcoord, layer, online, force_update, conf):
    #    raise NotImplementedException()

    def do_export(self, tcoord, layer, online, mapServ, styleID, size):
        raise NotImplementedException()

    def remove_old_tile(self, coord, layer, filename=None, interval=86400):
        raise NotImplementedException()

    # coord is (tile_x, tile_y, zoom)
    def is_tile_in_local_repos(self, coord, layer):
        raise NotImplementedException()

    def set_repository_path(self, conf):
        raise NotImplementedException()
