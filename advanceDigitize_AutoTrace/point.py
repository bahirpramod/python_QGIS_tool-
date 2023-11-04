#! /usr/bin/python

class Point: # in degrees
  def __init__(self, lat, lon):
    self.lat = lat
    self.lon = lon
  def format(self, nDigits=7):
    return '(%.*f, %.*f)' % (nDigits, self.lat, nDigits, self.lon)
