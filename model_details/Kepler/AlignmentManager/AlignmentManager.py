import sys
import pymongo
from sshtunnel import SSHTunnelForwarder
from bson.objectid import ObjectId
import pprint
import json

# Global parameter to indicate model type
# TODO: it should be loaded from some meta-configuration??
MY_MODEL = "flood"

MONGO_IP = "ds_core_mongo"
MONGO_KEYFILE = "dsworker_rsa"

# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    (MONGO_IP, 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/{0}".format(MONGO_KEYFILE),
    remote_bind_address=('localhost', 27017)
)

# Insert Configuration to MongoDB to extract corresponding parameters
# TODO: For now, we use synthetic hurricane data as an example.
def insertDataAlignConfig():
    global MY_MODEL
    # Connect to MongoDB
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo

    # Use configuration DB
    ds_config = mongo_client["ds_config"]
    config_db = mongo_client.ds_config.collection
    DS_CONFIG = config_db.find_one()

    # Add model configurations
    DS_CONFIG["model"][MY_MODEL] = dict()
    DS_CONFIG["model"][MY_MODEL]["upstream_models"] = "hurricane"
    DS_CONFIG["model"][MY_MODEL]["downstream_models"] = "human_mobility"
    DS_CONFIG["model"][MY_MODEL]["input_window"] = 150000
    
    # Sub-components configurations (for now, only DataManager)
    DS_CONFIG["model"][MY_MODEL]["DataManager"] = dict()
    DS_CONFIG["model"][MY_MODEL]["DataManager"]["temporal_alignment"] = "EQUAL_WINDOW_SIZE"
    DS_CONFIG["model"][MY_MODEL]["DataManager"]["format"] = "tif"

    print ('done with configuration...')
    # Update configuration into MongoDB 
    config_db.update({"_id":ObjectId(DS_CONFIG["_id"])}, DS_CONFIG)

# Read JSON file to see if received DSARs are temporally aligned 
def isTemporalAligned(DSAR):
    print (' - Checking alignment...')
    # Connect to MongoDB
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    ds_config = mongo_client["ds_config"]
    config_db = mongo_client.ds_config.collection
    DS_CONFIG = config_db.find_one()
    # Fetch temporal alignment strategy
    temporal_strategy = DS_CONFIG["model"][MY_MODEL]["DataManager"]["temporal_alignment"]
    if temporal_strategy == "EQUAL_WINDOW_SIZE":
        print('\t%% Adapt equal window size temproal alignment strategy...')
        # TODO: Check DSAR information
        window_sizes = [10800, 10800]
        if(window_sizes[0] == window_sizes[1]):
            return True
        else:
            return False
    else:
        print('Not support yet...')
        return False

# Do temproal conversion
def temporalConversion(DSAR):
    print(' - Temporal converting...')
    # Connect to MongoDB
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    ds_config = mongo_client["ds_config"]
    config_db = mongo_client.ds_config.collection
    DS_CONFIG = config_db.find_one()
    aligned_DSAR = DSAR

    # Fetch temporal alignment strategy
    temporal_strategy = DS_CONFIG["model"][MY_MODEL]["DataManager"]["temporal_alignment"]
    # TODO: Update content in DSAR
    if temporal_strategy == "EQUAL_WINDOW_SIZE":
        print('Strategey: ' + str(temporal_strategy))
        # TODO: Do alignment according to alignment strategy
    else:
        print('Not support yet...')
        return None

    # Return aligned DSAR
    return aligned_DSAR

# Do format conversion
def formatConversion(tAlignedDSAR):
    print(' - Format converting...')
    # Connect to MongoDB
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    config_db = mongo_client.ds_config.collection
    DS_CONFIG = config_db.find_one()
    updated_DSAR = tAlignedDSAR
    # Fetch required data format
    data_format = DS_CONFIG["model"][MY_MODEL]["DataManager"]["format"]
    # TODO: Store reformatted files
    if data_format == "grib2":
        print('\t%% Data Format: ' + str(data_format))
        # TODO: create reformatted file and store its location in final DSAR 
    elif data_format == "tif":
        print('\t%% Data Format: ' + str(data_format))
        # TODO: create reformatted file and store its location in final DSAR
    else:
        print('Not support yet...')
        return None

    # return updated DSAR
    return updated_DSAR 


