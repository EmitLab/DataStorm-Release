from bson.json_util import loads
from bson.objectid import ObjectId
from pymongo import MongoClient as PyMongoClient
from sshtunnel import SSHTunnelForwarder

DEBUG = True
MONGO_SERVER = None
MONGO_CLIENT = None
STATE_CONFIG = None
EXIT_CODE = 1
ROOT_PATH = "./"

# fetch my current model
with open("model.txt") as infile:
    model_type = infile.readline().replace("\n", "")

delta_type = "node_location_diff"
start_time = 1530403220
end_time = 1630457220

if MONGO_CLIENT is None:

    # read the configuration file from next to this file
    with open(ROOT_PATH + "mongo.json") as json_data:
        mongo_config = loads(json_data.read())

    # connect to the mongo database using that configuration
    MONGO_SERVER = SSHTunnelForwarder((mongo_config["mongo_ip"], int(mongo_config["ssh_port"])),
                                      ssh_pkey=(ROOT_PATH + mongo_config["ssh_key"]),
                                      ssh_username=mongo_config["ssh_username"],
                                      remote_bind_address=('localhost', 27017),
                                      )
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    MONGO_CLIENT = PyMongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo

    # with open(ROOT_PATH + "instance.json") as json_data:
    #     STATE_CONFIG = loads(json_data.read())

    DS_RESULTS = MONGO_CLIENT["ds_results"]
    dsfr_list = DS_RESULTS.dsfr.find({"model_type": model_type, "timestamp": {"$gte": start_time, "$lte": end_time}})
    locations = dict()
    data_insert = []

    for each in dsfr_list:
        node_id = each["observation"][0]
        timestamp = each["timestamp"]
        parent = each["parent"]
        coordinate = each["coordinate"]
        tmp = dict()
        tmp["coordinate"] = coordinate
        tmp["timestamp"] = timestamp
        tmp["parent"] = parent
        if node_id in locations:
            tmp2 = locations[node_id]
            new_entry = dict()
            new_entry["_id"] = ObjectId()
            new_entry["timestamp"] = timestamp
            new_entry["parent"] = parent
            new_entry["model_type"] = model_type
            new_entry["coordinate"] = coordinate
            new_entry["delta_type"] = delta_type
            tmp_list = []
            tmp_list.append(node_id)
            tmp_list.append(str(timestamp - tmp2["timestamp"]))
            tmp_list.append(str(coordinate[0] - tmp2["coordinate"][0]))
            tmp_list.append(str(coordinate[1] - tmp2["coordinate"][1]))
            new_entry["observation"] = tmp_list
            data_insert.append(new_entry)

        locations[node_id] = tmp

    MONGO_CLIENT.ds_results.dsdr.insert_many(data_insert)
    MONGO_SERVER.stop()
