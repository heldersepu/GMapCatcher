## @package src.mapUpdate
# All the update related logic

import openanything
from mapConst import *
from threading import Timer


## Class used to get latest version info
class MapUpdate():
    def __init__(self, strURL):
        self.latest_version = "0.0.0.0"
        self.latest_installer = ""
        self.html_data = self.get_data(strURL)
        if self.html_data:
            splitList = self.html_data.split(SEPARATOR)
            if len(splitList) == 2:
                self.latest_version = splitList[0]
                self.latest_installer = splitList[1]

    ## Return the data from the given URL
    def get_data(self, strURL):
        try:
            oa = openanything.fetch(strURL)
            if oa['status']==200:
                return oa['data']
        except Exception:
            return False

## Launch the MapUpdate in a thread to prevent any slowdowns
def UpdateThread(*strURL):
    update =  MapUpdate(strURL[0])
    print "Latest Version: ", update.latest_version

## Function that should be called to check for updates
def CheckForUpdates(intDelay, strURL):
    #Start after a few second delay
    myThread = Timer(intDelay, UpdateThread, args=[strURL])
    myThread.start()



if __name__ == "__main__":
    # Test some URLs
    URL_list = ["http://googlecode.com", "", "HTtp://Fake.url", None,
                "http://htmltab.kb-creative.net",
                "http://gmapcatcher.googlecode.com/svn/trunk/Changelog",
                "http://gmapcatcher.googlecode.com/svn/wiki/version.wiki"]

    # Once the version is up Test should "fail" for all but the last one!
    for myURL in URL_list:
        upd = MapUpdate(myURL)
        print "|------------------------------------------------"
        print "| Testing URL: ", myURL
        print "| "
        newVersionAvailable = upd.latest_version > VERSION
        if newVersionAvailable:
            print "| Your Version: ", VERSION
            print "| "
            print "| Latest Version: ", upd.latest_version
            print "| Latest Installer: ", upd.latest_installer
            if upd.html_data:
                print "| HTML data: ", upd.html_data[:50]
            print "| "
        print "| New Version Available = ", newVersionAvailable
        print "| "
