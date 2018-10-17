import pymongo
from sshtunnel import SSHTunnelForwarder
from bson import objectid
import sys
import math

# SSH / Mongo Configuration #
mongo_server = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('127.0.0.1', 27017)
)

# stuff that eventually needs to come from config
CONFIG = None
MY_MODEL = None
CONTEXT = None


def main():
    global CONFIG, CONTEXT

    print("Running WindowManager for model '{0}'".format(MY_MODEL))

    print("Setting up Mongo tunnel.")
    mongo_server.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('127.0.0.1', mongo_server.local_bind_port)  # connect to mongo
    print("Mongo ready! Checking status...")

    # load ds_config
    CONFIG = mongo_client.ds_config.collection.find_one()

    sdb = mongo_client.ds_state.kepler  # works with the kepler-level pool
    rdb = mongo_client.ds_results.dsar  # window manager works with DSARs

    # read the state outbox to see what records are available for me
    state = sdb.find_one({"model_type": MY_MODEL})
    if state is None:
        raise Exception("Unknown model type: {0}".format(MY_MODEL))

    # the WindowManager will abort if:
    # 1) there is a state, 2) it's not the output manager or the WM itself
    if state["subactor_state"] != "WindowManager":
        print("Current state: {0}".format(state["subactor_state"]))
        print("We can't execute, because it's not the WindowManagers's turn yet.")
        mongo_server.stop()
        return

    if len(state["result_pool"]["to_window"]) == 0:
        print("Nothing in the windowing pool, stopping.")
        mongo_server.stop()
        return  # we were able to window, but there were no records to window; just exit

    # determine the upstream models, so we can synchronize their windows independently
    # that is, ALL upstream models must have provided sufficient records to satisfy a window
    model_list = CONFIG["model"][MY_MODEL]["upstream_models"]
    if len(model_list) == 0:
        model_list.append("undefined")
    model_window = dict()
    for model_type in model_list:
        model_window[model_type] = dict.fromkeys(["begin", "end"])
        model_window[model_type]["satisfied"] = False

    # records are temporally-ordered
    # if there are enough to satisfy the current window, repackage the constituent DSIRs into a new DSAR
    window_begin, window_end = initialize_buckets(sdb,
                                                  CONFIG["simulation_context"]["temporal"]["begin"],
                                                  CONFIG["model"][MY_MODEL]["input_window"])

    print("Target temporal window is: [{0}, {1}]".format(window_begin, window_end))

    old_dsar_list = []
    ending_list = []
    for record_id in state["result_pool"]["to_window"]:
        record = rdb.find_one({"_id": record_id})
        record_model = record["metadata"]["model_type"]

        if model_window[record_model]["satisfied"]:
            continue  # don't process records from models that have already satisfied the current window

        this_begin = model_window[record_model]["begin"]

        if this_begin is None:
            model_window[record_model]["begin"] = record["metadata"]["temporal"]["begin"]
            model_window[record_model]["end"] = record["metadata"]["temporal"]["end"]
            this_begin = model_window[record_model]["begin"]
        else:
            model_window[record_model]["end"] = record["metadata"]["temporal"]["end"]

        if this_begin >= window_end:
            # we see data from the next window;
            #       send the current window (whatever it is, even empty) and stop
            model_window[record_model]["satisfied"] = True
        else:
            # we're looking in the right window, so include this record
            old_dsar_list.append(record_id)

            # and include its end time, so that we can decide to trim it or not
            ending_list.append(model_window[record_model]["end"])

        if model_window[record_model]["end"] >= window_end:
            # our data reaches to the end of the window
            model_window[record_model]["satisfied"] = True

        # our data doesn't span the window; keep looking

    # if all models are satisfied, we need to generate DSARs from those records
    overall_satisfaction = True
    for model_type in model_list:
        overall_satisfaction = overall_satisfaction and model_window[model_type]["satisfied"]

    if overall_satisfaction:
        print("Window was satisfied! Repackage for consumption.")
        new_dsar_list = repackage_records(rdb, old_dsar_list, model_window)

        # remove the consumed records from the windowing pool, provided that
        #      their "ends" fall entirely within the current temporal window)
        state = sdb.find_one({"model_type": MY_MODEL})  # need to fetch again for freshness
        while len(old_dsar_list) > 0:
            record_id = old_dsar_list.pop()
            record_end = ending_list.pop()
            if record_end <= window_end:
                state["result_pool"]["to_window"].remove(record_id)

        # the alignment pool is equal to the records we created
        state["result_pool"]["to_align"] = new_dsar_list

        # store the updated state
        sdb.save(state)

        state["subactor_state"] = "AlignmentManager"  # ready for next sub-actor
        sdb.save(state)
        print("State change, WM to AM" + " for model {0}".format(MY_MODEL))
    else:
        print("Window was not satisfied.")

    # time to exit!
    mongo_server.stop()  # close the SSH tunnel no matter what
    print("Mongo tunnel closed.")


