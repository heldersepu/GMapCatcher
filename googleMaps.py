import os, re, openanything, urllib, math, gtk, sys
MAP_MAX_ZOOM_LEVEL = 17
MAP_MIN_ZOOM_LEVEL = -2
TILES_WIDTH = 256
TILES_HEIGHT = 256
NR_MTS = 4


class GoogleMaps:
	locations = {}
	mt_counter = 0
	def get_png_file(self, zl, coord, filename, online):
		if os.path.isfile(filename):
		       return True
		else:
			if not online:
				return False
			href = 'http://mt%i.google.com/mt?n=404&v=w2.69&hl=en&x=%i&y=%i&zoom=%i' % (self.mt_counter,coord[0],
					coord[1], zl)
			self.mt_counter += 1
			self.mt_counter = self.mt_counter % NR_MTS
			try:
				print 'downloading:', href
				oa = openanything.fetch(href)
				if oa['status']==200:
					file = open( filename, 'wb' )
					file.write( oa['data'] )
					file.close()
					return True
			except KeyboardInterrupt:
				raise
			except:
				print '\tdownload failed -', sys.exc_info()[0]
			return False

	def read_locations(self):
		p = re.compile('location="([^"]+)".*lat="([^"]+)".*lng="([^"]+)".*')
		file = open(self.locationpath, "r")
		for line in file:
			m = p.search(line)
			if m:
				self.locations[m.group(1)] = (float(m.group(2)), float(m.group(3)))

		file.close()

	def write_locations(self):
		file = open(self.locationpath, "w")
		for l in self.locations.keys():
			file.write('location="%s"\tlat="%f"\tlng="%f"\n' % (
				l, self.locations[l][0], self.locations[l][1]))
		file.close()

	def __init__(self):
		self.configpath = os.path.expanduser("~/.googlemaps")
		self.locationpath = os.path.join(self.configpath, 'locations')
		self.tilespath = os.path.join(self.configpath, 'tiles')

		if not os.path.isdir(self.configpath):
		    os.mkdir(self.configpath)
		if not os.path.isdir(self.tilespath):
		    os.mkdir(self.tilespath)
		if (os.path.exists(self.locationpath)):
			self.read_locations()
		else:
			self.write_locations()

	def get_locations(self):
		return self.locations

	def search_location(self, location):
		print 'downloading the following location:', location
		oa = openanything.fetch( 'http://maps.google.com/maps?q='+urllib.quote_plus(location) )
		if oa['status']!=200:
			print 'error connecting to http://maps.google.com - aborting'
			return False
		html = oa['data']
		p = re.compile('laddr:"([^"]+)"')
		m = p.search(html)
		if m:
			location = m.group(1)
		else:
			print 'location %s not found' % location
			return False

		p = re.compile('center:{lat:([0-9.-]+),lng:([0-9.-]+)}')
		m = p.search(html)
		lat, lng = float(m.group(1)), float(m.group(2))
		self.locations[location] = (lat, lng)
		self.write_locations()
		return location

	def tile_adjustEx(self, zoom_level, tile, offset):
		world_tiles = int(2 ** (MAP_MAX_ZOOM_LEVEL - zoom_level))
		
		x = int((tile[0] * TILES_WIDTH + offset[0]) % (world_tiles * TILES_WIDTH))
		y = int((tile[1] * TILES_HEIGHT + offset[1]) % (world_tiles * TILES_HEIGHT))
		tile_coord = (x / int(TILES_WIDTH), y / int(TILES_HEIGHT))
		offset_in_tile = (x % int(TILES_WIDTH), y % int(TILES_HEIGHT))

		return tile_coord, offset_in_tile

	def tile_adjust(self, zoom_level, tile):
		world_tiles = int(2 ** (MAP_MAX_ZOOM_LEVEL - zoom_level))
		tile_coord = tile
		tile_coord = (int(tile_coord[0]) % world_tiles, int(tile_coord[1]) % world_tiles)
		return tile_coord

	def coord_to_path(self, zoom_level, coord):
		path = os.path.join(self.tilespath, '%d' % zoom_level)
		if not os.path.isdir(path):
			os.mkdir(path)
		## at most 1024 files in one dir
		## We onle have 2 levels for one axis
		path = os.path.join(path, "%d" % (coord[0] / 1024))
		if not os.path.isdir(path):
			os.mkdir(path)
		
		path = os.path.join(path, "%d" % (coord[0] % 1024))
		if not os.path.isdir(path):
			os.mkdir(path)

		path = os.path.join(path, "%d" % (coord[1] / 1024))
		if not os.path.isdir(path):
			os.mkdir(path)

		path = os.path.join(path, "%d.png" % (coord[1] % 1024))
		return path
	
	def get_file(self, zoom_level, coord, online):
		if (zoom_level > MAP_MAX_ZOOM_LEVEL) or (zoom_level < MAP_MIN_ZOOM_LEVEL):
			return None
		world_tiles = 2 ** (MAP_MAX_ZOOM_LEVEL - zoom_level)
		if (coord[0] > world_tiles):
			return None
		if (coord[1] > world_tiles):
			return None

		## Tiles dir structure
		filename = self.coord_to_path(zoom_level, coord)
#		print "Coord to path: %s" % filename
		if (self.get_png_file(zoom_level, coord, filename, online)):
			return filename
		else:
			return None


	def get_tile_pixbuf(self, zoom_level, coord, online):
		w = gtk.Image()
#		print ("get_tile_pixbuf: zl: %d, coord: %d, %d") % (zoom_level, coord[0], coord[1])
		filename = self.get_file(zoom_level, coord, online)
		if (filename == None):
			w.set_from_file('missing.png')
		else:
			w.set_from_file(filename)
		return w.get_pixbuf()

	def coord_to_tile(self, zl, lat, lng):
		world_tiles = int(2 ** (MAP_MAX_ZOOM_LEVEL - zl))
		lng += 180.0
		x = (world_tiles) / 360.0 * lng
		tiles_pre_radian = world_tiles / (2 * math.pi)
		e = math.sin(lat*(1/180.*math.pi))
		y = int(world_tiles/2 + 0.5*math.log((1+e)/(1-e)) * (-tiles_pre_radian))
		return (int(round(x, 0)) % world_tiles, int(round(y, 0)) % world_tiles)


