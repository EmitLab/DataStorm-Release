import openstack  # openstacksdk
import yaml  # PyYAML
import datetime
import threading
import copy
import concurrent.futures

OSC = None
DS_CONFIG = None
OSC_SHARED = None
SERVER_INFO = None
PARALLISE = 1


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


def _simple_create(name, flavor=None, image=None):
    # avoids 'NoneType is not subscriptable' issue
    if image is None:
        image = OSC_SHARED["image"]
    if flavor is None:
        flavor = OSC_SHARED["flavor"]

    _timed_print("\tInstantiating [{0}]...".format(name))
    old_info = OSC.get_server(name_or_id=name)
    if old_info is None:
        result = OSC.create_server(
            name=name,
            image=image,
            flavor=flavor,
            wait=True,
            auto_ip=False,
            key_name=OSC_SHARED["keypair"],
            timeout=600
        )
        _timed_print("\tdone!", showtime=False)

        return result
    else:
        _timed_print("\talready exists, skipped.")

        return old_info


def _parallel_simple_create(details):
    configs, name, flavor, image, type_info = details[0], details[1], details[2], details[3], details[4]

    print(str(threading.current_thread()) + " for server " + str(name))
    current_connection_object, current_connection_details = get_openstack_connections(configs)
    _timed_print("opening OpenStack connection ......")
    result = current_connection_object.create_server(
        name=name,
        image=image,
        flavor=flavor,
        wait=True,
        auto_ip=False,
        key_name=current_connection_details["keypair"],
        timeout=500
    )
    _timed_print("\n\tInstantiating [{0}]...Completed".format(name))
    return {"server_info": result, "type": type_info}


def read_configuration():
    global DS_CONFIG

    if DS_CONFIG is not None:
        pass

    with open("bootstrap.yaml") as infile:
        DS_CONFIG = yaml.load(infile)


def connect_to_openstack():
    global OSC, OSC_SHARED, SERVER_INFO

    _timed_print("Establishing primary connection to OpenStack cluster...")

    if OSC is not None:
        pass

    # generate cloud configuration
    auth_dict = dict()
    auth_dict["auth_url"] = DS_CONFIG["openstack"]["auth_url"]
    auth_dict["username"] = DS_CONFIG["openstack"]["base_user"]
    auth_dict["password"] = DS_CONFIG["openstack"]["base_password"]
    auth_dict["project_id"] = DS_CONFIG["openstack"]["project_name"]

    # openstack.enable_logging(debug=True)
    OSC = openstack.connection.Connection(auth=auth_dict)

    OSC_SHARED = dict()
    OSC_SHARED["keypair"] = OSC.get_keypair(name_or_id=DS_CONFIG["openstack"]["key_name"])["name"]
    OSC_SHARED["user"] = DS_CONFIG["openstack"]["base_user"]
    OSC_SHARED["image"] = OSC.get_image(name_or_id=DS_CONFIG["openstack"]["base_image"])["name"]
    OSC_SHARED["flavor"] = OSC.get_flavor_by_ram(4096)["name"]

    SERVER_INFO = dict()  # prepare a variable to receive bootstrapping results
    SERVER_INFO["core"] = dict()
    SERVER_INFO["models"] = dict()

    _timed_print("OpenStack connection successfully established.")


def get_openstack_connections(configs):
    auth_dict = dict()
    auth_dict["auth_url"] = configs["openstack"]["auth_url"]
    auth_dict["username"] = configs["openstack"]["base_user"]
    auth_dict["password"] = configs["openstack"]["base_password"]
    auth_dict["project_id"] = configs["openstack"]["project_name"]

    # openstack.enable_logging(debug=True)

    current_connection_object = openstack.connection.Connection(auth=auth_dict)

    conn_details = dict()
    conn_details["keypair"] = current_connection_object.get_keypair(name_or_id=configs["openstack"]["key_name"])["name"]
    conn_details["user"] = configs["openstack"]["base_user"]
    conn_details["image"] = current_connection_object.get_image(name_or_id=configs["openstack"]["base_image"])["name"]
    conn_details["flavor"] = current_connection_object.get_flavor_by_ram(4096)["name"]

    return current_connection_object, conn_details


def bootstrap_core():
    global SERVER_INFO

    _timed_print("Beginning Datastorm core server bootstrapping.")

    # core servers have the following requirements:
    # kepler: 8GB RAM
    # visualization: 4GB RAM
    # mongo: 4GB RAM

    # do mongo bootstrap
    # _timed_print("Bootstrapping Mongo core...")
    SERVER_INFO["core"]["ds_core_mongo"] = _simple_create(name="ds_core_mongo")

    # do viz bootstrap
    # _timed_print("Bootstrapping Visualization core...")
    SERVER_INFO["core"]["ds_core_visualization"] = _simple_create(name="ds_core_visualization")

    # do kepler bootstrap
    # _timed_print("Bootstrapping Kepler core...")
    SERVER_INFO["core"]["ds_core_kepler"] = _simple_create(name="ds_core_kepler")
    # ,flavor=OSC.get_flavor_by_ram(8192)["name"])

    _timed_print("Core bootstrapping complete.")


