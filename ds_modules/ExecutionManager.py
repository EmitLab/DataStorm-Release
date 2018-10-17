import sys

import paramiko
import pymongo
from sshtunnel import SSHTunnelForwarder

# SSH / Mongo Configuration #
SERVER_KEY = "../job_gateway/dsworker_rsa"

MONGO_SERVER = SSHTunnelForwarder(
    ("129.114.33.117", 22),
    ssh_username="cc",
    ssh_pkey=SERVER_KEY,
    remote_bind_address=('127.0.0.1', 27017)
)

# need the server connection to persist
MONGO_SERVER.start()  # open the SSH tunnel to the mongo server
MONGO_CLIENT = pymongo.MongoClient('127.0.0.1', MONGO_SERVER.local_bind_port)  # connect to mongo

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

    # do the execution
    ds_config = MONGO_CLIENT.ds_config.collection.find_one()
    model_run_command = ds_config["model"][MY_MODEL]["run_command"] + " &"  # this makes it async
    print("Execution command ready:\n{0}".format(model_run_command))
    cluster_state = MONGO_CLIENT.ds_state.cluster.find({"model_type": MY_MODEL})
    for instance in cluster_state:
        instance_id = int(instance["instance"])

        if len(instance["pool"]["waiting"]) == 0:
            print("No jobs for instance {0}, skipped.".format(instance_id))
            continue  # only execute if there's a job to run

        print("Job waiting for instance {0}, issuing command...".format(instance_id))

        # execute model over paramiko connection
        ssh_client = paramiko.SSHClient()
        try:
            ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())
            ssh_client.connect(hostname=instance["ip"], port=22,
                               username="cc", key_filename=SERVER_KEY)
            ssh_client.exec_command(model_run_command)
        except Exception as e:
            print(e)  # what should we do here? error state handling?
        finally:
            ssh_client.close()  # teardown - very important to not get orphaned SSH tunnels!

    state = MONGO_CLIENT.ds_state.kepler.find_one({"model_type": MY_MODEL})
    state["subactor_state"] = "PostSynchronizationManager"
    MONGO_CLIENT.ds_state.kepler.save(state)
    print("State change, EM to PSM" + " for model {0}".format(MY_MODEL))

    print("All commands issued! Closing Mongo...")
    MONGO_SERVER.stop()  # close the SSH tunnel
    print("Mongo closed.")


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
