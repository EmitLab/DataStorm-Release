import collections
import itertools
import sys

import pymongo
from bson import objectid
from sshtunnel import SSHTunnelForwarder

from scipy import stats as scipy_stats

MONGO_IP = "ds_core_mongo"
MONGO_KEYFILE = "dsworker_rsa"

# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    (MONGO_IP, 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/{0}".format(MONGO_KEYFILE),
    remote_bind_address=('localhost', 27017)
)

# stuff that eventually needs to come from config
CONFIG = None
MY_MODEL = None
CONTEXT = None
RDB = None
SDB = None
WINDOWING_POLICY = None


def _check_compatibility_temporal(candidate_sets):
    # records are temporally-ordered
    # if there are enough to satisfy the current window, repackage the constituent DSIRs into a new DSAR
    window_begin, window_end = _quantize_temporal_window(CONFIG["simulation_context"]["temporal"]["begin"],
                                                         CONFIG["model"][MY_MODEL]["input_window"])

    print("Target temporal window is: [{0}, {1}]".format(window_begin, window_end))

    new_candidates = []

    for candidate in candidate_sets:
        # check to see if this is a valid set of results
        record_set = candidate[0]
        compat_dict = candidate[1]
        compat_dict["temporal"] = _temporal_compatibility(record_set, window_end)

        if compat_dict["temporal"] > 0:
            new_candidates.append([record_set, compat_dict])

    return new_candidates


def _check_compatibility_spatial(candidate_sets):
    spatial_context = dict(CONFIG["simulation_context"]["spatial"])
    my_spatial_res = [CONFIG["model"][MY_MODEL]["x_resolution"], CONFIG["model"][MY_MODEL]["y_resolution"]]

    new_candidates = []

    # generate spatial satisfaction template, for re-use by compatibility checker
    spatial_template = dict()
    spatial_template["x"] = dict()
    spatial_template["y"] = dict()
    while spatial_context["left"] <= spatial_context["right"]:
        spatial_template["x"][spatial_context["left"]] = None
        spatial_context["left"] = round(spatial_context["left"] + my_spatial_res[0], 5)
    while spatial_context["top"] >= spatial_context["bottom"]:
        spatial_template["y"][spatial_context["top"]] = None
        spatial_context["top"] = round(spatial_context["top"] - my_spatial_res[1], 5)

    for candidate_record_set in candidate_sets:
        # check to see if this is a valid set of results
        record_set = candidate_record_set[0]
        compat_dict = candidate_record_set[1]
        compat_dict["spatial"] = _spatial_compatibility(record_set, spatial_template)

        if compat_dict["spatial"] > 0:
            new_candidates.append([record_set, compat_dict])

    return new_candidates


def _check_compatibility_variatic(candidate_sets):
    return candidate_sets


def main():
    global CONFIG, CONTEXT, RDB, SDB, WINDOWING_POLICY

    print("Running WindowManager for model '{0}'".format(MY_MODEL))

    print("Setting up Mongo tunnel.")
    MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo
    print("Mongo ready! Checking status...")

    # load ds_config
    CONFIG = mongo_client.ds_config.collection.find_one()

    SDB = mongo_client.ds_state.kepler  # works with the kepler-level pool
    RDB = mongo_client.ds_results.dsar  # window manager works with DSARs

    # read the state outbox to see what records are available for me
    state = SDB.find_one({"model_type": MY_MODEL})
    if state is None:
        raise Exception("Unknown model type: {0}".format(MY_MODEL))

    # the WindowManager will abort if:
    # 1) there is a state, 2) it's not the output manager or the WM itself
    if state["subactor_state"] != "WindowManager":
        print("Current state: {0}".format(state["subactor_state"]))
        print("We can't execute, because it's not the WindowManagers's turn yet.")
        MONGO_SERVER.stop()
        return

    if len(state["result_pool"]["to_window"]) == 0:
        print("Nothing in the windowing pool, stopping.")
        MONGO_SERVER.stop()
        return  # we were able to window, but there were no records to window; just exit

    WINDOWING_POLICY = dict(CONFIG["windowing_settings"])  # we have to cast so that we get a copy, not a ptr

    def _power_set(input_iterable: collections.Iterable):
        s = list(input_iterable)
        return list(itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1)))

    # N.B. the powerset preserves temporal ordering! a key assumption for temporal compatibility checking
    raw_powerset = _power_set(state["result_pool"]["to_window"])
    input_powerset = []
    for entry in raw_powerset:
        metadata = dict()
        input_powerset.append([entry, metadata])

    # generate temporally-compatible candidate sets of records
    candidate_sets = _check_compatibility_temporal(input_powerset)

    # check their spatial compatibility
    candidate_sets = _check_compatibility_spatial(candidate_sets)

    # check their variatic (causal) compatibility
    candidate_sets = _check_compatibility_variatic(candidate_sets)

    if len(candidate_sets) == 0:
        print("Window was not yet satisfied; we'll try again later.")

    # recompute weights as the harmonic mean of the compatibilities
    for index in range(len(candidate_sets)):
        metrics = list(candidate_sets[index][1].values())
        hmean = scipy_stats.hmean(metrics)
        candidate_sets[index].append(hmean)

    # sort the candidates by their weighted compatibility
    candidate_sets.sort(key=lambda each: each[2], reverse=True)

    if WINDOWING_POLICY["mode"] == "most_diverse":
        # repackage the most-compatible candidate for use by the model, give better records the chance to appear
        _repackage_records(candidate_sets[0])
    else:
        # send multiple candidates to the aligner
        for each_candidate in candidate_sets[0:WINDOWING_POLICY["candidates_generated"]]:
            _repackage_records(each_candidate)

    MONGO_SERVER.stop()  # close the SSH tunnel no matter what
    print("Mongo tunnel closed.")


