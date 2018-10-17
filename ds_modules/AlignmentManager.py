## --- AlignmentManager ---
# Purpose:
# Converts inputs from disparate sources into a single, cohesive format for use by SamplingManager.
# Additionally, handled temporal scaling and alignment of results.

# 1. Receive DSARs from window manager
#  - read from ds_state.
#  - each DSAR belongs to one specific model
#  - each DSAR is satisfied for alignment
#  - if received DSAR is seed, do nothing, else the DSAR should be temporal aligned,
#    and AM need to align data (DSIRs, DSFRs) within this given time window.
#
# 2. Align these messages to fit a specific window (window size is decided by configuration).
#    Alignment could be interpolate gap within messages or chunk exceed messages
#    - Create new DSIR and DSFR with the same DSAR ID received from Window Manager
#
# 3. Output a time-series data
#  - Same DSAR received from WM,but with updated temporal context,
#    e.g. window size and shift size) to sampling manager

import bson
import pymongo
from bson.objectid import ObjectId
from sshtunnel import SSHTunnelForwarder
import sys

# Global parameter to indicate model type
MY_MODEL = None
WINDOW_SIZE = None
SHIFT_SIZE = None

# SSH / Mongo Configuration #
mongo_server = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('127.0.0.1', 27017)
)

# Database in DS MongoDB
DS_STATE = None
DS_STATE_CLUSTER = None
DS_STATE_KEPLER = None
DS_CONFIG = None
DS_RESULTS = None


# return alignment strategy from ds_config
def getAlignmentStrategy():
    alignment_strategy = DS_CONFIG['alignment_settings']['alignment_strategy']
    return alignment_strategy


# Read received DSARs from ds_state.kepler.
def getDSARs():
    print('Fetching received DSARs...')
    kepler_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    dsar_list = kepler_state["result_pool"]["to_align"]
    return dsar_list


# Given a DSAR, return a list of dsir which belong to it.
def getDSIRs(dsar):
    print('Extract DSAR...')
    targetDSAR = DS_RESULTS.dsar.find_one({"_id": ObjectId(dsar)})
    dsir_list = targetDSAR['children']
    return dsir_list


def getDSFR(dsir_id):
    print('Get DSFR list...')
    dsfr_list = DS_RESULTS.dsfr.find({"parent": ObjectId(dsir_id)})
    return dsfr_list


# Check which case for alignment
def getAlignment(dsar_id, current_begin, current_end, tBegin, tEnd, alignment_strategy):
    result_id = None

    # Case 0: given dsir is located in current time window
    if tBegin >= current_begin and tEnd <= current_end:
        print("Don't need to aligned...")
        # put updated dsar id to Sampling Manager
        DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                                   {"$push": {"result_pool.to_sample": ObjectId(dsar_id)}})
        # remove updated dar id from Alignment Manager
        DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                                   {"$set": {"result_pool.to_align": []}})


    # Case 1: given dsir cross the boundary of current window
    elif tBegin >= current_begin and tEnd > current_end:
        print("Need to be chunked...")
        result_id = chunking(dsar_id, current_begin, current_end, tBegin, tEnd, alignment_strategy)

    # Case 2: given dsir over the boundary of current window
    elif tBegin >= current_end:
        print("Need to be shifted to next window...")

    return result_id


