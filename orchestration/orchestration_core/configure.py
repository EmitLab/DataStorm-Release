import concurrent.futures
import datetime
import os
import pathlib

import ansible_runner
import pymongo
from sshtunnel import SSHTunnelForwarder

SERVER_INFO = None
PRIVATE_KEY = None
PARALLELIZE: bool = True
PB_DIR = os.path.join(os.path.split(os.path.dirname(__file__))[0], "playbooks")


def _timed_print(in_string, newline=True, showtime=True):
    time = datetime.datetime.now()
    if showtime:
        output = time.replace(microsecond=0).isoformat() + "\t" + in_string
    else:
        output = in_string
    if newline:
        print(output)
    else:
        print(output, end='')


def _simple_ansible(playbook_path, ip, extravars=None):
    ansible_runner.run(
        playbook=playbook_path,
        verbosity=0,
        quiet=False,
        inventory="{0} ansible_connection=ssh ansible_user=cc ansible_ssh_extra_args='-o StrictHostKeyChecking=no'"
            .format(ip),  # this assumes Chameleon!
        ssh_key=PRIVATE_KEY,
        extravars=extravars)


def _set_mongo_cluster_metadata():
    _timed_print("Tidying up the newly-created Mongo server, and storing metadata...")

    mongo_server = SSHTunnelForwarder(
        (SERVER_INFO["core"]["ds_core_mongo"], 22),
        ssh_username="cc",
        ssh_pkey="~/.ssh/{0}".format(SERVER_INFO["mongo_keyname"]),
        remote_bind_address=('localhost', 27017)
    )
    mongo_server.start()
    mongo_client = pymongo.MongoClient('localhost', mongo_server.local_bind_port)

    # delete all current cluster info
    mongo_client.ds_state.cluster.delete_many({})

    # build replacement records
    new_cluster = []
    for server in SERVER_INFO["models"]:
        instance = dict()

        server_chunks = server.split("_")
        instance["model_type"] = "_".join(server_chunks[2:-1])
        instance["instance"] = server_chunks[-1]
        instance["ip"] = SERVER_INFO["models"][server]
        instance["status"] = "idle"
        instance["time_updated"] = "0"
        instance["pool"] = dict()
        instance["pool"]["running"] = []
        instance["pool"]["waiting"] = []

        new_cluster.append(instance)
    mongo_client.ds_state.cluster.insert_many(new_cluster)

    _timed_print("Mongo server tidying is now complete!")


def configure_core():
    _timed_print("Beginning Datastorm core server configuration.")

    mongopath = os.path.join(PB_DIR, "mongo.yaml")
    vizpath = os.path.join(PB_DIR, "visualization.yaml")
    keplerpath = os.path.join(PB_DIR, "kepler.yaml")

    extravars = dict()
    extravars["mongo_ip"] = SERVER_INFO["mongo_local_ip"]
    extravars["kepler_ip"] = SERVER_INFO["kepler_local_ip"]
    extravars["ssh_keyname"] = SERVER_INFO["mongo_keyname"]
    extravars["ssh_payload"] = PRIVATE_KEY

    _timed_print("\tConfiguring [{0}]...".format("mongo"))
    _simple_ansible(mongopath, SERVER_INFO["core"]["ds_core_mongo"])

    _timed_print("\tConfiguring [{0}]...".format("visualization"))
    _simple_ansible(vizpath, SERVER_INFO["core"]["ds_core_visualization"], extravars=extravars)

    _set_mongo_cluster_metadata()

    _timed_print("\tConfiguring [{0}]...".format("kepler"))
    _simple_ansible(keplerpath, SERVER_INFO["core"]["ds_core_kepler"], extravars=extravars)

    _timed_print("Core configuration complete.")


def configure_models():
    _timed_print("Beginning Datastorm model server configuration.")

    for server in SERVER_INFO["models"]:
        server_chunks = server.split("_")
        model = "_".join(server_chunks[2:-1])
        instance_id = server_chunks[-1]
        ip = SERVER_INFO["models"][server]

        _timed_print("\tConfiguring [{0}]...".format(server))

        extravars = dict()

        # configure the job gateway
        extravars["mongo_ip"] = SERVER_INFO["mongo_local_ip"]
        extravars["ssh_port"] = 22
        extravars["ssh_key"] = SERVER_INFO["mongo_keyname"]

        extravars["model_type"] = model
        extravars["instance_id"] = instance_id

        extravars["ssh_username"] = "cc"
        extravars["ssh_payload"] = PRIVATE_KEY
        extravars["ip_table"] = IP_TABLE

        _simple_ansible(os.path.join(PB_DIR, "job_gateway.yaml"), extravars=extravars, ip=ip)

        # configure the model itself
        _simple_ansible(os.path.join(PB_DIR, "{0}.yaml".format(model)), ip=ip)

    _timed_print("Model configuration complete.")


