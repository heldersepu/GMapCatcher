from __future__ import with_statement
from mapServers.googleMaps import search_location


def kml_to_markers(strFileName, marker, lookup=False):
    from xml.dom.minidom import parseString

    def getText(nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    try:
        with open(strFileName) as f:
            fileString = unicode(f.read(), errors='ignore')
        dom = parseString(fileString)
        PlacemarkElements = dom.getElementsByTagName("Placemark")
    except Exception, excInst:
        return excInst

    for element in PlacemarkElements:
        try:
            NameElement = element.getElementsByTagName("name")[0]
            PointElement = element.getElementsByTagName("Point")[0]
            CoordElement = PointElement.getElementsByTagName("coordinates")[0]
        except:
            pass
        else:
            Coord = getText(CoordElement.childNodes).split(',')
            if len(Coord) >= 2:
                strName = getText(NameElement.childNodes)
                if lookup:
                    location, c = search_location(Coord[1] + ' ' + Coord[0])
                    if (location[:6] != "error="):
                        strName += " - " + location
                marker.append_marker((Coord[1], Coord[0], 10), strName, lookup)
                marker.refresh()
    dom.unlink()


def load_gpx_coords(gpxfile):
    from xml.dom.minidom import parseString

    try:
        with open(gpxfile) as f:
            fileString = unicode(f.read(), errors='ignore')
        dom = parseString(fileString)
        trkpt = dom.getElementsByTagName("trkpt")
    except:
        raise

    coords = []
    for element in trkpt:
        try:
            elem_lat = float(element.getAttribute('lat'))
            elem_lon = float(element.getAttribute('lon'))
        except:
            pass
        else:
            coords.append((elem_lat, elem_lon))
    dom.unlink()

    return coords
