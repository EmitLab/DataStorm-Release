from bson.json_util import loads
from bson.objectid import ObjectId
from pymongo import MongoClient as PyMongoClient
from sshtunnel import SSHTunnelForwarder
from abc import ABC, abstractmethod


class DeltaOperator(ABC):
    MONGO_CLIENT = None
    @abstractmethod
    def mongo_connect(self):
        ROOT_PATH = "./"

        # read the configuration file from next to this file
        with open(ROOT_PATH + "mongo.json") as json_data:
            mongo_config = loads(json_data.read())

        # connect to the mongo database using that configuration
        self.MONGO_SERVER = SSHTunnelForwarder((mongo_config["mongo_ip"], int(mongo_config["ssh_port"])),
                                          ssh_pkey=(ROOT_PATH + mongo_config["ssh_key"]),
                                          ssh_username=mongo_config["ssh_username"],
                                          remote_bind_address=('localhost', 27017),
                                          )
        self.MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
        self.MONGO_CLIENT = PyMongoClient('localhost', self.MONGO_SERVER.local_bind_port)  # connect to mongo

    @abstractmethod
    def __init__(self, start_time, end_time):
        super().__init__()
        self.mongo_connect()
        ROOT_PATH = "./"

        # fetch my current model
        with open("model.txt") as infile:
            model_type = infile.readline().replace("\n", "")

        # with open(ROOT_PATH + "instance.json") as json_data:
        #     STATE_CONFIG = loads(json_data.read())

        DS_RESULTS = self.MONGO_CLIENT["ds_results"]
        self.dsfr_list = DS_RESULTS.dsfr.find({"model_type": model_type, "timestamp": {"$gte": start_time, "$lte": end_time}})
        self.data_insert = []


    @abstractmethod
    def perform(self, delta_type, model_type):

        locations = dict()

        for each in self.dsfr_list:
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
                new_entry["model_type"] = model_type + "_" + delta_type
                new_entry["coordinate"] = coordinate
                tmp_list = []
                tmp_list.append(node_id)
                tmp_list.append(str(timestamp - tmp2["timestamp"]))
                tmp_list.append(str(coordinate[0] - tmp2["coordinate"][0]))
                tmp_list.append(str(coordinate[1] - tmp2["coordinate"][1]))
                new_entry["observation"] = tmp_list
                self.data_insert.append(new_entry)

            locations[node_id] = tmp


    @abstractmethod
    def finish(self):
        self.MONGO_CLIENT.ds_results.dsfr.insert_many(self.data_insert)
        self.MONGO_SERVER.stop()
