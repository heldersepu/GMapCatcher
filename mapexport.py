#!/usr/bin/python
# coding: utf-8

import sys
import re, os, sqlite3, math

import gmapcatcher.mapConf as mapConf

from gmapcatcher.mapUtils import *
from gmapcatcher.mapArgs import MapArgs
from gmapcatcher.mapServices import MapServ
from gmapcatcher.mapDownloader import MapDownloader

mConf = mapConf.MapConf()
ctx_map = MapServ(mConf.init_path, mConf.repository_type)


from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

# Constants
TILE=256

### Tile convertion ###

def deg2pix(lat_deg, lon_deg, zoom):
    coord, offset = coord_to_tile((lat_deg, lon_deg, 17-zoom))
    return (coord[0] * TILES_WIDTH + offset[0], coord[1] * TILES_HEIGHT + offset[1])

def coord2pixels(coords, zoom):
    a = deg2pix(coords[0][0], coords[0][1], zoom)
    b = deg2pix(coords[1][0], coords[1][1], zoom)
    st = min(a[0],b[0]), min(a[1],b[1])
    ed = max(a[0],b[0]), max(a[1],b[1])
    pixels = (st,ed)
    pixels_sz = (ed[0]-st[0], ed[1]-st[1])
    return pixels, pixels_sz


### Page size in inches
#PAGESIZE = 8.27, 11.69
#PAGESIZE = 11.69, 8.27
PAGESIZE = tuple(x/72.0 for x in pagesizes.landscape(pagesizes.A4))
MARGIN = 0.22, 0.27
SOLAPE = 0.25, 0.25


"""
    Parameters
    pixels = ((px_x,px_y),(px_x,px_y))
    pixel_center = (px_x, px_y)
    pixel_range = (delta_x, delta_y)
    coords = ((lat,lon), (lat,lon))
    coord_center = (lat,lon)
    coord_range = (delta_lat,delta_lon)
    zoom
    dpi
    pages
"""
def mapPDF(pdffile, zoom, layer=2, coords=None, coord_center=None, coord_range=None, pixels=None, pixel_center=None, pixel_range=None, pages=(1,1), dpi=None, title=None):
    # Check de parámetros
    pgsz = (PAGESIZE[0] - 2*MARGIN[0] - SOLAPE[0], PAGESIZE[1] - 2*MARGIN[1] - SOLAPE[1])
    pixels_sz = None
    
    if isinstance(pages, int):
        pages = (pages, pages)
    
    if zoom != None and pixel_center == None and coord_range != None:
        pixel_center = deg2pix(coord_center[0], coord_center[1], zoom)
    
    if dpi != None and pages != None and pixel_range == None:
        pixel_range = (int(pgsz[0] * dpi * pages[0] /2), int(pgsz[1] * dpi * pages[1] /2))
    
    if zoom != None:
        if coords != None:
            # Pixels en función de las coordenadas y el zoom
            pixels, pixels_sz = coord2pixels(coords, zoom)
        elif coord_center != None:
            # Pixels en función del centro y algún rango
            if coord_range != None:
                coords = ( (coord_center[0]-coord_range[0], coord_center[1]-coord_range[1]), \
                    (coord_center[0]+coord_range[0], coord_center[1]+coord_range[1]))
                pixels, pixels_sz = coord2pixels(coords, zoom)
            elif pixel_range != None:
                a = deg2pix(coord_center[0], coord_center[1], zoom)
                pixels = ((a[0]-pixel_range[0], a[1]-pixel_range[1]), (a[0]+pixel_range[0], a[1]+pixel_range[1]))
                pixels_sz = (2*pixel_range[0], 2*pixel_range[1])
    
    if pixels == None or pixels_sz == None:
        print "You must provide more information to define the map, comeon!"
        d = locals()
        for x in d:
            print '%15s = %r' % (x, d[x])
        return False

    # Computes the dpi
    if dpi == None:
        dpix = float(pixels_sz[0]) / pages[0] / pgsz[0]
        dpiy = float(pixels_sz[1]) / pages[1] / pgsz[1]
        dpi = max(dpix, dpiy)

    pages = ( \
        int(math.ceil(float(pixels_sz[0]) / dpi / pgsz[0] - 0.1)), \
        int(math.ceil(float(pixels_sz[1]) / dpi / pgsz[1] - 0.1)))

    sz = ( \
        int(float(pages[0]) * dpi * pgsz[0]),
        int(float(pages[1]) * dpi * pgsz[1]) )

    dbzoom = 17 - zoom
    st,ed = pixels

    # Generate the PDF
    pdf = canvas.Canvas(pdffile, pagesize=pagesizes.landscape(pagesizes.A4))
    pgw,pgh = int(round(dpi*(pgsz[0]+SOLAPE[0]))), int(round(dpi*(pgsz[1]+SOLAPE[1])))
    if title == None:
        title = pdffile
    pdf.setTitle('%s - zoom %d' % (title, zoom))
    #pdf.setFontSize(size=5)
    pdf.setStrokeColorRGB(0.2,0.5,0.3)
    
    print 'Generating pages, dpi=%.2f, pages=%dx%d, pagesize=%dx%d' % (dpi, pages[0], pages[1], pgw, pgh)
    
    flist = []
    for px in range(pages[0]):
        for py in range(pages[1]):
            ### Print some information over the map ###
            info = "dpi=%d zoom=%d page=%d,%d" % (int(dpi), zoom, px+1, py+1)
            imfn = '%s_%d_%d_%d.png' % (pdffile, zoom, px,py)
            flist.append(imfn)

            crx, cry = st[0]+int(round(px * dpi * pgsz[0])), st[1]+int(round(py * dpi*pgsz[1]))
            ctx_map.do_combine_subtile(dbzoom, layer, True, mConf, imfn, (0,0), crop_start=(crx,cry), crop_size=(pgw,pgh))

            pdf.drawImage(imfn, MARGIN[0]*inch, MARGIN[1]*inch, width=(pgsz[0]+SOLAPE[0])*72.0, height=(pgsz[1]+SOLAPE[1])*72.0, )
            pdf.setFont("Helvetica", 7)
            pdf.drawString((PAGESIZE[0] - MARGIN[0] - 1.5)*inch, (MARGIN[1]-0.08)*inch, info)
            pdf.drawString(MARGIN[0]*inch, (MARGIN[1]-0.08)*inch, '%s - page %d,%d' % (title, px+1, py+1))
            pdf.showPage()
            print crx,cry
    pdf.save()
    del pdf
    for f in flist: os.unlink(f)
    print pages

def main(layer):
    ### Examples

    # Export Paris in 160dpi, zoom=15 and in 2x3 landscape A4 pages. The width and height of the map is computed to fit this requirement.
    dpi = 160
    mapPDF('paris_%d.pdf'%dpi, title="Paris, France", zoom=15, pages=(2, 3), coord_center=(48.856245, 2.347898), dpi=dpi, layer=layer)

    # Export a given region of Paris with the given zoom=14, in 2x2 landscape A4 pages, adjusting the dpi to the needed value.
    zoom = 14
    mapPDF('paris_z%d.pdf'%zoom, title='Paris, France', zoom=zoom, pages=2, coord_center=(48.856245, 2.347898), coord_range=(0.028623, 0.084114), layer=layer)



if __name__ == '__main__':
    try:
        main(layer=2)

    finally:
        # Sory for this rude thing, but the program doesn't stop by itself
        import signal ; os.kill(os.getpid(), signal.SIGTERM)

