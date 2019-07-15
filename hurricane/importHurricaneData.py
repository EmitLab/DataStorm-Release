import pygrib
import numpy as np
import json
import argparse
from sshtunnel import SSHTunnelForwarder
import pymongo
import bson
from bson.decimal128 import Decimal128
# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    ("ds_core_mongo", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('localhost', 27017)
)

def csvwrite(fname, data, delimit=','):
    """ Save the data matrix as a csv file """
    if '.csv' not in fname:
        fname += '.csv'
    np.savetxt(fname, data, '%5.10f', delimiter=delimit)


def geofilter(file_name, lon_min=-87.64, lat_min=24.43, lon_max=-80.02, lat_max=31.0, verbose=True, ts=1530414000):
    
   # Create DSAR

   # Create DSIR

   # Create DSFR

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

    rain = np.float64(data[0][lat_index[0]:(lat_index[-1] + 1), lon_index[0]:(lon_index[-1] + 1)])
    lat = np.float64(data[1][lat_index[0]:(lat_index[-1] + 1), lon_index[0]:(lon_index[-1] + 1)])
    lng = np.float64(data[2][lat_index[0]:(lat_index[-1] + 1), lon_index[0]:(lon_index[-1] + 1)] - 180)
    u = grb.select(name='U component of wind')[0].values[lat_index[0]:(lat_index[-1] + 1),
                                                         lon_index[0]:(lon_index[-1] + 1)]
    v = grb.select(name='V component of wind')[0].values[lat_index[0]:(lat_index[-1] + 1),
                                                         lon_index[0]:(lon_index[-1] + 1)]
    row, col = v.shape
    
    model_type = 'hurricane'    
    dsfr_list =[]
    for i in range(row):
	for j in range(col):
            dsfr = dict()
            dsfr['_id'] = bson.objectid.ObjectId()
            dsfr['parent'] = bson.objectid.ObjectId("5b73434aa7d631e8a4bf5956")
            dsfr['model_type'] = model_type
            dsfr['timestamp'] = ts
            dsfr['coordinate'] = [np.float64(lng[i][j]), np.float64(lat[i][j])]
	    dsfr['observation'] = []
	    dsfr['observation'].append(rain[i][j])
	    dsfr['observation'].append(np.float64(u[i][j]))
	    dsfr['observation'].append(np.float64(v[i][j]))
            dsfr_list.append(dsfr)
    
    rdb.insert_many(dsfr_list)

    if verbose:
    	print('Insert data into MongoDB ds_result')

mongo_client = None
if __name__ == '__main__':
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    rdb = mongo_client.ds_results.dsfr

    begin = 1530414000
    for i in range(3, 27, 3):
        begin = begin + 10800
        print(begin) 
    	fileName = './GRIBS/gfs.0p25.2016070100.f'
	part  = str(i).zfill(3)
        fileName = fileName + part + ".grib2"
	print(fileName)
    	geofilter(fileName, -87.6400, 24, -80.0200, 31.0000, True, begin)
    MONGO_SERVER.stop()  # close the SSH tunnel
