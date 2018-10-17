import sys
import json
import os

import pymongo
from sshtunnel import SSHTunnelForwarder

# Global parameter to indicate model type
MY_MODEL = None

# Database in DS MongoDB
DS_STATE = None
DS_STATE_CLUSTER = None
DS_STATE_KEPLER = None
DS_CONFIG = None
DS_RESULTS = None

NOTIFIER_FOLDER = "/home/cc/viz-actor/"

# SSH / Mongo Configuration #
mongo_server = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('127.0.0.1', 27017)
)


def getDSARs():
    kepler_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    dsar_list = kepler_state["result_pool"]["to_output"]
    return dsar_list


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


def increaseTemporalContext():
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    current_end = current_model_state["temporal_context"]['end']

    # Update begin time
    updated_begin = current_end
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$set": {"temporal_context.begin": updated_begin}})

    # Update end time
    updated_end = current_end + DS_CONFIG['model'][MY_MODEL]['input_window']
    DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                               {"$set": {"temporal_context.end": updated_end}})


def send_results_downstream(dsar_list):
    # find the downstream models
    downstream_model_list = DS_CONFIG["model"][MY_MODEL]["downstream_models"]
    print("Sending results to the following models:\n{0}".format(str(downstream_model_list)))

    # write the results
    for downstream_model in downstream_model_list:
        for dsar_id in dsar_list:
            # update the downstream queue
            DS_STATE.kepler.update_one({"model_type": downstream_model},
                                       {"$addToSet": {"result_pool.to_window": dsar_id}})

            # update my own queue
            DS_STATE.kepler.update_one({"model_type": MY_MODEL},
                                       {"$pull": {"result_pool.to_output": dsar_id}})

    print("The following records were successfully dispatched downstream:\n{0}".format(dsar_list))


def main():
    print('*** Output Manager in (' + str(MY_MODEL) + ') ***')

    # Database initialization
    initializeDB()

    # check current kepler state
    sdb = DS_STATE.kepler  # works with the kepler-level pool
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    if current_model_state is None:
        raise Exception("Unknown model type: {0}".format(MY_MODEL))

    # the Output Manager will abort if:
    # 1) there is a state, 2) it's not the SM or the PSM itself
    if current_model_state["subactor_state"] != "OutputManager":
        print("Current state: {0}".format(current_model_state["subactor_state"]))
        print("We can't execute, because it's not the OutputManagers's turn yet.")
        mongo_server.stop()
        return

    if len(current_model_state["result_pool"]["to_output"]) == 0:
        print("Nothing to dispatch, stopping now...")
        mongo_server.stop()
        return  # we were able to align, but there were no records to alignment manager; just exit

    # Get DSARs that send to Output manager
    dsar_list = getDSARs()
    print(dsar_list)

    # TODO: What content should OutputManager provide to visualization?? In what format?, how?

    # send end results for windowing in the downstream
    try:
        send_results_downstream(dsar_list)
    except Exception as e:
        print("Could not dispatch results downstream, with exception:\n{0}".format(str(e)))

    # Increase temporal content
    increaseTemporalContext()

    # update state
    current_model_state = DS_STATE.kepler.find_one({"model_type": MY_MODEL})
    current_model_state["subactor_state"] = "WindowManager"
    sdb.save(current_model_state)
    print("State change, OM to WM" + " for model {0}".format(MY_MODEL))

    # send the display config to viz notifier
    send_config_to_viz_notifier(MY_MODEL)

    # Exit
    print("OutputManager complete! Closing Mongo connection...")
    mongo_server.close()
    print("Mongo connection closed.")


def send_config_to_viz_notifier(model_to_notify):
    model_type = model_to_notify

    DEFAULT_CONFIG = {
        'date': {
            'begin': 'Jul 01 2018 00:00:00',
            'end': 'Jul 03 2018 00:00:00',
            'increment_hours': 0
        },
        'filters': {
            'flood': True,
            'network': True,
            'rain': True,
            'wind': True
        }
    }

    if model_type == 'hurricane':
        DEFAULT_CONFIG['filters']['network'] = False
        DEFAULT_CONFIG['filters']['flood'] = False
        files = [f for f in os.listdir(NOTIFIER_FOLDER + ".") if os.path.isfile(f) and
                 f.endswith('_viz_config.json')]
        print(files)
        if len(files) <= 3:
            for f in files:
                print("# Removing file: " + f)
                os.remove(f)

    elif model_type == 'flood':
        DEFAULT_CONFIG['filters']['network'] = False

    files = [f for f in os.listdir(NOTIFIER_FOLDER + ".") if os.path.isfile(f) and
             f.endswith(model_type + '_viz_config.json')]
    if len(files) == 1:
        for f in files:
            print("Removing file: " + f)
            os.remove(f)

    # writes the config to disk
    json.dump(DEFAULT_CONFIG, open(NOTIFIER_FOLDER + model_type + '_viz_config.json', 'w'))


if __name__ == "__main__":

    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")

    try:
        main()
        print('done')
    except Exception as e:
        print(e)
        sys.exit(1)
    sys.exit(0)
