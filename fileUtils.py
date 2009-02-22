#A common location for all the File I/O Utilities
import os
import re

# return all the locations from a given file (filePath)
def read_file(strInfo, filePath):
    fileData = {}
    if os.path.exists(filePath):
        p = re.compile(strInfo + '="([^"]+)".*lat="([^"]+)".*lng="([^"]+)".*')
        q = re.compile('.*zoom="([^"]+)".*')
        file = open(filePath, "r")
        for line in file:
            if (line[0] != '#'):
                m = p.search(line)
                if m:
                    zoom = 10
                    z = q.search(line)
                    if z:
                        zoom = int(z.group(1))
                    fileData[m.group(1)] = (float(m.group(2)),
                                            float(m.group(3)),
                                            zoom)
        file.close()
        return fileData
    else:
        write_file(strInfo, filePath, fileData)

# Writes all the locations (fileData) to given file (filePath)
def write_file(strInfo, filePath, fileData):
    file = open(filePath, "w")
    file.write("# This is the "+ strInfo +"s file used by GMapCatcher.\n"+\
        "#\n"+\
        "# This file contains a list of Locations/Position.\n"+\
        "# Each entry should be kept on an individual line.\n"+\
        "# The latitude, longitud and zoom should be TAB separated.\n"+\
        "#\n"+\
        "# Additionally, comments (such as these) may be inserted on\n"+\
        "# lines sarting with a '#' symbol.\n"+\
        "#\n" + "# For example:\n" + "#\n" +
        ('#   '+ strInfo +'="%s"\tlat="%f"\tlng="%f"\tzoom="%i"\n' %
         ("Paris, France", 48.856667, 2.350987, 5)) + "#\n" )

    for l in fileData.keys():
        file.write(strInfo + '="%s"\tlat="%f"\tlng="%f"\tzoom="%i"\n' %
                  (l, fileData[l][0], fileData[l][1], fileData[l][2]))
    file.close()

# Checks if a directory exist if not it will be created
def check_dir(strPath, strSubPath=None):
        if (strSubPath != None):
            strPath = os.path.join(strPath, strSubPath)
        if not os.path.isdir(strPath):
            os.mkdir(strPath)
        return strPath

