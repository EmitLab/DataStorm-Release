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

MONGO_IP = "ds_core_mongo"
MONGO_KEYFILE = "dsworker_rsa"

# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    (MONGO_IP, 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/{0}".format(MONGO_KEYFILE),
    remote_bind_address=('localhost', 27017)
)

# Database in DS MongoDB
DS_STATE = None
DS_STATE_CLUSTER = None
DS_STATE_KEPLER = None
DS_CONFIG = None
DS_RESULTS = None


# return alignment strategy from ds_config
def get_alignment_strategy():
    alignment_strategy = DS_CONFIG['alignment_settings']['alignment_strategy']
    return alignment_strategy


# Read received DSARs from ds_state.kepler.
def get_dsar():
    print('Fetching received DSARs...')
    return DS_STATE.kepler.find_one({"model_type": MY_MODEL})["result_pool"]["to_align"][0]


# Given a DSAR, return a list of dsir which belong to it.
def get_dsir(dsar):
    print('Extract DSAR...')
    return DS_RESULTS.dsar.find_one({"_id": ObjectId(dsar)})['children']


def get_dsfr(dsir_id):
    print('Get DSFR list...')
    return DS_RESULTS.dsfr.find({"parent": ObjectId(dsir_id)})


# Check which case for alignment
def get_alignment(dsar_id, current_begin, current_end, t_begin, t_end, alignment_strategy):
    result_id = None

    # Case 0: given dsir is located in current time window
    if t_begin >= current_begin and t_end <= current_end:
        print("Don't need to aligned...")
        # put updated dsar id to Sampling Manager
        DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                                   {"$push": {"result_pool.to_sample": ObjectId(dsar_id)}})
        # remove updated dar id from Alignment Manager
        DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                                   {"$pop": {"result_pool.to_align": -1}})

    # Case 1: given dsir cross the boundary of current window
    elif t_begin >= current_begin and t_end > current_end:
        print("Need to be chunked...")
        result_id = chunking(dsar_id, current_begin, current_end, t_begin, t_end, alignment_strategy)

    # Case 2: given dsir over the boundary of current window
    elif t_begin >= current_end:
        print("Need to be shifted to next window...")

    return result_id


# TODO: should we update existed DSAR/DSIR/DSFR or create new DSAR/DSIR/DSFR??? \
# Current approach: update existed DSAR and create new DSIR and DSFR
def update_dsar(dsar_id, new_begin, new_end):
    # update DSAR with proper window
    target_dsar = DS_RESULTS.dsar.find_one({"_id": ObjectId(dsar_id)})

    # Fetch all children who within new time window
    dsir_list = target_dsar['children']
    updated_disr_list = []
    for dsir_id in dsir_list:
        target_dsir = DS_RESULTS.dsir.find_one({"_id": ObjectId(dsir_id)})

        # Create new DSIRs for this updated DSAR
        new_dsir = dict()
        new_dsir['parent'] = target_dsar['_id']
        new_dsir['_id'] = bson.objectid.ObjectId()
        new_dsir['metadata']['model_type'] = target_dsir['metadata']['model_type']
        new_dsir['metadata']['temporal']['begin'] = new_begin
        new_dsir['metadata']['temporal']['end'] = new_end
        new_dsir['metadata']['temporal']['window_size'] = new_begin
        new_dsir['metadata']['temporal']['shift_size'] = new_end
        new_dsir['metadata']['spatial']['top'] = target_dsir['metadata']['spatial']['top']
        new_dsir['metadata']['spatial']['left'] = target_dsir['metadata']['spatial']['left']
        new_dsir['metadata']['spatial']['bottom'] = target_dsir['metadata']['spatial']['bottom']
        new_dsir['metadata']['spatial']['right'] = target_dsir['metadata']['spatial']['right']
        new_dsir['metadata']['spatial']['x_resolution'] = target_dsir['metadata']['spatial']['x_resolution']
        new_dsir['metadata']['spatial']['y_resolution'] = target_dsir['metadata']['spatial']['y_resolution']
        updated_disr_list.append(new_dsir)

        # Create new DSFRs for this updated DSAR
        dsfr_list = get_dsfr(target_dsir['_id'])
        selected_dsfr_list = []
        for dsfr in dsfr_list:
            if dsfr['timestamp'] <= new_end:
                new_dsfr = dict()
                new_dsfr['_id'] = bson.objectid.ObjectId()
                new_dsfr['parent'] = new_dsir['_id']
                new_dsfr['model_type'] = dsfr['model_type']
                new_dsfr['timestamp'] = dsfr['timestamp']
                new_dsfr['coordinate'] = dsfr['coordinate']
                new_dsfr['observation'] = dsfr['observation']
                selected_dsfr_list.append(new_dsfr)
        DS_RESULTS.dsfr.insert_many(selected_dsfr_list)

    if len(updated_disr_list) > 0:
        DS_RESULTS.dsir.insert_many(updated_disr_list)

    # TODO: if we receive seed DSAR, should we update following fields?
    DS_RESULTS.dsar.update_one({"_id": ObjectId(dsar_id)},
                               {"$set": {
                                   "metadata.temporal": {"begin": new_begin, "end": new_end, "window_size": WINDOW_SIZE,
                                                         "shift_size": SHIFT_SIZE}}})
    # put updated dsar id to Sampling Manager
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$push": {"result_pool.to_sample": ObjectId(dsar_id)}})
    # remove updated dar id from Alignment Manager
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$pop": {"result_pool.to_align": -1}})
    return target_dsar['_id']


