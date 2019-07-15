## Post-Synchronization
#  - input:
#       1. States of Jobs (From ds_states DB)
#       2. Object IDs for scheduled job
#  - output:
#       1. One or more DSARs, according to the strategy

import sys
import time

import bson
import numpy as np
import pymongo
from bson.objectid import ObjectId
from sshtunnel import SSHTunnelForwarder

# Global parameter to indicate model type
MY_MODEL = None
CACHE_DATA = False

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


def computeContribution(dsir_list):
    # TODO: make actual similarity
    return round(float(np.random.uniform(0, 1, 1)), 4)


## Getting Databases and collections
def initializeDB():
    global DS_CONFIG, DS_RESULTS, DS_STATE

    # open the SSH tunnel to the mongo server
    MONGO_SERVER.start()

    # connect to mongo
    mongo_client = pymongo.MongoClient("localhost", MONGO_SERVER.local_bind_port)
    print(" - Connected to DataStorm MongoDB")

    # DS Results
    DS_RESULTS = mongo_client["ds_results"]

    # DS States
    DS_STATE = mongo_client["ds_state"]

    # DS Configuration
    DS_CONFIG = mongo_client["ds_config"]["collection"]
    DS_CONFIG = DS_CONFIG.find_one()


# return aggregation strategy from ds_config
def getAggregationStrategy():
    aggregation_strategy = DS_CONFIG["post_synchronization_settings"]["aggregation_strategy"]
    return aggregation_strategy


def getDSFR(dsir_id, timestamp):
    # print("Get DSFR list...")
    dsfr_list = DS_RESULTS.dsfr.find({"$and": [{"parent": ObjectId(dsir_id)}, {"timestamp": timestamp}]})
    return dsfr_list


def getDSIRs():
    print("Get DSIR list...")
    kepler_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    dsir_list = kepler_state["result_pool"]["to_sync"]
    return dsir_list


def agg_average(obs_dict):
    print("averaging...")
    # result should be 2-D array, each row represents the observations for a DSFR
    result = {}
    target_dsir_id = next(iter(obs_dict))
    targetDSIR = DS_RESULTS.dsir.find_one({'_id': ObjectId(target_dsir_id)})
    timestamp_list = targetDSIR['timestamp_list']
    for t in timestamp_list:
        result[t] = None
        prevLen = 0
        prevIdx = None
        for dsir in obs_dict:
            if(MY_MODEL == 'human_mobility'):
                if result[t] is None:
                    prevLen = len(obs_dict[dsir][t])
                    prevIdx = dsir
                    result[t] = np.array(obs_dict[dsir][t])
                else:
                    curLen = len(obs_dict[dsir][t])
                    if curLen < prevLen:
                        diff = prevLen - curLen
                        for i in range(diff):
                            obs_dict[dsir][t].append([0])
                    elif curLen > prevLen:
                        diff = curLen - prevLen
                        for i in range(diff):
                            obs_dict[prevIdx][t].append([0])
                    result[t] = np.array(obs_dict[prevIdx][t]) + np.array(obs_dict[dsir][t])
            else:
                if result[t] is None:
                    result[t] = np.array(obs_dict[dsir][t])
                else:
                    result[t] = np.array(obs_dict[dsir][t]) + np.array(obs_dict[dsir][t])

        res = np.divide(result[t], len(obs_dict))
        print(res)
        result[t] = res
    print('Done with averaing...')
    return result


def getJobLink(job_id):
    targetJob = DS_RESULTS.jobs.find_one({"_id": ObjectId(job_id)})
    return targetJob["upstream_job"], targetJob["downstream_job"]


