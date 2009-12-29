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
            print getText(NameElement.childNodes)
            print getText(CoordElement.childNodes)
            print " "

if __name__ == "__main__":
    import_kml('KML_Samples.kml')
