import sys
import numpy as np
import pygrib
from math import sin, cos, sqrt, atan2, radians

def main():
    fileName = sys.argv[1]
    grib = pygrib.open(fileName)

    # Florida peninsula bounding box coordinates 
    # adjust these values for different area
    lat_min = 24
    lat_max = 31
    lon_min = 272.36
    lon_max = 279.98
    
    # 1. Hurricane Center Coordinates
    wind = grib.select(name = 'Wind speed (gust)')[0]
    wind_data = wind.data(lat1=lat_min,lat2=lat_max,lon1=lon_min,lon2=lon_max) # get the data in the bounding box
    # wind_data[0], wind_data[1], and wind_data[2] have same dimensions
    indices = np.where(wind_data[0] == wind_data[0].min()) # wind_data[0] is the matrix of wind values
    x = indices[0][0]
    y = indices[1][0]
    lat = wind_data[1][x][y] # wind_data[1] is the matrix of lat values
    lon = wind_data[2][x][y] # wind_data[2] is the matrix of lon values
    print "Hurricane Center Coordinates:"
    print "lat: ", lat
    print "lon: ", lon

    # 2. Max Wind Speed (mph)
    max_wind_speed = wind_data[0].max()
    print "Max Wind Speed (mph): ", max_wind_speed
    
    # 3. Storm Speed (knots)
    storm_speed = max_wind_speed * 30 * .868976
    print "Storm Speed (knots): ", storm_speed

    # 4. Delta Pressure (mb)
    surface_pressure = grib.message(217)
    surface_pressure_data = surface_pressure.data(lat1=lat_min,lat2=lat_max,lon1=lon_min,lon2=lon_max) # get the data in the bounding box
    min_surface_pressure = surface_pressure_data[0].min()
    
    above_pressure = grib.message(276)
    above_pressure_data = above_pressure.data(lat1=lat_min,lat2=lat_max,lon1=lon_min,lon2=lon_max) # get the data in the bounding box
    max_above_pressure = above_pressure_data[0].max()

    delta_pressure = abs((max_above_pressure - min_surface_pressure) * .01)
    print "Delta Pressure (mb): ", delta_pressure

    # 5. Radius of Maximum Wind (miles)
    min_wind_lat = lat
    min_wind_lon = lon
    indices = np.where(wind_data[0] == wind_data[0].max()) # wind_data[0] is the matrix of wind values
    x = indices[0][0]
    y = indices[1][0]
    max_wind_lat = wind_data[1][x][y] # wind_data[1] is the matrix of lat values
    max_wind_lon = wind_data[2][x][y] # wind_data[2] is the matrix of lon values

    R = 3959.0
    lat1 = radians(min_wind_lat)
    lon1 = radians(min_wind_lon)
    lat2 = radians(max_wind_lat)
    lon2 = radians(max_wind_lon)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    distance = distance / 4 # issues with how distance was calculated, needs to be scaled down
    print "Radius of Maximum Wind (miles): ", distance
    
if __name__ == '__main__':
    main()