def bootstrap_models():
    global SERVER_INFO

    _timed_print("Beginning Datastorm model server bootstrapping.")

    if "models" not in SERVER_INFO:
        SERVER_INFO["models"] = dict()

    for model_name in DS_CONFIG["datastorm"]["initial_models"]:
        for instance_number in range(int(DS_CONFIG["datastorm"]["initial_models"][model_name]["count"])):
            name = "ds_model_" + model_name + "_" + str(instance_number)

            if "image" in DS_CONFIG["datastorm"]["initial_models"][model_name]:
                image = DS_CONFIG["datastorm"]["initial_models"][model_name]["image"]
            else:
                image = OSC_SHARED["image"]

            if "flavor" in DS_CONFIG["datastorm"]["initial_models"][model_name]:
                flavor = DS_CONFIG["datastorm"]["initial_models"][model_name]["flavor"]
            else:
                flavor = OSC_SHARED["flavor"]

            SERVER_INFO["models"][name] = _simple_create(name=name,
                                                         flavor=flavor,
                                                         image=image)

    _timed_print("Model bootstrapping complete.")


def parallel_bootstrap_core_model():
    global SERVER_INFO, DS_CONFIG, OSC_SHARED, OSC
    configs = copy.deepcopy(DS_CONFIG)

    future_details = []
    core_servers = ["ds_core_mongo", "ds_core_visualization", "ds_core_kepler"]

    _timed_print("...Generating tasks for Core Instance Creation...")
    for name in core_servers:

        flavor, image = None, None
        if image is None:
            image = OSC_SHARED["image"]
        if flavor is None:
            flavor = OSC_SHARED["flavor"]

        old_info = OSC.get_server(name_or_id=name)

        if old_info is None:
            _timed_print("\tInstantiating [{0}]...".format(name))
            future_details.append((configs, name, flavor, image, "core"))
        else:
            SERVER_INFO["core"][name] = OSC.get_server(name_or_id=name)
            _timed_print("\t" + name + " already exists, skipped.")

    if "models" not in SERVER_INFO:
        SERVER_INFO["models"] = dict()

    # Generating tasks for Model Instance Creation
    _timed_print("...Generating tasks for Model Instance Creation...")
    for model_name in DS_CONFIG["datastorm"]["initial_models"]:
        for instance_number in range(int(DS_CONFIG["datastorm"]["initial_models"][model_name]["count"])):
            name = "ds_model_" + model_name + "_" + str(instance_number)

            if "image" in DS_CONFIG["datastorm"]["initial_models"][model_name]:
                image = DS_CONFIG["datastorm"]["initial_models"][model_name]["image"]
            else:
                image = OSC_SHARED["image"]

            if "flavor" in DS_CONFIG["datastorm"]["initial_models"][model_name]:
                flavor = DS_CONFIG["datastorm"]["initial_models"][model_name]["flavor"]
            else:
                flavor = OSC_SHARED["flavor"]

            old_info = OSC.get_server(name_or_id=name)

            if old_info is None:
                _timed_print("\tInstantiating [{0}]...".format(name))
                future_details.append((configs, name, flavor, image, "models"))
            else:
                SERVER_INFO["models"][name] = OSC.get_server(name_or_id=name)
                _timed_print("\t" + name + " already exists, skipped.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_compilation = {executor.submit(_parallel_simple_create, details): details for details in future_details}
        for future in concurrent.futures.as_completed(future_compilation):
            results_holder = future_compilation[future]
            try:
                data = future.result()
                server_type = data["type"]
                server_name = data["server_info"]["name"]
                SERVER_INFO[server_type][server_name] = data["server_info"]
            except Exception as exc:
                _timed_print("Load Failed")
                _timed_print(' %r generated an exception: %s' % (results_holder, exc))
            else:
                _timed_print("Successfully Loaded " + str(server_name))

    _timed_print("Instance bootstrapping complete.")


def bootstrap_all():
    global_start = datetime.datetime.now()
    print("")
    _timed_print("----- Bootstrapping DataStorm -----".format(global_start.isoformat()))

    read_configuration()
    connect_to_openstack()

    if PARALLISE == 0:
        bootstrap_core()
        bootstrap_models()

    if PARALLISE == 1:
        _timed_print("----- Bootstrapping Instances in Parallel  -----".format(global_start.isoformat()))
        parallel_bootstrap_core_model()

    diff = datetime.datetime.now() - global_start
    _timed_print("----- Bootstrap completed successfully in {0}! -----".format(diff))
    return SERVER_INFO

