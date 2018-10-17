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

    location_path = "/Users/xchen120/Desktop/csv/20160702_21."
    lat_file = location_path + "lat.csv"
    lng_file = location_path + "lng.csv"
    rain_file = location_path + "rain.csv"
    u_file = location_path + "U.csv"
    v_file = location_path + "V.csv"

    time = dict()
    time['begin'] = "1467798000"
    time['end'] = "1467808800"
    time['window_size'] = "10800"

    with open(lat_file) as f:
        reader = csv.reader(f)
        lat_data = [r for r in reader]

    with open(lng_file) as f:
        reader = csv.reader(f)
        lng_data = [r for r in reader]

    with open(rain_file) as f:
        reader = csv.reader(f)
        rain_data = [r for r in reader]

    with open(u_file) as f:
        reader = csv.reader(f)
        u_data = [r for r in reader]

    with open(v_file) as f:
        reader = csv.reader(f)
        v_data = [r for r in reader]

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

    rdb.save(doc)
    mongo_server.stop()  # close the SSH tunnel


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
