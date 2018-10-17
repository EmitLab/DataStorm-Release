import sys

import bson
import pymongo
from sshtunnel import SSHTunnelForwarder

# SSH / Mongo Configuration #
SERVER_KEY = "../job_gateway/dsworker_rsa"

MONGO_SERVER = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey=SERVER_KEY,
    remote_bind_address=('127.0.0.1', 27017)
)

# need the server connection to persist
MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
MONGO_CLIENT = pymongo.MongoClient('127.0.0.1', MONGO_SERVER.local_bind_port)  # connect to mongo


def reset_mongo():
    seed_id = None

    print("Resetting everything.......")

    # purge all the non-seed DSARs
    dsars = MONGO_CLIENT.ds_results.dsar.find()
    for dsar_record in dsars:
        if dsar_record["IS_SEED"]:
            seed_id = dsar_record["_id"]
            break
    MONGO_CLIENT.ds_results.dsar.delete_many({"IS_SEED": {"$ne": True}})

    # fix the kepler state
    kepler_state = MONGO_CLIENT.ds_state.kepler.find()
    for model in kepler_state:
        # temporal context
        model["temporal_context"] = dict()
        model["temporal_context"]["begin"] = 0
        model["temporal_context"]["end"] = 0
        model["temporal_context"]["window_size"] = 0

        # subactor state
        model["subactor_state"] = "WindowManager"

        # result pools
        for queue in model["result_pool"]:
            model["result_pool"][queue] = []

        # seed record
        if model["model_type"] == "hurricane":
            model["result_pool"]["to_window"] = [bson.objectid.ObjectId(seed_id)]

        MONGO_CLIENT.ds_state.kepler.save(model)

    # ignore the cluster state for now, it's mostly always correct anyway
    cluster_state = MONGO_CLIENT.ds_state.cluster.find()
    for instance_record in cluster_state:
        instance_record["pool"] = dict.fromkeys(["running", "waiting"], [])
        instance_record["status"] = "idle"
        instance_record["time_updated"] = 0
        MONGO_CLIENT.ds_state.cluster.save(instance_record)

    # purge everything else
    MONGO_CLIENT.ds_results.dsir.delete_many({"IS_SEED": {"$ne": True}})
    MONGO_CLIENT.ds_results.dsfr.delete_many({"IS_SEED": {"$ne": True}})
    MONGO_CLIENT.ds_results.jobs.delete_many({"IS_SEED": {"$ne": True}})

    print("Everything reset!")

    MONGO_CLIENT.close()


def main():
    reset_mongo()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Exception encountered:\n{0}".format(e))
        sys.exit(1)
    sys.exit(0)
