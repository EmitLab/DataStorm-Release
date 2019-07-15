import sys
import uuid

import bson
import pymongo
from sshtunnel import SSHTunnelForwarder

# SSH / Mongo Configuration #
USE_SSH = True

MONGO_IP = "ds_core_mongo"
MONGO_KEYFILE = "dsworker_rsa"

# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    (MONGO_IP, 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/{0}".format(MONGO_KEYFILE),
    remote_bind_address=('localhost', 27017)
)

if USE_SSH:
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    MONGO_CLIENT = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
else:
    MONGO_CLIENT = pymongo.MongoClient(MONGO_IP)


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


def init_trace():
    # generate a new trace ID (this is the only place where that can happen - corresponds to a single "run")
    new_traceid = uuid.uuid4()

    # write the new traceID into the cluster state, for later use
    kepler_state = MONGO_CLIENT.ds_state.kepler.find()



def main():
    reset_mongo()
    init_trace()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Exception encountered:\n{0}".format(e))
        sys.exit(1)
    sys.exit(0)
