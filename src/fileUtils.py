## @package src.fileUtils
# A common location for all the File I/O Utilities

import os
import re
from time import time

## Return all the locations from a given file (filePath)
def read_file(strInfo, filePath):
    fileData = {}
    if os.path.exists(filePath):
        p = re.compile(strInfo + '="([^"]+)".*lat="([^"]+)".*lng="([^"]+)".*')
        q = re.compile('.*zoom="([^"]+)".*wait="([^"]+)".*')
        r = re.compile('.*wait="([^"]+)".*')
        i = re.compile('.*id="([^"]+)".*')
        file = open(filePath, "r")
        for line in file:
            if (line[0] != '#'):
                m = p.search(line)
                if m:
                    zoom = 10
                    z = q.search(line)
                    if z:
                        zoom = int(z.group(1))
                    wait = 0
                    id = 0
                    w = r.search(line)
                    if w:
                    	wait = int(z.group(2))
                    idval = i.search(line)
                    if idval:
                    	id = int(idval.group(1))
                    #print m.group(1)	
                    fileData[int(id)] = (float(m.group(2)),
                                            float(m.group(3)),
                                            zoom,wait, id)
        file.close()
        return fileData
    else:
        write_file(strInfo, filePath, fileData)
        return None

## Writes all the locations (fileData) to given file (filePath)
def write_file(strInfo, filePath, fileData):
    try:
        file = open(filePath, "w")
    except Exception:
        print 'Error! Can NOT write file:'
        print '  ' + filePath
        return
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
        file.write(strInfo + '="%s"\tlat="%.10f"\tlng="%.10f"\tzoom="%i"\tid="%i"\twait="%i"\n' %
                  (fileData[l][4], fileData[l][0], fileData[l][1], fileData[l][2], int(l), fileData[l][3]))
    file.close()

## Append the location (strData) to given file (filePath)
def append_file(strInfo, filePath, strData, strName):
    try:
        file = open(filePath, "a")
    except Exception:
        print 'Error! Can NOT write file:'
        print '  ' + filePath
        return

    file.write(strInfo + '="%s"\tlat="%s"\tlng="%s"\tzoom="%i"\tid="%i"\twait="%i"\n' %
              (strName, strData[0][0], strData[0][1], strData[0][2]+2, strData[1], strData[2]))
    file.close()

## Writes a new gtkrc file with the given theme
def write_gtkrc(strTheme):
    filePath = './etc/gtk-2.0/gtkrc'
    try:
        file = open(filePath, "w")
    except Exception:
        print 'Error! Can NOT write file:'
        print '  ' + filePath
        return

    file.write('# You can change the GMapCatcher theme here!\n'+\
               '#\n'+\
               '#gtk-theme-name = "Industrial"\n'+\
               '#gtk-theme-name = "XFCE-4.2"\n'+\
               '\n'+\
               'gtk-theme-name = "' + strTheme + '"')
    file.close()

## Returns the current theme from the gtkrc file
def read_gtkrc():
    filePath = './etc/gtk-2.0/gtkrc'
    if os.path.exists(filePath):
        file = open(filePath, "r")
        for line in file:
            line = line.strip()
            if line.startswith('gtk-theme-name'):
                return line[17:].strip('"')

## Returns all the available themes
def get_themes():
    themesPath = './share/themes/'
    myThemes = []
    if os.path.isdir(themesPath):
        for l in os.listdir(themesPath):
            if os.path.isdir(themesPath + l) and (l[0] != '.'):
                myThemes += [l]
    return myThemes

## Checks if a directory exist if not it will be created
def check_dir(strPath, strSubPath=None):
    if (strSubPath is not None):
        strPath = os.path.join(strPath, strSubPath)
    if not os.path.isdir(strPath):
        try:
            os.mkdir(strPath)
        except Exception:
            print 'Error! Can not create directory:'
            print '  ' + strPath
    return strPath

## Deletes a given file
def del_file(filename):
    try:
        os.remove(filename)
    except:
        pass

## Remove file if is older than given time
#  (24h * 3600s) = 86400s
def delete_old(filename, intSeconds=86400):
    if os.path.isfile(filename):
        if (int(time() - os.path.getmtime(filename)) > intSeconds):
            try:
                os.remove(filename)
                return True
            except:
                pass



def read_asalt(filePath):
    print "read from asalt file"
	
	

def write_asalt(filePath,updates):
    try:
        file = open(filePath, "w")
    except Exception:
        print 'Error! Can NOT write file:'
        print '  ' + filePath
        return
    file.write("#This is the ASALT data file used by GmapCatcher\n"+\
               "#the data shown here has been returned by the vehicle\n"+\
               "#during its last journey\n"
              )
    if(updates is not None):
	    for data in updates:
	       file.write('lat="%s"\tlng="%s"\tpitch="%s"\troll="%s"\theading="%s"\tstatus="%s"\n' %
		      (str(data[0]),str(data[1]), str(data[2]), str(data[3]), str(data[4]),str(data[5])))
    file.close()

def append_asalt(filePath,data):
    print "append to asalt file"
    print data
    try:
        file = open(filePath, "a")
    except Exception:
        print 'Error! Can NOT write file:'
        print '  ' + filePath
        return
    file.write('lat="%s"\tlng="%s"\tpitch="%s"\troll="%s"\theading="%s"\tstatus="%s"\n' %
              (str(data[0]),str(data[1]), str(data[2]), str(data[3]), str(data[4]),str(data[5])))
    file.close()
    
def read_bad(filePath):
    print "read from asalt file"
    if os.path.exists(filePath):
        p = re.compile("[^,]+,[^,]+,[^,]+.*")	
	file = open(filePath, "r")
	  for line in file:
            if (line[0] != '#'):

def write_bad(filePath,areas):
    try:
        file = open(filePath, "w")
    except Exception:
        print 'Error! Can NOT write file:'
        print '  ' + filePath
        return
    file.write("#This is the data file used by GmapCatcher for the ASALT vehicle\n"+\
               "#the data shown here depicts the \"no-go\" areas\n"+\
               "#the format goes: bad area id, lat, long\n"
              )
    if(areas is not None):
	    for data in updates:
	       file.write('%s,%s,%s' %
		      (str(data[0]),str(data[1]), str(data[2])))
    file.close()

   