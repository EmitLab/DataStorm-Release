import sys, os

import paramiko
import pymongo
from sshtunnel import SSHTunnelForwarder

HOMEPATH = os.path.expanduser("~")
MONGO_IP = "ds_core_mongo"
MONGO_KEYFILE = "dsworker_rsa"

KEPLER_TO_MONGO_KEYFILE = "{0}/.ssh/{1}".format(HOMEPATH, MONGO_KEYFILE)
KEPLER_TO_MODEL_KEYFILE = KEPLER_TO_MONGO_KEYFILE

# SSH / Mongo Configuration #
MONGO_SERVER = SSHTunnelForwarder(
    (MONGO_IP, 22),
    ssh_username="cc",
    ssh_pkey=KEPLER_TO_MONGO_KEYFILE,
    remote_bind_address=('localhost', 27017)
)

# need the server connection to persist
MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
MONGO_CLIENT = pymongo.MongoClient('localhost', MONGO_SERVER.local_bind_port)  # connect to mongo

MY_MODEL = None


def main():
    print("Mongo connection established.")

    # update kepler state
    state = MONGO_CLIENT.ds_state.kepler.find_one({"model_type": MY_MODEL})
    if state["subactor_state"] != "ExecutionManager":
        print("Current state: {0}".format(state["subactor_state"]))
        print("We can't execute, because it's not the ExecutionManager's turn yet.")
        MONGO_SERVER.stop()
        return

    instances = MONGO_CLIENT.ds_state.cluster.find({"model_type": MY_MODEL})

    # Checking if there are busy instances
    no_of_busy = 0
    for instance in instances:
        if (len(instance["pool"]["waiting"]) > 0 or (len(instance["pool"]["running"]) > 0)
                or instance["status"] != "idle"):
            no_of_busy += 1

    if no_of_busy != 0:
        print("Not handing from EM to PSM yet. Jobs waiting or in-process:", no_of_busy)
    # Skipping to PSM if all jobs are done
    else:
        print("All jobs completed")
        state = MONGO_CLIENT.ds_state.kepler.find_one({"model_type": MY_MODEL})
        state["subactor_state"] = "PostSynchronizationManager"
        MONGO_CLIENT.ds_state.kepler.save(state)
        print("State change, EM to PSM" + " for model {0}".format(MY_MODEL))

        MONGO_SERVER.stop()  # close the SSH tunnel
        print("Mongo closed.")
        return

    # do the execution
    ds_config = MONGO_CLIENT.ds_config.collection.find_one()
    model_run_command = ds_config["model"][MY_MODEL]["run_command"] + " &"  # this makes it async
    print("Execution command ready:\n{0}".format(model_run_command))

    instances.rewind()
    for instance in instances:
        instance_id = int(instance["instance"])

        print("{1} Jobs waiting for instance {0} ...".format(instance_id, len(instance["pool"]["waiting"])))

        if len(instance["pool"]["waiting"]) == 0:
            print("No jobs for instance {0}, skipped.".format(instance_id))
            continue  # only execute if there's a job to run

        print("Job waiting for instance {0}, issuing command...".format(instance_id))

        # execute model over paramiko connection
        ssh_client = paramiko.SSHClient()
        try:
            ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
            ssh_client.connect(hostname=instance["ip"], port=22,
                               username="cc", key_filename=KEPLER_TO_MODEL_KEYFILE)
            ssh_client.exec_command(model_run_command)
        except Exception as e:
            # what should we do here? error state handling?
            print(e)
        finally:
            ssh_client.close()  # teardown - very important to not get orphaned SSH tunnels!
    
    MONGO_SERVER.stop()  # close the SSH tunnel

    print("All commands issued!Closing Mongo...")


if __name__ == "__main__":
    with open("model.txt") as infile:
        MY_MODEL = infile.readline().replace("\n", "")
    print("ExecutionManager initiated for model '{0}'".format(MY_MODEL))

    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(1)
    print("done")  # for Kepler compatibility - this can be used to set flags
    sys.exit(0)
