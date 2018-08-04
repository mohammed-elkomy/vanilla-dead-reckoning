import math
from geopy import Point
from geopy.distance import VincentyDistance
import geopy

def geopyDistance(lat, long, bearingAngleDeg, distanceMeasuredInKM):
    # Define starting point.
    start = Point(lat, long)  # lat ,long
    distance = geopy.distance.VincentyDistance(kilometers=distanceMeasuredInKM).destination(point=start, bearing=bearingAngleDeg)
    return distance.latitude, distance.longitude


def myGeoDistance(lat, long, bearingAngleDeg, distanceMeasuredInKM):
    # https://stackoverflow.com/questions/7222382/get-lat-long-given-current-point-distance-and-bearing
    R = 6378.1  # Radius of the Earth
    brng = bearingAngleDeg/180*math.pi  # Bearing is 90 degrees converted to radians.
    d = distanceMeasuredInKM  # Distance in km

    # lat2  52.20444 - the lat result I'm hoping for
    # lon2  0.36056 - the long result I'm hoping for.

    lat1 = math.radians(lat)  # Current lat point converted to radians
    lon1 = math.radians(long)  # Current long point converted to radians

    lat2 = math.asin(math.sin(lat1) * math.cos(d / R) +
                     math.cos(lat1) * math.sin(d / R) * math.cos(brng))

    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(d / R) * math.cos(lat1),
                             math.cos(d / R) - math.sin(lat1) * math.sin(lat2))

    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)

    return lat2, lon2