# noinspection PyTypeChecker
def createDSAR(dsir_list, aggregated_result):
    print("Creating new DSAR...")
    # Create a new DSIR template
    new_DSIR = dict()
    new_DSIR["metadata"] = dict()
    new_DSIR["metadata"]['spatial'] = dict()
    new_DSIR["metadata"]['temporal'] = dict()
    new_DSIR["_id"] = bson.objectid.ObjectId()

    # Create a new DSAR template
    new_DSAR = dict()
    new_DSAR["metadata"] = dict()
    new_DSAR["metadata"]['spatial'] = dict()
    new_DSAR["metadata"]['temporal'] = dict()
    new_DSAR["_id"] = bson.objectid.ObjectId()

    # Link new DSAR and new DSIR
    new_DSAR["children"] = [new_DSIR["_id"]]
    new_DSIR["parent"] = new_DSAR["_id"]
    new_DSAR["metadata"]["upstream_data"] = []
    new_DSAR["metadata"]["jobs"] = []

    # label for debugging
    new_DSAR["created_by"] = "PostSynchronizationManager"

    # Propagate varying DSIR information to DSAR (Provenance)
    for dsir in dsir_list:
        targetDSIR = DS_RESULTS.dsir.find_one({"_id": ObjectId(dsir)})
        newContrib = computeContribution(dsir_list)
        oldDSIR_detail = DS_RESULTS.dsir.find_one({"_id": ObjectId(dsir)})
        oldDSIR_detail['metadata']['contribution'] = newContrib
        DS_RESULTS.dsir.save(oldDSIR_detail)
        # Job provenance
        # Link upstream jobs (job_id for received DSIRs) for new DSAR
        new_DSAR["metadata"]["jobs"].append(ObjectId(targetDSIR["metadata"]["job_id"]))

        # Data provenance
        #  - upstream data
        targetJob = DS_RESULTS.jobs.find_one({'_id': ObjectId(targetDSIR["metadata"]["job_id"])})
        prevDSARs = targetJob["input_dsars"]
        for prevDSAR in prevDSARs:
            new_DSAR["metadata"]["upstream_data"].append(prevDSAR)
        print("Upstream data is connected")

        #  - downstream data
        for prev_dsar_id in prevDSARs:
            DS_RESULTS.dsar.update_one({"_id": ObjectId(prev_dsar_id)},
                                       {"$addToSet": {"metadata.downstream_data": new_DSAR["_id"]}})
        print("Downstream data is connected")

    new_DSAR["metadata"]["upstream_data"] = list(set(new_DSAR["metadata"]["upstream_data"]))
    print("Done with Propagate varying DSIR information to DSAR (Provenance)")

    # Propagate fixed previous DSIR information to new DSAR
    targetDSIR = DS_RESULTS.dsir.find_one({"_id": ObjectId(dsir_list[0])})  # arbitrarily use context from first DSIR

    new_DSAR["metadata"]["model_type"] = targetDSIR["metadata"]["model_type"]
    new_DSAR["metadata"]["temporal"]["begin"] = targetDSIR["metadata"]["temporal"]["begin"]
    new_DSAR["metadata"]["temporal"]["end"] = targetDSIR["metadata"]["temporal"]["end"]
    new_DSAR["metadata"]["temporal"]["window_size"] = targetDSIR["metadata"]["temporal"]["window_size"]
    new_DSAR["metadata"]["temporal"]["shift_size"] = targetDSIR["metadata"]["temporal"]["shift_size"]
    new_DSAR["metadata"]["spatial"]["top"] = targetDSIR["metadata"]["spatial"]["top"]
    new_DSAR["metadata"]["spatial"]["left"] = targetDSIR["metadata"]["spatial"]["left"]
    new_DSAR["metadata"]["spatial"]["bottom"] = targetDSIR["metadata"]["spatial"]["bottom"]
    new_DSAR["metadata"]["spatial"]["right"] = targetDSIR["metadata"]["spatial"]["right"]
    new_DSAR["metadata"]["spatial"]["x_resolution"] = targetDSIR["metadata"]["spatial"]["x_resolution"]
    new_DSAR["metadata"]["spatial"]["y_resolution"] = targetDSIR["metadata"]["spatial"]["y_resolution"]
    print("Done with Propagate fixed previous DSIR information to new DSAR")

    # Propagate fixed previous DSIR information to new DSIR
    new_DSIR["metadata"]["model_type"] = targetDSIR["metadata"]["model_type"]
    new_DSIR["metadata"]["temporal"]["begin"] = targetDSIR["metadata"]["temporal"]["begin"]
    new_DSIR["metadata"]["temporal"]["end"] = targetDSIR["metadata"]["temporal"]["end"]
    new_DSIR["metadata"]["temporal"]["window_size"] = targetDSIR["metadata"]["temporal"]["window_size"]
    new_DSIR["metadata"]["temporal"]["shift_size"] = targetDSIR["metadata"]["temporal"]["shift_size"]
    new_DSIR["metadata"]["spatial"]["top"] = targetDSIR["metadata"]["spatial"]["top"]
    new_DSIR["metadata"]["spatial"]["left"] = targetDSIR["metadata"]["spatial"]["left"]
    new_DSIR["metadata"]["spatial"]["bottom"] = targetDSIR["metadata"]["spatial"]["bottom"]
    new_DSIR["metadata"]["spatial"]["right"] = targetDSIR["metadata"]["spatial"]["right"]
    new_DSIR["metadata"]["spatial"]["x_resolution"] = targetDSIR["metadata"]["spatial"]["x_resolution"]
    new_DSIR["metadata"]["spatial"]["y_resolution"] = targetDSIR["metadata"]["spatial"]["y_resolution"]
    new_DSIR["timestamp_list"] = targetDSIR["timestamp_list"]

    print("Done with Propagate fixed previous DSIR information to new DSIR")

    new_DSFR_list = []
    for t in targetDSIR["timestamp_list"]:
        print("Building DSFRs for timestamp {0}".format(t))
        # Duplicate DSFRs from one of previous DSIR
        targetDSFR_list = getDSFR(targetDSIR["_id"], t)
        idx = 0
        for targetDSFR in targetDSFR_list:
            new_DSFR = dict()
            new_DSFR["_id"] = bson.objectid.ObjectId()
            new_DSFR["parent"] = new_DSIR["_id"]
            new_DSFR["model_type"] = targetDSFR["model_type"]
            new_DSFR["timestamp"] = targetDSFR["timestamp"]
            new_DSFR["coordinate"] = targetDSFR["coordinate"]
            re = aggregated_result[t][idx, :]
            row = re.shape
            if row[0] == 1:
                new_DSFR["observation"] = [np.float64(aggregated_result[t][idx, :]).tolist()]
            else:
                new_DSFR["observation"] = np.float64(aggregated_result[t][idx, :]).tolist()
            # print("Idx - '+str(idx)+', obs: " + str(new_DSFR["observation"]))
            new_DSFR_list.append(new_DSFR)
            idx = idx + 1

    print("Done with Duplicate DSFRs from one of previous DSIR")
    # TODO: comapring similiarity between newDSIR and received DSIRS, storing simility in received DSIR

    return new_DSAR, new_DSIR, new_DSFR_list


