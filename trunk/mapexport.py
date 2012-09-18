#!/usr/bin/python
# coding: utf-8

import os
import math

import gmapcatcher.mapConf as mapConf

from gmapcatcher.mapUtils import *
from gmapcatcher.mapServices import MapServ
from gmapcatcher.xmlUtils import load_gpx_coords

mConf = mapConf.MapConf()
ctx_map = MapServ(mConf.init_path, mConf.repository_type)


from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab.lib.units import inch

# Constants
TILE = 256


### Tile convertion ###

def deg2pix(lat_deg, lon_deg, zoom):
    coord, offset = coord_to_tile((lat_deg, lon_deg, 17 - zoom))
    return (coord[0] * TILES_WIDTH + offset[0], coord[1] * TILES_HEIGHT + offset[1])


def coord2pixels(coords, zoom):
    a = deg2pix(coords[0][0], coords[0][1], zoom)
    b = deg2pix(coords[1][0], coords[1][1], zoom)
    st = min(a[0], b[0]), min(a[1], b[1])
    ed = max(a[0], b[0]), max(a[1], b[1])
    pixels = (st, ed)
    pixels_sz = (ed[0] - st[0], ed[1] - st[1])
    return pixels, pixels_sz


### Page size in inches
#PAGESIZE = 8.27, 11.69
#PAGESIZE = 11.69, 8.27
PAGESIZE = tuple(x / 72.0 for x in pagesizes.landscape(pagesizes.A4))
MARGIN = 0.22, 0.27
SOLAPE = 0.20, 0.20


## Parameters
# pixels = ((px_x,px_y),(px_x,px_y))
# pixel_center = (px_x, px_y)
# pixel_range = (delta_x, delta_y)
# coords = ((lat,lon), (lat,lon))
# coord_center = (lat,lon)
# coord_range = (delta_lat,delta_lon)
# zoom
# dpi
# pages
def mapPDF(pdffile, zoom, layer=2, coords=None, coord_center=None, coord_range=None, pixels=None, pixel_center=None, pixel_range=None, pages=(1, 1), dpi=None, title=None):
    # Check de parámetros
    pgsz = (PAGESIZE[0] - 2 * MARGIN[0] - SOLAPE[0], PAGESIZE[1] - 2 * MARGIN[1] - SOLAPE[1])
    pixels_sz = None

    if isinstance(pages, int):
        pages = (pages, pages)

    if zoom is not None and pixel_center is None and coord_range is not None:
        pixel_center = deg2pix(coord_center[0], coord_center[1], zoom)

    if dpi is not None and pages is not None and pixel_range is None:
        pixel_range = (int(pgsz[0] * dpi * pages[0] / 2), int(pgsz[1] * dpi * pages[1] / 2))

    if zoom is not None:
        if coords is not None:
            # Pixels en función de las coordenadas y el zoom
            pixels, pixels_sz = coord2pixels(coords, zoom)
        elif coord_center is not None:
            # Pixels en función del centro y algún rango
            if coord_range is not None:
                coords = ((coord_center[0] - coord_range[0], coord_center[1] - coord_range[1]),
                    (coord_center[0] + coord_range[0], coord_center[1] + coord_range[1]))
                pixels, pixels_sz = coord2pixels(coords, zoom)
            elif pixel_range is not None:
                a = deg2pix(coord_center[0], coord_center[1], zoom)
                pixels = ((a[0] - pixel_range[0], a[1] - pixel_range[1]), (a[0] + pixel_range[0], a[1] + pixel_range[1]))
                pixels_sz = (2 * pixel_range[0], 2 * pixel_range[1])

    if pixels is None or pixels_sz is None:
        print "You must provide more information to define the map, comeon!"
        d = locals()
        for x in d:
            print '%15s = %r' % (x, d[x])
        return False

    # Computes the dpi
    if dpi is None:
        dpix = float(pixels_sz[0]) / pages[0] / pgsz[0]
        dpiy = float(pixels_sz[1]) / pages[1] / pgsz[1]
        dpi = max(dpix, dpiy)

    pages = (
        int(math.ceil(float(pixels_sz[0]) / dpi / pgsz[0] - 0.1)),
        int(math.ceil(float(pixels_sz[1]) / dpi / pgsz[1] - 0.1)))
    print "pages needed: (%.2f,%.2f)" % (float(pixels_sz[0]) / dpi / pgsz[0] - 0.1, float(pixels_sz[1]) / dpi / pgsz[1] - 0.1)

    sz = (
        int(float(pages[0]) * dpi * pgsz[0]),
        int(float(pages[1]) * dpi * pgsz[1])
    )

    dbzoom = 17 - zoom
    st, ed = pixels

    # Centers the image in the requested area:
    dsp = (
        (sz[0] - pixels_sz[0]) / 2,
        (sz[1] - pixels_sz[1]) / 2
    )
    st = (st[0] - dsp[0], st[1] - dsp[1])
    ed = (ed[0] - dsp[0], ed[1] - dsp[1])

    # Generate the PDF
    pdf = canvas.Canvas(pdffile, pagesize=pagesizes.landscape(pagesizes.A4))
    pgw, pgh = int(round(dpi * (pgsz[0] + SOLAPE[0]))), int(round(dpi * (pgsz[1] + SOLAPE[1])))
    if title is None:
        title = pdffile
    pdf.setTitle('%s - zoom %d' % (title, zoom))
    #pdf.setFontSize(size=5)
    pdf.setStrokeColorRGB(0.2, 0.5, 0.3)

    print 'Generating pages, dpi=%.2f, pages=%dx%d, pagesize=%dx%d' % (dpi, pages[0], pages[1], pgw, pgh)

    flist = []
    for px in range(pages[0]):
        for py in range(pages[1]):
            ### Print some information over the map ###
            info = "dpi=%d zoom=%d page=%d,%d" % (int(dpi), zoom, px + 1, py + 1)
            imfn = '%s_%d_%d_%d.png' % (pdffile, zoom, px, py)
            flist.append(imfn)

            crx, cry = st[0] + int(round(px * dpi * pgsz[0])), st[1] + int(round(py * dpi * pgsz[1]))
            ctx_map.do_combine_subtile(dbzoom, layer, True, mConf, imfn, (0, 0), crop_start=(crx, cry), crop_size=(pgw, pgh))

            pdf.drawImage(imfn, MARGIN[0] * inch, MARGIN[1] * inch, width=(pgsz[0] + SOLAPE[0]) * 72.0, height=(pgsz[1] + SOLAPE[1]) * 72.0, )
            pdf.setFont("Helvetica", 7)
            pdf.drawString((PAGESIZE[0] - MARGIN[0] - 1.5) * inch, (MARGIN[1] - 0.08) * inch, info)
            pdf.drawString(MARGIN[0] * inch, (MARGIN[1] - 0.08) * inch, '%s - page %d,%d' % (title, px + 1, py + 1))
            pdf.showPage()
            print crx, cry
    pdf.save()
    del pdf
    for f in flist:
        os.unlink(f)
    print pages


