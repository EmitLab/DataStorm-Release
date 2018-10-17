import pymongo
from sshtunnel import SSHTunnelForwarder
import bson
import csv


# SSH / Mongo Configuration #
mongo_server = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('127.0.0.1', 27017)
)


def main():
    mongo_server.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('127.0.0.1', mongo_server.local_bind_port)  # connect to mongo
    rdb = mongo_client.ds_results.collection

    location_path = "/Users/xchen120/Desktop/default_scenario_LocationSnapshotReport.txt"

    time = dict()
    time['begin'] = "141292880"
    time['end'] = "1467808800"
    time['window_size'] = "54880000"

    with open(location_path) as f:
        reader = csv.reader(f)
        data = [r for r in reader]

    doc = dict()
    doc["_id"] = bson.objectid.ObjectId()
    doc["metadata"] = dict()
    doc["metadata"]['type'] = "collated"
    doc["metadata"]['model'] = "human_mobility"
    doc["metadata"]['temporal'] = time

    doc["results"] = []
    tmp = dict()
    tmp['location'] = dict()

    for i in range(len(data)):
        if '[' in data[i][0]:
            doc["results"].append(tmp)
            tmp = dict()
            tmp['timestamp'] = int(time['begin']) + int(data[i][0].replace("[", "").replace("]", ""))*1000
            tmp['location'] = dict()
            continue

        tmp_line = data[i][0].split(" ")
        tmp['location'][tmp_line[0]] = tmp_line[1] + "," + tmp_line[2]

    doc["results"].append(tmp)
    doc["results"].pop(0)

    doc["results"] = doc["results"][0::10]

    rdb.save(doc)
    mongo_server.stop()  # close the SSH tunnel


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
