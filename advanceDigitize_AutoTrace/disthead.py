#! /usr/bin/python

import math
from .point import Point
##from pyproj import Proj, transform
earthSemimajorAxis = 6378137.
earthFlattening = 1 / 298.257223563

def latLonScale(phi): # in meters per degree
  eSq = earthFlattening * (2 - earthFlattening)
  sinPhi = math.sin(math.radians(phi))
  c = 1 - eSq * sinPhi * sinPhi
  k = earthSemimajorAxis / math.degrees(math.sqrt(c))
  return ((1 - eSq) * k / c, math.cos(math.radians(phi)) * k)

def distance(p, q):
  latScale, lonScale = latLonScale((p.lat + q.lat) * 0.5)
  dx = (q.lon - p.lon) * lonScale
  dy = (q.lat - p.lat) * latScale
  return math.sqrt(dx * dx + dy * dy)

def heading(p, q):
  latScale, lonScale = latLonScale((p.lat + q.lat) * 0.5)
  h = 90 - math.degrees(math.atan2((q.lat - p.lat) * latScale,
                                   (q.lon - p.lon) * lonScale))
  if h > 180: h -= 360
  return h
def heading_without_dig(p, q):
  latScale, lonScale = latLonScale((p.lat + q.lat) * 0.5)
  h = math.atan2((q.lat - p.lat) * latScale,(q.lon - p.lon) * lonScale)
  return h
def distanceAndHeading(p, q):
  latScale, lonScale = latLonScale((p.lat + q.lat) * 0.5)
  dx = (q.lon - p.lon) * lonScale
  dy = (q.lat - p.lat) * latScale
  d = math.sqrt(dx * dx + dy * dy)
  h = (90 - math.degrees(math.atan2(dy, dx)))
  if h > 180: h -= 360
  return d, h
 
 
#-------------Imran Inamdar -----------------------------------------------------------------------------
#pyproj liberty used for conversion between 4326 to 3857 projection--(from pyproj import Proj, transform)
#https://jswhit.github.io/pyproj/pyproj-pysrc.html

#Here implement code for calculatePointPos based on heading and distance
#distance in degree Unit
def calculatePointPos(p,d,h):   
    a = math.cos(h) * d
    b = math.sin(h) * d
    lon  = p.lon + a
    lat = p.lat + b
    return Point(lat,lon)



def calculatePointPos_3857(p,d,h):  
    lon, lat = epsg_3857_to_4326(p.lat,p.lon)# return x,y
    p_4326 = calculatePointPos(Point(lat, lon),d.h)
    p_3857 = epsg_4326_to_3857(p_4326.lat,p_4326.lon)
    return p_3857
    
def distance_3857(p, q):
    lon1, lat1 = epsg_3857_to_4326(p.lat,p.lon)
    lon2, lat2 = epsg_3857_to_4326(q.lat,q.lon)
    p1 =Point(lat1, lon1)
    p2 =Point(lat2, lon2)   
    return distance(p1, q2)
def heading_3857(p, q):
    lon1, lat1 = epsg_3857_to_4326(p.lat,p.lon)
    lon2, lat2 = epsg_3857_to_4326(q.lat,q.lon)
    p1 =Point(lat1, lon1)
    p2 =Point(lat2, lon2)
    return heading(p1, q2)

def distanceAndHeading_3857(p, q):
    lon1, lat1 = epsg_3857_to_4326(p.lat,p.lon)
    lon2, lat2 = epsg_3857_to_4326(q.lat,q.lon)
    p1 =Point(lat1, lon1)
    p2 =Point(lat2, lon2)
    return distanceAndHeading(p1, q2)
def epsg_4326_to_3857(lat,lon):
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:3857')
    x,y = transform(inProj,outProj,lon, lat)
    return x, y
def epsg_3857_to_4326(x, y):
    inProj = Proj(init='epsg:3857')
    outProj = Proj(init='epsg:4326')
    lon, lat= transform(inProj,outProj,x, y)
    return lon, lat