# TODO: should we update existed DSAR/DSIR/DSFR or create new DSAR/DSIR/DSFR??? \
# Current approach: update existed DSAR and create new DSIR and DSFR
def updateDSAR(dsar_id, newBegin, newEnd):
    # update DSAR with proper window
    targetDSAR = DS_RESULTS.dsar.find_one({"_id": ObjectId(dsar_id)})

    # Fetch all children who within new time window
    dsir_list = targetDSAR['children']
    updated_disr_list = []
    for dsir_id in dsir_list:
        targetDSIR = DS_RESULTS.dsir.find_one({"_id": ObjectId(dsir_id)})

        # Create new DSIRs for this updated DSAR
        new_DSIR = dict()
        new_DSIR['parent'] = targetDSAR['_id']
        new_DSIR['_id'] = bson.objectid.ObjectId()
        new_DSIR['metadata']['model_type'] = targetDSIR['metadata']['model_type']
        new_DSIR['metadata']['temporal']['begin'] = newBegin
        new_DSIR['metadata']['temporal']['end'] = newEnd
        new_DSIR['metadata']['temporal']['window_size'] = newBegin
        new_DSIR['metadata']['temporal']['shift_size'] = newEnd
        new_DSIR['metadata']['spatial']['top'] = targetDSIR['metadata']['spatial']['top']
        new_DSIR['metadata']['spatial']['left'] = targetDSIR['metadata']['spatial']['left']
        new_DSIR['metadata']['spatial']['bottom'] = targetDSIR['metadata']['spatial']['bottom']
        new_DSIR['metadata']['spatial']['right'] = targetDSIR['metadata']['spatial']['right']
        new_DSIR['metadata']['spatial']['x_resolution'] = targetDSIR['metadata']['spatial']['x_resolution']
        new_DSIR['metadata']['spatial']['y_resolution'] = targetDSIR['metadata']['spatial']['y_resolution']
        updated_disr_list.append(new_DSIR)

        # Create new DSFRs for this updated DSAR
        dsfr_list = getDSFR(targetDSIR['_id'])
        selected_dsfr_list = []
        for dsfr in dsfr_list:
            if dsfr['timestamp'] <= newEnd:
                new_DSFR = dict()
                new_DSFR['_id'] = bson.objectid.ObjectId()
                new_DSFR['parent'] = new_DSIR['_id']
                new_DSFR['model_type'] = dsfr['model_type']
                new_DSFR['timestamp'] = dsfr['timestamp']
                new_DSFR['coordinate'] = dsfr['coordinate']
                new_DSFR['observation'] = dsfr['observation']
                selected_dsfr_list.append(new_DSFR)
        DS_RESULTS.dsfr.insert_many(selected_dsfr_list)

    if len(updated_disr_list) > 0:
        DS_RESULTS.dsir.insert_many(updated_disr_list)

    # TODO: if we receive seed DSAR, should we update following fields?
    DS_RESULTS.dsar.update_one({"_id": ObjectId(dsar_id)},
                               {"$set": {
                                   "metadata.temporal": {"begin": newBegin, "end": newEnd, "window_size": WINDOW_SIZE,
                                                         "shift_size": SHIFT_SIZE}}})
    # put updated dsar id to Sampling Manager
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$push": {"result_pool.to_sample": ObjectId(dsar_id)}})
    # remove updated dar id from Alignment Manager
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$set": {"result_pool.to_align": []}})
    return targetDSAR['_id']


# Chunking alignment
def chunking(dsar_id, current_begin, current_end, tBegin, tEnd, alignment_strategy):
    print('chunking')
    # Update dsar by chunking
    if alignment_strategy == 'equal_window_size':
        print(alignment_strategy)
        newBegin = current_begin
        newEnd = current_end
        updated_dsar_id = updateDSAR(dsar_id, newBegin, newEnd)
        return updated_dsar_id