def _temporal_compatibility(list_of_records, window_end):
    model_window = _generate_temporal_window()

    old_dsar_list = []
    ending_list = []
    record_cache = dict()
    for record_id in list_of_records:
        record = RDB.find_one({"_id": record_id})
        record_cache[record_id] = record
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

    if len(old_dsar_list) != len(list_of_records):
        return 0  # don't allow cases where not all the records are used (this set of inputs is a superset)

    # if all models are satisfied, we need to generate DSARs from those records
    overall_satisfaction = True
    for model_type in model_window.keys():
        overall_satisfaction = overall_satisfaction and model_window[model_type]["satisfied"]

    if not overall_satisfaction:
        return 0

    # compute compatibility metric
    sec_overlap, sec_gap = 0, 0
    curr_begin, curr_end = None, None
    window_begin = float("inf")
    for record_id in list_of_records:
        record = record_cache[record_id]
        window_begin = min(window_begin, record["metadata"]["temporal"]["begin"])

        if curr_begin is None:
            curr_begin, curr_end = record["metadata"]["temporal"]["begin"], record["metadata"]["temporal"]["end"]
            continue

        if record["metadata"]["temporal"]["begin"] < curr_end:
            sec_overlap += (curr_end - record["metadata"]["temporal"]["begin"])  # there is an overlap
        elif curr_end < record["metadata"]["temporal"]["begin"]:
            sec_gap += (record["metadata"]["temporal"]["begin"] - curr_end)  # there is a gap

        curr_begin, curr_end = record["metadata"]["temporal"]["begin"], record["metadata"]["temporal"]["end"]

    window_size = window_end - window_begin
    if window_size == 0:
        return 1  # just in case it's 0, don't want a div by zero

    if WINDOWING_POLICY["mode"] == "least_gap":
        gap_weight = 2
        overlap_weight = 0
    elif WINDOWING_POLICY["mode"] == "least_overlap":
        gap_weight = 0
        overlap_weight = 2
    elif WINDOWING_POLICY["mode"] == "most_diverse":
        gap_weight = 2
        overlap_weight = 1
    elif WINDOWING_POLICY["mode"] == "most_compatible":
        gap_weight = 2
        overlap_weight = 1
    else:
        raise ValueError("Unknown windowing mode: {0}".format(WINDOWING_POLICY["mode"]))
    metric = 1 - (1 * ((gap_weight*sec_gap + overlap_weight*sec_overlap)/window_size))

    return metric