def parallel_configure_core():
    _timed_print("Beginning Datastorm core server parallel configuration.")

    path = {"ds_core_mongo": os.path.join(PB_DIR, "mongo.yaml"),
            "ds_core_visualization": os.path.join(PB_DIR, "visualization.yaml"),
            "ds_core_kepler": os.path.join(PB_DIR, "kepler.yaml")}

    extravars = dict()
    extravars["mongo_ip"] = SERVER_INFO["mongo_local_ip"]
    extravars["kepler_ip"] = SERVER_INFO["kepler_local_ip"]
    extravars["ssh_keyname"] = SERVER_INFO["mongo_keyname"]
    extravars["ssh_payload"] = PRIVATE_KEY
    extravars["ip_table"] = IP_TABLE

    different_servers = ["ds_core_mongo", "ds_core_visualization", "ds_core_kepler"]

    future_details = []

    for server in different_servers:
        _timed_print("\tConfiguring [{0}]...".format(server))
        server_ip = SERVER_INFO["core"][server]
        future_details.append((path[server], server_ip, extravars))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_compilation = {executor.submit(_simple_ansible, details[0], details[1], details[2]): details
                              for details in future_details}
        for future in concurrent.futures.as_completed(future_compilation):
            results_holder = future_compilation[future]
            try:
                data = future.result()
            except Exception as exc:
                _timed_print("Load Failed")
                _timed_print(' %r generated an exception: %s' % (results_holder, exc))
            else:
                _timed_print("Successfully Loaded " + str(data))

    _set_mongo_cluster_metadata()

    _timed_print("Core configuration complete.")


def parallel_server_model_config(details):
    server_ip, extravars = details[0], details[1]
    _simple_ansible(os.path.join(extravars["role_path"], "job_gateway.yaml"), extravars=extravars, ip=server_ip)
    # configure the model itself
    _simple_ansible(os.path.join(extravars["role_path"], "{0}.yaml".format(extravars["model_type"])),
                    extravars=extravars, ip=server_ip)


def parallel_configure_model():
    _timed_print("Beginning DataStorm Model Server Parallel Configuration.")

    future_details = list()
    print("IP_TABLE Generated :\n" + str(IP_TABLE))

    for server in SERVER_INFO["models"]:
        server_chunks = server.split("_")
        model = "_".join(server_chunks[2:-1])
        instance_id = server_chunks[-1]
        ip = SERVER_INFO["models"][server]

        _timed_print("\tConfiguring [{0}]...".format(server))

        extravars = dict()

        # configure the job gateway
        extravars["mongo_ip"] = SERVER_INFO["mongo_local_ip"]
        extravars["ssh_port"] = 22
        extravars["ssh_key"] = SERVER_INFO["mongo_keyname"]

        extravars["model_type"] = model
        extravars["instance_id"] = instance_id

        extravars["ssh_username"] = "cc"
        extravars["ssh_payload"] = PRIVATE_KEY
        extravars["role_path"] = os.path.join(PB_DIR)
        extravars["ip_table"] = IP_TABLE

        future_details.append((ip, extravars))

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_compilation = {executor.submit(parallel_server_model_config, details): details
                              for details in future_details}
        for future in concurrent.futures.as_completed(future_compilation):
            results_holder = future_compilation[future]
            try:
                data = future.result()
            except Exception as exc:
                _timed_print("Load Failed")
                _timed_print(' %r generated an exception: %s' % (results_holder, exc))
            else:
                _timed_print("Successfully Configured " + str(data))

    _timed_print("Model configuration complete.")


def configure_all(server_info):
    global SERVER_INFO, PRIVATE_KEY, IP_TABLE

    # getting started
    global_start = datetime.datetime.now()
    print("")
    _timed_print("----- Configuring DataStorm -----".format(global_start.isoformat()))

    # parse raw server info from upstream
    SERVER_INFO = dict()
    SERVER_INFO["core"] = dict()
    SERVER_INFO["models"] = dict()
    IP_TABLE = dict()
    keyname = ""
    host_str = ""

    for server in server_info["core"]:
        SERVER_INFO["core"][server] = server_info["core"][server]["private_v4"]
        keyname = server_info["core"][server]["key_name"]
        IP_TABLE[server] = server_info["core"][server]["private_v4"]
        if "kepler" in server:
            SERVER_INFO["kepler_local_ip"] = server_info["core"][server]["private_v4"]
            SERVER_INFO["kepler_keyname"] = keyname
        if "mongo" in server:
            SERVER_INFO["mongo_local_ip"] = server_info["core"][server]["private_v4"]
            SERVER_INFO["mongo_keyname"] = keyname
    for server in server_info["models"]:
        SERVER_INFO["models"][server] = server_info["models"][server]["private_v4"]
        IP_TABLE[server] = server_info["models"][server]["private_v4"]

    # generate configurations for local use
    keypath = os.path.join(str(pathlib.Path.home()), ".ssh", keyname)
    with open(keypath, "r") as keyfile:
        PRIVATE_KEY = keyfile.read()

    # Writing all ips to a Template file
    for host in IP_TABLE:
        host_str = host_str + IP_TABLE[host] + " " + host + " \n"
    new_file = open(os.path.join(PB_DIR) + "/roles/commons/files/host_vars.txt", "w+")
    new_file.write(host_str)
    new_file.close()

    if PARALLELIZE:
        _timed_print("----- Bootstrapping Instances in Parallel  -----".format(global_start.isoformat()))
        parallel_configure_core()
        parallel_configure_model()
    else:
        configure_core()
        configure_models()

    # done!
    diff = datetime.datetime.now() - global_start
    _timed_print("----- Configuration completed successfully in {0}! -----".format(diff))
