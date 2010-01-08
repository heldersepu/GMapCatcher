from mapUtils import altitude_to_zoom

def kml_to_markers(strFileName, marker):
    from xml.dom.minidom import parse

    def getText(nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    try:
        dom = parse(strFileName)
        PlacemarkElements = dom.getElementsByTagName("Placemark")
    except:
        return False

    for element in PlacemarkElements:
        try:
            NameElement = element.getElementsByTagName("name")[0]
            PointElement = element.getElementsByTagName("Point")[0]
            CoordElement = PointElement.getElementsByTagName("coordinates")[0]
        except:
            pass
        else:
            strName = getText(NameElement.childNodes)
            Coord = getText(CoordElement.childNodes).split(',')
            if len(Coord) >= 2:
                if len(Coord) >= 3:
                    zoom = altitude_to_zoom(Coord[2])
                else:
                    zoom = 10
                marker.append_marker((Coord[1], Coord[0], zoom), strName)
                marker.refresh()
    dom.unlink()