# Save aligned data into Mongo provenance DB (MPDB)
def saveAlignedResult(tAlignedDSAR):
    print(' - Saving aligned data into MPDB...')
    # Connect to MPDB and insert aligned DSAR
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    ds_results = mongo_client["ds_results"]
    results_db = mongo_client.ds_results.collection
    
    if(not isExist(results_db, tAlignedDSAR)):
        res = results_db.insert_one(dict(tAlignedDSAR), True)
        updatedID = res.inserted_id
        return updatedID
    else:
        #print('This DSAR is already existed...')
        return tAlignedDSAR["_id"]

# Save reformatted data into file and update DSAR
def saveReformattedResult(fAlignedDSAR):    
    print(' - Saving reformatted data into file...')


# Check existence of document
def isExist(collection, document):
    res = collection.find({"_id":ObjectId(document["_id"])})
    if res == None:
        return False
    else:
        return True

# Main
def main():
    #print 'Insert synthetic hurricane configuration'
    #insertDataAlignConfig()
    global MY_MODEL
    print('*** Data Manager ***')
    print(' - Received DSAR_ID:', str(sys.argv[1]))
    DSAR_ID = sys.argv[1]
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    print(' - Connected to DataStorm MongoDB')

    ## Getting Databases and collections
    # DSAR Results
    ds_results = mongo_client["ds_results"]
    ds_res_collection = ds_results['collection']

    # DSAR States
    ds_states = mongo_client["ds_state"]
    ds_state_collection = ds_states['collection']
    state = ds_state_collection.find_one()

    # Configuration
    ds_config = mongo_client["ds_config"]
    config_db = mongo_client.ds_config.collection
    DS_CONFIG = config_db.find_one()

    ready_list = []
    # check all instances
    for instance in state["cluster"]["instances"]:
        # select instances that running upstream model
        if instance["model_type"] == MY_MODEL:
            # check state of upstream model
            ready_list = instance["job_pool"]["ready"]
            print('Ready List:')
            print(ready_list)
            #TODO: Move below statement to here to handle real object ID


    # Find target DSAR document (JSON) by DSAR ID
    targetDSAR = ds_res_collection.find_one({"_id":ObjectId(DSAR_ID)})
    print(" - Number of DSIRs: " + str(len(targetDSAR['results'])))
    print("========================================================")
    for i in range(0, len(targetDSAR['results'])):
        print('DSIR-'+str(i))
        tmp = targetDSAR['results'][i]
        pprint.pprint(tmp['metadata']['temporal'])
    print("========================================================")

    # Temporal Conversion
    if(isTemporalAligned(targetDSAR)):
        print('\t%% Received DSARs are already temporal aligned')
        tAlignedDSAR = targetDSAR
    else:
        tAlignedDSAR = temporalConversion(targetDSAR)
    
    # Save aligned data into Mongo provenance DB (MPDB)
    updatedID = saveAlignedResult(tAlignedDSAR)
    # TODO: write this ID to a temporary file
    print('Updated DSAR ID: ' + str(updatedID))
    with open(".updatedDSAR_id","w") as f:
        f.write(str(updatedID))
    print('Before formatting...')
 
    # Format Conversion
    if(tAlignedDSAR is not None):
        fAlignedDSAR = formatConversion(tAlignedDSAR)
    else:
        print('Error: Aligned DSAR is Null!')
        sys.exit()

    # Save reformatted data into a file
    saveReformattedResult(fAlignedDSAR)

    # Close the SSH tunnel
    MONGO_SERVER.stop()
    print(' - Closed DB connection')

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
