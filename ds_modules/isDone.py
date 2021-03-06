import sys
import time

import bson
import numpy as np
import pymongo
from bson.objectid import ObjectId
from sshtunnel import SSHTunnelForwarder

# Global parameter to indicate model type
MY_MODEL = None

# Database in DS MongoDB
DS_STATE = None
DS_STATE_CLUSTER = None
DS_STATE_KEPLER = None
DS_CONFIG = None
DS_RESULTS = None

MONGO_IP = "ds_core_mongo"
MONGO_KEYFILE = "dsworker_rsa"

# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    (MONGO_IP, 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/{0}".format(MONGO_KEYFILE),
    remote_bind_address=('localhost', 27017)
)


## Getting Databases and collections
def initializeDB():
    global DS_CONFIG, DS_RESULTS, DS_STATE

    # open the SSH tunnel to the mongo server
    MONGO_SERVER.start()

    # connect to mongo
    mongo_client = pymongo.MongoClient("localhost", MONGO_SERVER.local_bind_port)
    # print(" - Connected to DataStorm MongoDB")

    # DS Results
    DS_RESULTS = mongo_client["ds_results"]

    # DS States
    DS_STATE = mongo_client["ds_state"]

    # DS Configuration
    DS_CONFIG = mongo_client["ds_config"]["collection"]
    DS_CONFIG = DS_CONFIG.find_one()


def findEndModel():
    res = None
    model_list = DS_CONFIG['model'].keys()
    for model_str in model_list:
        if len(DS_CONFIG['model'][model_str]['downstream_models']) == 0:
            res = model_str
            break
    return res


def main():
    # Database initialization
    initializeDB()

    final_model = findEndModel()
    #final_model = "hurricane"
    if (final_model == None):
        #print('Error in final model!')
        return

    final_model_state = DS_STATE.kepler.find_one({"model_type": final_model})

    simEnd = DS_CONFIG['simulation_context']['temporal']['end']
    modelEnd = final_model_state['temporal_context']['begin']

    if simEnd == modelEnd:
        print(1)
    else:
        print(0)

    # Exit
    MONGO_SERVER.close()


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)
