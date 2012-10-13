#!/usr/bin/python
## @package gmapcatcher.cmRoute
# CloudMade route information fetcher

from mapConf import MapConf
from mapUtils import Track, TrackPoint
import gpxpy
import urllib2
import re


# http://routes.cloudmade.com/YOUR-API-KEY-GOES-HERE/api/0.3/start_point,[transit_point1,...,transit_pointN],end_point/route_type[/route_type_modifier].output_format[?lang=(Two letter ISO 3166-1 code)][&units=(km|miles)]
class cmRoute:
    def __init__(self, apikey, start, end, transit_points=None, route_type='car', name=None):
        self.apikey = apikey
        self.start = start
        self.end = end
        self.transit_points = transit_points
        self.route_type = route_type
        self.name = name
        # print self.apikey

    def buildUrl(self):
        if len(self.transit_points) > 0:
            transit_point_str = '['
            for point in self.transit_points:
                transit_point_str += '%s,%s,' % (point.latitude, point.longitude)
            transit_point_str = transit_point_str.rstrip(',')
            transit_point_str += '],'
        else:
            transit_point_str = ''
        url = 'http://routes.cloudmade.com/%s/api/0.3/%s,%s,%s%s,%s/%s.gpx?lang=en' % (
            self.apikey,
            self.start.latitude,
            self.start.longitude,
            transit_point_str,
            self.end.latitude,
            self.end.longitude,
            self.route_type,
            )
        return url

    def getWaypoints(self):
        url = self.buildUrl()
        r = urllib2.urlopen(url)
        data = r.read()
        gpx = gpxpy.parse(data)

        distance = None
        distance_re = re.compile('()(\\d+)(<\\/distance>)',re.IGNORECASE|re.DOTALL)
        m = distance_re.search(data)
        if m:
            distance = int(m.group(2)) / 1000.

        waypoints = list()
        for waypoint in gpx.waypoints:
            waypoints.append(TrackPoint(waypoint.latitude, waypoint.longitude))
        if len(waypoints) >= 1:
            if self.name:
                return Track(waypoints, self.name, distance)
            else:
                return Track(waypoints, 'CloudMade waypoints', distance)
        return None


if __name__ == '__main__':
    apikey = MapConf(None).cloudMade_API
    start = TrackPoint(61.052979, 28.096043)
    end = TrackPoint(61.064982, 28.095131)
    transit_points = [TrackPoint(61.058514, 28.104358), TrackPoint(61.063124, 28.101482)]
    cm = cmRoute(apikey, start, end, transit_points)
    print cm.getWaypoints()
