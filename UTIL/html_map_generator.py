# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 02:36:07 2018

@author: Sara Hussien
"""
import os
import random
import string

import gmplot
from bs4 import BeautifulSoup


def launch_with_gmplot(lat_long, landmark_lat_long_list_pair=None):
    fileName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + ".html"
    filePath = "./mapFiles/" + fileName

    # Initialize two empty lists to hold the latitude and longitude values
    latitude = []
    longitude = []

    # Transform the the fetched latitude and longitude data into two separate lists
    for i in range(len(lat_long)):
        latitude.append(lat_long[i][0])
        longitude.append(lat_long[i][1])

    # Initialize the map to the first location in the list
    gmap = gmplot.GoogleMapPlotter(latitude[0], longitude[0], 16)

    # Draw the points on the map. I created my own marker for '#FF66666'.
    # You can use other markers from the available list of markers.
    # Another option is to place your own marker in the folder -
    # /usr/local/lib/python3.5/dist-packages/gmplot/markers/

    if landmark_lat_long_list_pair:
        gmap.scatter(landmark_lat_long_list_pair[0], landmark_lat_long_list_pair[1], '#554083', size=10, marker=False)

    gmap.polygon(latitude, longitude, '#FFFFFF', edge_width=10)

    gmap.draw(filePath)

    insertapikey(filePath, 'AIzaSyDSx6c1Mr4UUfx3KjWoB9jhfnZVOsQvq6o')
    os.system('start chrome {}'.format(filePath))


def insertapikey(fname, apikey):
    """put the google api key in a html file"""

    def putkey(htmltxt, apikey, apistring=None):
        """put the apikey in the htmltxt and return soup"""
        if not apistring:
            apistring = "https://maps.googleapis.com/maps/api/js?key=%s&callback=initMap"
        soup = BeautifulSoup(htmltxt, 'html.parser')
        body = soup.body
        src = apistring % (apikey,)
        tscript = soup.new_tag("script", src=src, async="defer")
        body.insert(-1, tscript)

        tscript = soup.new_tag("script")
        tscript.append(soup.find_all('script')[1].text[:-232] + 'polygon = new google.maps.Polyline({path: coords,geodesic: true,strokeColor: "#FF0000",' \
                                                                'strokeOpacity: 1.0,strokeWeight: 5});polygon.setMap(map);}')
        body.insert(-1, tscript)
        soup.find_all('script')[1].extract()

        return soup

    htmltxt = open(fname, 'r').read()
    soup = putkey(htmltxt, apikey)
    newtxt = soup.prettify()
    open(fname, 'w').write(newtxt)
