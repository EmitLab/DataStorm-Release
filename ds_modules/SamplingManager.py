import random
import sys
import math

import bson
import pymongo
from sshtunnel import SSHTunnelForwarder

MY_MODEL = None

# SSH / Mongo Configuration #
mongo_server = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey="~/.ssh/dsworker_rsa",
    remote_bind_address=('127.0.0.1', 27017)
)


def main():
    print("Initializing SamplingManager...")
    mongo_client, config, sample_config, kepler_state = init_sampler()

    # set sub-actor state
    if kepler_state["subactor_state"] != "SamplingManager":
        print("Current state: {0}".format(kepler_state["subactor_state"]))
        print("We can't execute, because it's not the SamplingManagers's turn yet.")
        mongo_server.stop()
        return

    dsar_ids, dsar_info = parse_dsar_upstream(mongo_client, sample_config)

    if len(dsar_ids) == 0:
        # no data to sample!
        print("No DSARs to sample, stopping...")
        mongo_server.stop()
        return

    history = read_history(mongo_client, sample_config)  # TODO: currently does not consider history

    generate_samples(history, dsar_ids, dsar_info, mongo_client, config, sample_config)

    # notify the EM
    kepler_state = mongo_client.ds_state.kepler.find_one({"model_type": MY_MODEL})
    kepler_state["subactor_state"] = "ExecutionManager"
    mongo_client.ds_state.kepler.save(kepler_state)
    print("State change, SM to EM" + " for model {0}".format(MY_MODEL))

    print("SamplingManager complete!")
    mongo_server.stop()  # close the SSH tunnel


def init_sampler():
    global MY_MODEL

    # Fixed (user-defined) model and parameters
    # Flexible model parameters and their ranges
    # Fixed model data
    # Number of execution samples needed
    # Sampling strategy (selected from multiple built-in sampling strategies for each model)
    # (User-defined) Length of historical data needed for computing samples for each model

    # fetch my current model
    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")

    mongo_server.start()  # open the SSH tunnel to the mongo server
    mongo_client = pymongo.MongoClient('127.0.0.1', mongo_server.local_bind_port)  # connect to mongo

    print("Reading DS Config...")
    config_db = mongo_client.ds_config.collection
    ds_config = config_db.find_one()

    print("Reading Kepler state...")
    kepler_state = mongo_client.ds_state.kepler.find_one({"model_type": MY_MODEL})

    print("Collating sampler configuration...")
    model_config = ds_config["model"][MY_MODEL]
    upstream_models = model_config["upstream_models"]
    downstream_models = model_config["downstream_models"]
    sampler_config = ds_config['sample_settings']
    sampler_config["upstream_models"] = upstream_models
    sampler_config["downstream_models"] = downstream_models

    print(sampler_config)

    return mongo_client, ds_config, sampler_config, kepler_state


def parse_dsar_upstream(mongo_client, sample_config):
    # time window [tmin,tmax]
    # The sequence, [TS1,..., TSh]  of timestamps for which data is available
    # A set of message streams, M1...Mk (DSAR IDs)

    print("Parsing and fetching DSARs to sample...")

    sdb = mongo_client.ds_state.kepler
    state = sdb.find_one({"model_type": MY_MODEL})
    dsar_ids = state["result_pool"]["to_sample"]

    dsar_collection = mongo_client.ds_results.dsar
    dsar_info = []

    for each in dsar_ids:
        record = dsar_collection.find_one({"_id": each})
        if record is None:
            continue
        dsar_info.append(record)

    print("DSARs retrieved.")
    print(dsar_ids)

    return dsar_ids, dsar_info


def read_history(mongo_client, config):
    # time window [tmin_old,tmax_old]
    # Simulation data read from Provenance DB
    # TODO

    history = []

    print("Reading historical data...")

    # sdb = mongo_client.ds_state.cluster
    # rdb = mongo_client.ds_results.dsar

    print("History retrieved.")

    return history