def _spatial_compatibility(list_of_records, spatial_template):
    if WINDOWING_POLICY["mode"] == "least_gap":
        gap_weight = 3
        overlap_weight = 0
    elif WINDOWING_POLICY["mode"] == "least_overlap":
        gap_weight = 0
        overlap_weight = 0.01
    elif WINDOWING_POLICY["mode"] == "most_diverse":
        gap_weight = 3
        overlap_weight = 0.01
    elif WINDOWING_POLICY["mode"] == "most_compatible":
        gap_weight = 3
        overlap_weight = 0.01
    else:
        raise ValueError("Unknown windowing mode: {0}".format(WINDOWING_POLICY["mode"]))

    spatial_satisfaction = dict()
    models = set()
    record_cache = dict()
    for record_id in list_of_records:
        record = RDB.find_one({"_id": record_id})
        record_cache[record_id] = record
        record_model = record["metadata"]["model_type"]
        models.add(record_model)
        if record_model not in spatial_satisfaction:
            spatial_satisfaction[record_model] = dict(spatial_template)

        x_bounds = [record["metadata"]["spatial"]["left"], record["metadata"]["spatial"]["right"]]
        y_bounds = [record["metadata"]["spatial"]["top"], record["metadata"]["spatial"]["bottom"]]
        rec_res = (record["metadata"]["spatial"]["x_resolution"], record["metadata"]["spatial"]["y_resolution"])

        while x_bounds[0] <= x_bounds[1]:
            if spatial_satisfaction[record_model]["x"][x_bounds[0]] is None:
                spatial_satisfaction[record_model]["x"][x_bounds[0]] = 1
            else:
                spatial_satisfaction[record_model]["x"][x_bounds[0]] += overlap_weight
            x_bounds[0] = round(x_bounds[0] + rec_res[0], 5)

        while y_bounds[0] >= y_bounds[1]:
            if spatial_satisfaction[record_model]["y"][y_bounds[0]] is None:
                spatial_satisfaction[record_model]["y"][y_bounds[0]] = 1
            else:
                spatial_satisfaction[record_model]["y"][y_bounds[0]] += overlap_weight
            y_bounds[0] = round(y_bounds[0] - rec_res[1], 5)

    # collapse the results into a unified meaning
    for model in models:
        for axis in spatial_satisfaction[model]:
            gap_score = 0
            overlap_score = 0
            resolution = len(spatial_satisfaction[model][axis])
            for cell in spatial_satisfaction[model][axis]:
                if spatial_satisfaction[model][axis][cell] is None:
                    gap_score += gap_weight
                else:
                    overlap_score += spatial_satisfaction[model][axis][cell]
            axis_score = 1 / ((gap_score + overlap_score) / resolution)
            if overlap_score == 0:
                axis_score = 0  # no overlaps means no data at all, only gaps -> minimum score
            spatial_satisfaction[model][axis] = axis_score
        model_score = min(spatial_satisfaction[model]["x"], spatial_satisfaction[model]["y"])
        spatial_satisfaction[model] = model_score
    metric = min(spatial_satisfaction.values())

    return metric


def _repackage_records(candidate_dsar_list):
    print("Repackaging...")

    # convert from candidate to DSAR list format
    candidate_dsar_list = list(candidate_dsar_list[0])

    model_begin = float("inf")
    model_end = float("-inf")
    model_list = set()

    # get temporal context of used records
    records = dict()
    for record_id in candidate_dsar_list:
        record_info = RDB.find_one({"_id": record_id})
        records[record_id] = record_info
        model_begin = min(model_begin, record_info["metadata"]["temporal"]["begin"])
        model_end = max(model_end, record_info["metadata"]["temporal"]["end"])
        model_list.add(record_info["metadata"]["model_type"])
    model_list = list(model_list)

    bunch_of_dsars = dict()
    for model_type in model_list:
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

    for record_id in candidate_dsar_list:
        record_info = RDB.find_one({"_id": record_id})
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
        RDB.save(dsar_payload)
        new_dsar_id_list.append(dsar_payload["_id"])

    print("DSAR generation complete!")

    state = SDB.find_one({"model_type": MY_MODEL})
    if WINDOWING_POLICY["mode"] == "most_diverse":
        # remove the consumed records
        for record_id in candidate_dsar_list:
            state["result_pool"]["to_window"].remove(record_id)
    else:
        # remove ALL the records
        state["result_pool"]["to_window"] = []
        state.update()

    # go to alignment manager
    state["result_pool"]["to_align"].append(new_dsar_id_list)
    state["subactor_state"] = "AlignmentManager"

    # save to mongo
    SDB.save(state)

    print("State change, WM to AM" + " for model {0}".format(MY_MODEL))


def _quantize_temporal_window(begin, window_size):
    print("Fetching current temporal window...")
    state = SDB.find_one({"model_type": MY_MODEL})
    if state["temporal_context"]["begin"] != 0:
        print("Valid temoral window found.")
        return state["temporal_context"]["begin"], state["temporal_context"]["end"]

    print("No valid window found, building...")
    state["temporal_context"]["begin"] = begin
    state["temporal_context"]["end"] = begin + window_size
    state["temporal_context"]["window_size"] = window_size
    SDB.save(state)
    return state["temporal_context"]["begin"], state["temporal_context"]["end"]


def _generate_temporal_window():
    # determine the upstream models, so we can synchronize their windows independently
    # that is, ALL upstream models must have provided sufficient records to satisfy a window
    model_list = CONFIG["model"][MY_MODEL]["upstream_models"]
    if len(model_list) == 0:
        model_list.append("undefined")
    model_window = dict()
    for model_type in model_list:
        model_window[model_type] = dict.fromkeys(["begin", "end"])
        model_window[model_type]["satisfied"] = False

    return model_window


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
