from mapUtils import altitude_to_zoom

def import_kml(strFileName):
    from xml.dom.minidom import parse

    def getText(nodelist):
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc

    dom = parse(strFileName)

    PlacemarkElements = dom.getElementsByTagName("Placemark")

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
                print strName, Coord[0], Coord[1], Coord[2], zoom
    dom.unlink() 

if __name__ == "__main__":
    import_kml('KML_Samples.kml')