def generate_samples(history, dsar_ids, dsar_info, mongo_client, config, sample_config):
    samples = []
    samples_ids = []

    print("Generating samples...")

    # Mapping Weight for samples and history branches
    cluster_state_db = mongo_client.ds_state.cluster
    jobs_db = mongo_client.ds_results.jobs

    instance_info = list(cluster_state_db.find({"model_type": MY_MODEL}))
    instance_count = len(instance_info)
    job_count = int(sample_config["num_samples"])

    # NOTE: data provenance is handled by the post-synchronizer, since it knows more about data than the sampler

    # job provenance is handled here - first, gather the upstream jobs from the upstream data
    upstream_jobs = []
    for previous_record_info in dsar_info:
        upstream_jobs = upstream_jobs + previous_record_info["metadata"]["jobs"]

    # generate the new jobs
    new_jobs = []
    for job_number in range(job_count):
        new_jobs.append(bson.objectid.ObjectId())

    # set the downstream of the upstream jobs to the new jobs (and save)
    for job_id in upstream_jobs:
        upstream_job_data = mongo_client.ds_results.jobs.find_one({"_id": job_id})
        upstream_job_data["downstream_jobs"] = new_jobs
        mongo_client.ds_results.jobs.save(upstream_job_data)

    # build all the required jobs
    new_job_id_list = []
    for new_job_id in new_jobs:
        new_job = dict()
        new_job["_id"] = new_job_id
        new_job["model_type"] = MY_MODEL
        new_job["input_dsars"] = dsar_ids  # provide all the data available from the upstream
        new_job["output_dsir"] = None
        new_job["upstream_jobs"] = upstream_jobs
        new_job["downstream_jobs"] = []
        new_job["variables"] = dict()
        new_job["weights"] = calculate_weights(new_job, history, mongo_client, sample_config)

        # actually sample the variables
        model_vars = config["model"][MY_MODEL]["variables"]
        for each_var in model_vars:
            min_bound = float(model_vars[each_var].split(",")[0])
            max_bound = float(model_vars[each_var].split(",")[1])

            # TODO variable precision
            new_job["variables"][each_var] = round(random.uniform(min_bound, max_bound), 2)

        # compute relevance based on variables
        new_job["relevance"] = compute_relevance(new_job["variables"], config["model"][MY_MODEL]["variables"])

        # remember the job ID, and store the newly-created job
        new_job_id_list.append(new_job_id)
        jobs_db.insert_one(new_job)

    # allocated the created jobs (via round robin) to the cluster instances
    curr_instance = 0
    while len(new_job_id_list) > 0:
        job_to_assign = new_job_id_list.pop()
        instance_info[curr_instance]["pool"]["waiting"].append(job_to_assign)

        # go to the next available instance
        curr_instance = curr_instance + 1
        if curr_instance >= instance_count:
            curr_instance = 0

    # record the new queues to the cloud
    for instance_state in instance_info:
        mongo_client.ds_state.cluster.save(instance_state)

    print("Updating Kepler state...")
    kepler_state = mongo_client.ds_state.kepler.find_one({"model_type": MY_MODEL})
    kepler_state["result_pool"]["to_sample"] = []
    mongo_client.ds_state.kepler.save(kepler_state)

    print("Sampling process complete!")


def calculate_weights(job_info, history, mongo_client, sample_config):
    # Mapping Weight for samples and history branches
    # TODO

    base_weight = round(float(1) / int(sample_config["num_samples"]), 2)
    weights = []
    for each in job_info["upstream_jobs"]:
        weights.append((each, base_weight))

    return weights


def compute_relevance(job_variables, sampling_variables):
    # how far away from the center of our range are our sampled values?
    total_relevance = 0
    relevance_count = 0
    for each_var in sampling_variables:
        lower, upper = sampling_variables[each_var].split(",")
        upper = float(upper)
        lower = float(lower)
        span = (upper - lower) / 2
        expected = lower + span

        diff = abs(expected - job_variables[each_var])
        relevance = 1 - (diff / (span * 2))  # on a 0.0 to 0.5 normalized inverse scale?
        total_relevance = total_relevance + relevance
        relevance_count = relevance_count + 1

    # on average, over our sampled values
    return round(total_relevance / relevance_count, 4)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
    print("done")  # for kepler compatibility
    sys.exit(0)