# Given a list of DSARs, do data alignment during specific time window
def doAlignment(dsar_list):
    global WINDOW_SIZE, SHIFT_SIZE

    # Current status
    WINDOW_SIZE = DS_CONFIG['model'][MY_MODEL]['input_window']
    SHIFT_SIZE = DS_CONFIG['model'][MY_MODEL]['shift_size']
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    current_begin = current_model_state["temporal_context"]['begin']
    current_end = current_model_state["temporal_context"]['end']
    print('WINDOW_SIZE for ' + str(MY_MODEL) + ': ' + str(WINDOW_SIZE))
    print('current_begin:' + str(current_begin) + ' current_end: ' + str(current_end),
          ' size: ' + str(current_end - current_begin))

    # Get alignment strategy
    alignment_strategy = getAlignmentStrategy()
    alignedDSAR_list = []

    # Receive one single DSAR
    if len(dsar_list) == 1:
        targetDSAR_id = dsar_list[0]
        targetDSAR = DS_RESULTS.dsar.find_one({"_id": ObjectId(targetDSAR_id)})
        tBegin = targetDSAR['metadata']['temporal']['begin']
        tEnd = targetDSAR['metadata']['temporal']['end']
        print('target_begin:' + str(tBegin) + ' target_end: ' + str(tEnd))
        print('window size for target DSAR: ' + str(tEnd - tBegin))

        # check model's window size to see if we need to do any alignment
        alignedDSAR_id = getAlignment(targetDSAR_id, current_begin, current_end, tBegin, tEnd, alignment_strategy)
        alignedDSAR_list.append(alignedDSAR_id)
    # Receive multiple DSARs
    else:
        for dsar_id in dsar_list:
            targetDSAR = DS_RESULTS.dsar.find_one({"_id": ObjectId(dsar_id)})
            tBegin = targetDSAR['metadata']['temporal']['begin']
            tEnd = targetDSAR['metadata']['temporal']['end']
            # check model's window size to see if we need to do any alignment
            alignedDSAR_id = getAlignment(dsar_id, current_begin, current_end, tBegin, tEnd, alignment_strategy)
            alignedDSAR_list.append(alignedDSAR_id)

    print('done with alignment')
    return alignedDSAR_list


## Getting Databases and collections
def initializeDB():
    global DS_CONFIG, DS_RESULTS, DS_STATE

    # open the SSH tunnel to the mongo server
    mongo_server.start()

    # connect to mongo
    mongo_client = pymongo.MongoClient('127.0.0.1', mongo_server.local_bind_port)
    print(' - Connected to DataStorm MongoDB')

    # DS Results
    DS_RESULTS = mongo_client["ds_results"]

    # DS States
    DS_STATE = mongo_client["ds_state"]

    # DS Configuration
    DS_CONFIG = mongo_client["ds_config"]['collection']
    DS_CONFIG = DS_CONFIG.find_one()


# Main
def main():
    print('*** Alignment Manager in (' + str(MY_MODEL) + ') ***')

    # Database initialization
    initializeDB()
    sdb = DS_STATE.kepler  # works with the kepler-level pool

    # check current kepler state
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    if current_model_state is None:
        raise Exception("Unknown model type: {0}".format(MY_MODEL))

    # the Alignment Manager will abort if:
    # 1) there is a state, 2) it's not the WM or the AM itself
    if current_model_state["subactor_state"] != "AlignmentManager":
        print("Current state: {0}".format(current_model_state["subactor_state"]))
        print("We can't execute, because it's not the AlignmentManagers's turn yet.")
        mongo_server.stop()
        return

    if len(current_model_state["result_pool"]["to_align"]) == 0:
        print("There is no data to align, just wait for the next round.")
        mongo_server.stop()
        return  # we were able to align, but there were no records to alignment manager; just exit

    print("Alignment is needed and ready to run. Let's go!")

    # Get DSARs that send to alignment manager
    dsar_list = getDSARs()
    print('Received DSARs: ' + str(dsar_list))

    # Do alignment
    aligned_dsar_list = doAlignment(dsar_list)
    if len(aligned_dsar_list) == 0:
        print('Error in aligned DSARs!!!')
        return

    # alignment complete, update state (from fresh state)
    print("AM complete, notifying SamplingManager...")
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    current_model_state["subactor_state"] = "SamplingManager"
    sdb.save(current_model_state)
    print("State change, AM to SM" + " for model {0}".format(MY_MODEL))

    # Close the SSH tunnel
    print(' - Closed DB connection')
    mongo_server.stop()


if __name__ == "__main__":

    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")

    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)