def doAggregation(obs_dict):
    print("Doing aggregation...")
    # Get aggregation strategy
    aggregation_strategy = getAggregationStrategy()
    aggregated_result = None
    if aggregation_strategy == 'average':
        aggregated_result = agg_average(obs_dict)
    else:
        print("Invalid aggregation strategy...")

    # Store aggregated result into file
    # np.savetxt("cached_data.csv', aggregated_result, delimiter=',', fmt='%f")

    return aggregated_result


def doSynchronization(dsir_list):
    print("Synchronizing...")
    # Traverse DSIRs to extract their observation
    aggregated_result = None
    if CACHE_DATA == True:
        print("reading cached file for aggregation result...")
        aggregated_result = np.loadtxt(open("./cached_data.csv', 'r"), delimiter=",")
    else:
        obs_dict = {}  # key: dsir_id, value: the vector of observation in given dsir_id
        # fetch observation matrix for each DSIR at given timestamps
        for dsir in dsir_list:
            targetDSIR = DS_RESULTS.dsir.find_one({'_id': ObjectId(dsir)})
            obs_dict[dsir] = {}
            timestamp_list = targetDSIR["timestamp_list"]
            for t in timestamp_list:
                obs_dict[dsir][t] = []
                dsfr_list = getDSFR(dsir, t)
                for dsfr in dsfr_list:
                    obs_list = dsfr["observation"]
                    obs_dict[dsir][t].append(obs_list)

        print("Done with getting observations...")
        # Obs_dict: [dsir_id][t][dsfrs]

        # aggregation
        aggregated_result = doAggregation(obs_dict)
        # aggregated_result: [t][dsfrs]

    if aggregated_result is None:
        print("Error in aggregated result!!")
        return None

    # Create a new DSAR with aggregated_result
    [new_dsar, new_dsir, new_dsfr_list] = createDSAR(dsir_list, aggregated_result)

    return new_dsar, new_dsir, new_dsfr_list


