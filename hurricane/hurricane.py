import pygrib
import numpy as np
import json
import argparse
from sshtunnel import SSHTunnelForwarder
import pymongo
import bson
# SSH / Mongo Configuration #
mongo_server = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('127.0.0.1', 27017)
)

def csvwrite(fname, data, delimit=','):
    """ Save the data matrix as a csv file """
    if '.csv' not in fname:
        fname += '.csv'
    np.savetxt(fname, data, '%5.10f', delimiter=delimit)


def geofilter(file_name, lon_min=-87.64, lat_min=24.43, lon_max=-80.02, lat_max=31.0, verbose=True):
    mongo_server.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('127.0.0.1', mongo_server.local_bind_port)  # connect to mongo
    rdb = mongo_client.ds_results.collection

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
    #if verbose:
    #    print 'Saving the data to the disk.'

    # Insert grib information into MongoDB	
    rain_data = rain.tolist()
    lat_data = lat.tolist()
    lng_data = lng.tolist()
    u_data = u.tolist()
    v_data = v.tolist()

    time = dict()
    time['begin'] = "1467798000"
    time['end'] = "1467808800"
    time['window_size'] = "10800"

    doc = dict()
    doc["_id"] = bson.objectid.ObjectId()
    doc["metadata"] = dict()
    doc["metadata"]['type'] = "collated"
    doc["metadata"]['temporal'] = time
    doc["results"] = []

    for i in range(len(lat_data)):
        for j in range(len(lat_data[i])):
            tmp = dict()
            tmp['lat'] = lat_data[i][j]
            tmp['lng'] = lng_data[i][j]
            tmp['rain'] = rain_data[i][j]
            tmp['u'] = u_data[i][j]
            tmp['v'] = v_data[i][j]
            doc["results"].append(tmp)

    if verbose:
    	print('Insert data into MongoDB ds_result')
    	print('ObjectID: ' + str(doc['_id']))

    rdb.save(doc)
    mongo_server.stop()  # close the SSH tunnel

    #csvwrite(file_name + '.rain.csv', rain)
    #csvwrite(file_name + '.lat.csv', lat)
    #csvwrite(file_name + '.lng.csv', lng)
    #csvwrite(file_name + '.U.csv', u)
    #csvwrite(file_name + '.V.csv', v)

    # Creating the context for the subsequent models. 
    #if verbose:
    #    print'Creating the context for the subsequent models.'

    #config_file_name = 'config.txt'

    #config = {"grib": file_name,
    #          "param": ["rain", "lat", "lng", "U", "V"],
    #          "data": gb.validityDate,
    #          "time": gb.validityTime}

    #space = {"step": 0.25,
    #         "unit": "deg",
    #         "bound": {
    #             "lon_min": lon_min, "lat_min": lat_min,
    #             "lon_max": lon_max, "lat_max": lat_max
    #         }}

    #time = {"step": 1,
    #        "unit": "day"}

    #res = {"space": space,
    #       "time": time}

    #config["res"] = res
    #config["output_file_ext"] = ".csv"

    #with open(config_file_name, 'w') as outfile:
    #    json.dump(config, outfile)


if __name__ == '__main__':
    fileName = 'gfs.0p25.2016070100.f003.grib2'
    parser = argparse.ArgumentParser(description='Process some parameters.')
    parser.add_argument('config', help='config')
    args = parser.parse_args()
    with open(args.config, 'r') as f:
	datastore = json.load(f)
    # d, t, r = getPrecipitation(fileName, -87.6400, 24, -80.0200, 31.0000)
    # print getHurricaneCenter(fileName, -87.6400, 24, -80.0200, 31.0000)
    #geofilter(args.grib_filename, -87.6400, 24, -80.0200, 31.0000)
    grib_filename = datastore['grib']
    lon_min = datastore['res']['space']['bound']['lon_min']
    lon_max = datastore['res']['space']['bound']['lon_max']
    lat_min = datastore['res']['space']['bound']['lat_min']
    lat_max = datastore['res']['space']['bound']['lat_max']
    print('--- Hurricane Execution---')

    print('Grib file: ' + str(grib_filename))
    print('Date: ' + str(datastore['data']))
    print('Time Unit: ' + str(datastore['res']['time']['unit']))
    print('Boundary information:')
    print('\tlon_min: '+str(lon_min) + ' lon_max: ' + str(lon_max)+ ' lat_min: '+str(lat_min)+' lat_max: '+ str(lat_max))


    geofilter(grib_filename, lon_min, lat_min, lon_max, lat_max)
