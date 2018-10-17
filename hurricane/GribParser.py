import pygrib
import numpy as np
import json


def csvwrite(fname, data, delimit=','):
    """ Save the data matrix as a csv file """
    if '.csv' not in fname:
        fname += '.csv'
    np.savetxt(fname, data, '%5.10f', delimiter=delimit)


def geofilter(file_name, lon_min=-87.64, lat_min=24.43, lon_max=-80.02, lat_max=31.0, verbose=True):
    # Creating the GRIB file object.
    if verbose:
        print 'Creating the GRIB file object.'

    grb = pygrib.open(file_name)

    # Getting the precipitation data
    if verbose:
        print 'Getting the precipitation data.'

    gb = grb.select(name='Total Precipitation')[0]
    data = gb.data()

    # Filtering the Latitude and Longitude based on the user input
    if verbose:
        print 'Filtering the Latitude and Longitude based on the user input.'

    lat_index = np.where((data[1][:, 0] >= lat_min) & (data[1][:, 0] <= lat_max))[0]
    lon_index = np.where((data[2][0, :] - 180 >= lon_min) & (data[2][0, :] - 180 <= lon_max))[0]

    # Getting the data
    if verbose:
        print 'Getting the data'

    rain = data[0][lat_index[0]:(lat_index[-1] + 1), lon_index[0]:(lon_index[-1] + 1)]
    lat = data[1][lat_index[0]:(lat_index[-1] + 1), lon_index[0]:(lon_index[-1] + 1)]
    lng = data[2][lat_index[0]:(lat_index[-1] + 1), lon_index[0]:(lon_index[-1] + 1)] - 180
    u = grb.select(name='U component of wind')[0].values[lat_index[0]:(lat_index[-1] + 1),
                                                         lon_index[0]:(lon_index[-1] + 1)]
    v = grb.select(name='V component of wind')[0].values[lat_index[0]:(lat_index[-1] + 1),
                                                         lon_index[0]:(lon_index[-1] + 1)]

    # Saving the data to the disk.
    if verbose:
        print 'Saving the data to the disk.'

    csvwrite(file_name + '.rain.csv', rain)
    csvwrite(file_name + '.lat.csv', lat)
    csvwrite(file_name + '.lng.csv', lng)
    csvwrite(file_name + '.U.csv', u)
    csvwrite(file_name + '.V.csv', v)

    # Creating the context for the subsequent models. 
    if verbose:
        print'Creating the context for the subsequent models.'

    config_file_name = 'config.txt'

    config = {"grib": file_name,
              "param": ["rain", "lat", "lng", "U", "V"],
              "data": gb.validityDate,
              "time": gb.validityTime}

    space = {"step": 0.25,
             "unit": "deg",
             "bound": {
                 "lon_min": lon_min, "lat_min": lat_min,
                 "lon_max": lon_max, "lat_max": lat_max
             }}

    time = {"step": 1,
            "unit": "day"}

    res = {"space": space,
           "time": time}

    config["res"] = res
    config["output_file_ext"] = ".csv"

    with open(config_file_name, 'w') as outfile:
        json.dump(config, outfile)


if __name__ == '__main__':
    fileName = 'gfs.0p25.2015011500.f003.grib2'
    # d, t, r = getPrecipitation(fileName, -87.6400, 24, -80.0200, 31.0000)
    # print getHurricaneCenter(fileName, -87.6400, 24, -80.0200, 31.0000)
    geofilter(fileName, -87.6400, 24, -80.0200, 31.0000)