def sendDSAR(new_DSAR, new_DSIR, new_DSFR_list):
    # Insert new DSAR, DSIR and DSFR
    DS_RESULTS.dsar.insert_one(new_DSAR)
    print("Done with inserting new DSAR: " + str(new_DSAR["_id"]))
    DS_RESULTS.dsir.insert_one(new_DSIR)
    print("Done with inserting new DSIR: " + str(new_DSIR["_id"]))
    DS_RESULTS.dsfr.insert_many(new_DSFR_list)
    print("Done with inserting new DSFRs")

    # Put aggregated DSAR id to Output Manager
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$set": {"result_pool.to_display": [ObjectId(new_DSAR["_id"])]}})
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$set": {"result_pool.to_output": [ObjectId(new_DSAR["_id"])]}})

    print("Done with moving new DSAR_id to output manager.")
    # remove updated DSIR id from Post-Synchronization Manager
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$set": {"result_pool.to_sync": []}})

    print("Done with moving new DSAR_id from post-synchronization manager.")


def isInstanceReady():
    result = True
    targetInstances = DS_STATE.cluster.find({"model_type": MY_MODEL})
    for inst in targetInstances:
        # the inbox is empty
        if len(inst["pool"]["waiting"]) > 0:
            result = False
            break

        # the instances are idle (i.e. running is empty too)
        if inst["status"] != "idle":
            result = False
            break
    return result


def main():
    print("*** Post-Synchronization Manager in (" + str(MY_MODEL) + ") ***")
    startTime = time.time()
    # Database initialization
    initializeDB()

    # check current kepler state
    sdb = DS_STATE.kepler  # works with the kepler-level pool
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    if current_model_state is None:
        raise Exception("Unknown model type: {0}".format(MY_MODEL))

    print("Checking to see if PSM can run...")

    # the Post-Synchronization Manager will abort if:
    # 1) there is a state, 2) it's not the SM or the PSM itself
    if current_model_state["subactor_state"] != "PostSynchronizationManager":
        print("Current state: {0}".format(current_model_state["subactor_state"]))
        print("We can't execute, because it's not the PSM's turn yet.")
        MONGO_SERVER.stop()
        return

    # if nothing to sync, don't sync
    if len(current_model_state["result_pool"]["to_sync"]) == 0:
        print("ZERO model results are ready...")
        MONGO_SERVER.stop()
        return  # we were able to align, but there were no records to alignment manager; just exit

    # if instances are not ready, don't sync
    if isInstanceReady() is False:
        print("SOME model results are ready...")
        MONGO_SERVER.stop()
        return

    print("All model results are ready! Here we go...")

    # Get DSARs that send to Post-synchronization manager
    dsir_list = getDSIRs()
    print("DSIR List: " + str(dsir_list))

    # Synchronize received DSIRs and aggregate them into a DSAR
    [new_dsar, new_dsir, new_dsfr_list] = doSynchronization(dsir_list)
    if new_dsar is None:
        print("Error in aggregated DSAR")

    # Store and send generated DSAR to the Output Manager
    sendDSAR(new_dsar, new_dsir, new_dsfr_list)
    print("Total execution time: %s seconds" % (time.time() - startTime))

    # update state
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    current_model_state["subactor_state"] = "OutputManager"
    sdb.save(current_model_state)
    print("State change, PSM to OM" + " for model {0}".format(MY_MODEL))

    # Exit
    MONGO_SERVER.close()


if __name__ == "__main__":

    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")

    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)