def repackage_records(record_db_handle, old_dsar_list, model_windows):
    print("Repackaging...")

    bunch_of_dsars = dict()
    model_list = model_windows.keys()
    for model_type in model_list:
        model_begin = model_windows[model_type]["begin"]
        model_end = model_windows[model_type]["end"]

        new_dsar = dict()
        new_dsar["_id"] = objectid.ObjectId()
        new_dsar["metadata"] = dict()
        new_dsar["metadata"]["upstream_data"] = []  # same as the upstream data for the constituent DSARs
        new_dsar["metadata"]["jobs"] = []  # same as the jobs for constituent DSARs
        new_dsar["metadata"]["downstream_data"] = []  # don't know it yet
        new_dsar["metadata"]["model_type"] = model_type
        new_dsar["metadata"]["temporal"] = \
            dict([("begin", model_begin),
                  ("end", model_end),
                  ("window_size", 0),
                  ("shift_size", 0)])
        new_dsar["metadata"]["spatial"] = None
        new_dsar["children"] = []
        new_dsar["created_by"] = "WindowManager"
        bunch_of_dsars[model_type] = new_dsar

    print("DSAR skeleton ready, populating...")

    for record_id in old_dsar_list:
        record_info = record_db_handle.find_one({"_id": record_id})
        model_type = record_info["metadata"]["model_type"]

        # inherit the spatial context from the upstream
        if bunch_of_dsars[model_type]["metadata"]["spatial"] is None:
            bunch_of_dsars[model_type]["metadata"]["spatial"] = record_info["metadata"]["spatial"]

        # job provenance is equal to the aggregate provenance of the constituent streams
        bunch_of_dsars[model_type]["metadata"]["upstream_data"] = \
            bunch_of_dsars[model_type]["metadata"]["upstream_data"] + [record_info["_id"]]
        bunch_of_dsars[model_type]["metadata"]["jobs"] = \
            bunch_of_dsars[model_type]["metadata"]["jobs"] + record_info["metadata"]["jobs"]

        # aggregate the child DSIRs (if any) into our new DSAR
        bunch_of_dsars[model_type]["children"] = \
            bunch_of_dsars[model_type]["children"] + record_info["children"]

    new_dsar_id_list = []
    for model_type in model_list:
        dsar_payload = bunch_of_dsars[model_type]
        print("Generated DSAR ID {0} for model '{1}'...".format(dsar_payload["_id"], model_type))
        record_db_handle.save(dsar_payload)
        new_dsar_id_list.append(dsar_payload["_id"])

    print("DSAR generation complete!")

    return new_dsar_id_list


def initialize_buckets(state_db_handle, begin, window_size):
    print("Fetching current temporal window...")
    state = state_db_handle.find_one({"model_type": MY_MODEL})
    if state["temporal_context"]["begin"] != 0:
        print("Valid temoral window found.")
        return state["temporal_context"]["begin"], state["temporal_context"]["end"]

    print("No valid window found, building...")
    state["temporal_context"]["begin"] = begin
    state["temporal_context"]["end"] = begin + window_size
    state["temporal_context"]["window_size"] = window_size
    state_db_handle.save(state)
    return state["temporal_context"]["begin"], state["temporal_context"]["end"]


if __name__ == "__main__":
    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")

    try:
        main()
    except Exception as e:
        print("WindowManager encountered an exception:\n{0}".format(e))
        sys.exit(1)
    finally:
        print("done")  # for Kepler compatibility - this can be used to set flags
        sys.exit(0)