# Chunking alignment
def chunking(dsar_id, current_begin, current_end, t_begin, t_end, alignment_strategy):
    print('chunking')
    # Update dsar by chunking
    if alignment_strategy == 'equal_window_size':
        print(alignment_strategy)
        new_begin = current_begin
        new_end = current_end
        updated_dsar_id = update_dsar(dsar_id, new_begin, new_end)
        return updated_dsar_id


# Given a list of DSARs, do data alignment during specific time window
def do_alignment(dsar_list):
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
    alignment_strategy = get_alignment_strategy()
    aligned_dsar_list = []

    # Receive one single DSAR
    if len(dsar_list) == 1:
        target_dsar_id = dsar_list[0]
        target_dsar = DS_RESULTS.dsar.find_one({"_id": ObjectId(target_dsar_id)})
        t_begin = target_dsar['metadata']['temporal']['begin']
        t_end = target_dsar['metadata']['temporal']['end']
        print('target_begin:' + str(t_begin) + ' target_end: ' + str(t_end))
        print('window size for target DSAR: ' + str(t_end - t_begin))

        # check model's window size to see if we need to do any alignment
        aligned_dsar_id = get_alignment(target_dsar_id, current_begin, current_end, t_begin, t_end, alignment_strategy)
        aligned_dsar_list.append(aligned_dsar_id)
    # Receive multiple DSARs
    else:
        for dsar_id in dsar_list:
            target_dsar = DS_RESULTS.dsar.find_one({"_id": ObjectId(dsar_id)})
            t_begin = target_dsar['metadata']['temporal']['begin']
            t_end = target_dsar['metadata']['temporal']['end']
            # check model's window size to see if we need to do any alignment
            aligned_dsar_id = get_alignment(dsar_id, current_begin, current_end, t_begin, t_end, alignment_strategy)
            aligned_dsar_list.append(aligned_dsar_id)

    print('done with alignment')
    return aligned_dsar_list


# Getting Databases and collections
def initialize_db():
    global DS_CONFIG, DS_RESULTS, DS_STATE

    # open the SSH tunnel to the mongo server
    MONGO_SERVER.start()

    # connect to mongo
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)
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
    initialize_db()
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
        MONGO_SERVER.stop()
        return

    data_processed = False
    while len(current_model_state["result_pool"]["to_align"]) > 0:
        data_processed = True
        print("There is data to align - let's go!")

        # Get DSARs that send to alignment manager
        dsar_list = get_dsar()
        print('Received DSARs: ' + str(dsar_list))

        # Do alignment
        aligned_dsar_list = do_alignment(dsar_list)
        if len(aligned_dsar_list) == 0:
            print('Error in aligned DSARs!!!')
            return

        # refresh state
        current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})

    if not data_processed:
        print("WM said there was data to align, but didn't provide any - this is bad!")
        # note - don't proceed to next actor, if it's AM's turn and nothing to window - indicates a data flow bug
    else:
        # alignment complete, update state (from fresh state)
        print("AM complete, notifying SamplingManager...")
        current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
        current_model_state["subactor_state"] = "SamplingManager"
        sdb.save(current_model_state)
        print("State change, AM to SM" + " for model {0}".format(MY_MODEL))

    MONGO_SERVER.stop()


if __name__ == "__main__":

    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")

    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)