def coordRange(coords):
    xr, yr = None, None
    for x, y in coords:
        if xr is None:
            xr = (x, x)
        else:
            xr = min(xr[0], x), max(xr[0], x)

        if yr is None:
            yr = (y, y)
        else:
            yr = min(yr[0], y), max(yr[0], y)
    return xr, yr


def gpxRange(files):
    if isinstance(files, str):
        files = [files]
    coordlist = []
    for fn in files:
        coordlist.append(load_gpx_coords(fn))
    return itertools.chain(*coordlist)


def main(layer):
    ### Examples

    # Export Paris in 160dpi, zoom=15 and in 2x3 landscape A4 pages. The width and height of the map is computed to fit this requirement.
    #~ mapPDF('paris_%d.pdf'%dpi, title="Paris, France", zoom=15, pages=(2, 3), coord_center=(48.856245, 2.347898), dpi=dpi, layer=layer)

    # Export a given region of Paris with the given zoom=14, in 2x2 landscape A4 pages, adjusting the dpi to the needed value.
    zoom = 8
    #~ mapPDF('paris_z%d.pdf'%zoom, title='Paris, France', zoom=zoom, pages=2, coord_center=(48.856245, 2.347898), coord_range=(0.028623, 0.084114), layer=layer)

    zoom = 7
    #~ mapPDF('euro_z%d_l%d.pdf'%(zoom,layer), title='Paris, France', zoom=zoom, pages=1, coords=((37.83, -4.45), (52.88, 23.94)), layer=layer)
    zoom = 8
    #~ mapPDF('euro_z%d_l%d.pdf'%(zoom,layer), title='Paris, France', zoom=zoom, pages=2, coords=((37.83, -4.45), (52.88, 23.94)), layer=layer)

    path = '/home/deymo/progs/voyage/toprint/'
    lst = [
        #~ ('France-west', 'france-west', 10, 3, (44.598290, -0.8500), (48.283193, 2.050)),
        #~ ('Paris, France', 'paris', 11, 3, (48.788319, 2.090836), (49.026838, 2.581100)),
        #~ ('Spain', 'spain', 10, 3, (43.369119, -3.235474), (41.166249, 3.131104)),
        #~ ('Belgium', 'belgium', 11, 3, (51.267071, 2.680664), (50.433017, 5.350342)),
        #~ ('Germany', 'germany', 10, 3, (52.869130, 12.00), (47.783635, 17.55)),
        #~ ('Hungary', 'hungary', 10, 3, (48.246626, 16.226807), (47.301585, 19.544678)),
        #~ ('Serbia', 'serbia', 10, 3, (47.569114, 18.929443), (44.606113, 20.731201)),
        #~ ('Macedonia', 'macedonia', 10, 3, (44.816916, 20.335693), (41.037931, 22.730713)),
        ('Greece', 'greece', 11, 3, (37.9, 24.00), (40.76, 21.23)),
        #~ ('', '', 10, 3, (), ()),
        #~ ('', '', 10, 3, (), ()),
        #~ ('', '', 10, 3, (), ()),
    ]
    for title, fn, zoom, pages, coord1, coord2 in lst:
        for layer in [0, ]:
            print '%s_z%d_l%d.pdf' % (path + fn, zoom, layer)
            mapPDF('%s_z%d_l%d.pdf' % (path + fn, zoom, layer), title=title, zoom=zoom, dpi=175, coords=(coord1, coord2), layer=layer)
    #~ print gpxRange(


if __name__ == '__main__':
    except_occ = False
    try:
        main(layer=2)
    except:
        except_occ = True
        raise

    finally:
        # Sory for this rude thing, but the program doesn't stop by itself
        if not except_occ:
            import signal
            os.kill(os.getpid(), signal.SIGTERM)
