Using JobGateway
======

The JobGateway is the primary API that models use to interact with the DataStorm system. It provides functionality for interfacing with the pending job queue, managing the provenance of results, and abstracts database access into a simple file-based approach.

Although the JobGateway is fundamentally a Python-based application, it is completely self-contained, and does not use the system-level Python installation, nor does it require the installation of any additional libraries or modules.

Since it is designed to be used by each constituent model, it is important that it is configured on a model-specific basis *on each instance running a model*. Since this may be a variable number of instances, it may be beneficial to include it in any deployment management system to be used.

This configuration process consists of the modification of two JSON files, and should not be a difficult process to automate.

Configuration Files
===

Before using the JobGateway, it is important to configure it to work with the model running on the local instance. This is accomplished through the modification of two JSON configuration files, *mongo.json* and *instance.json*.

The former is used to connect to the MongoDB server, and will be shared by all instances within the same cluster. This simplifies the deployment significantly. Specifically, it contains the following key-value pairs:

* mongo_ip: The IP address of the MongoDB server
* ssh_port: The port number through which the SSH tunnel should connect
* ssh_key: The local path of the SSK private key that will be used to authenticate the connection
* ssh_username: The username of the SSH user that the connection should use

The *instance.json* file, in contrast, must be configured on a per-instance basis to ensure that proper consumption of queued jobs takes place. However, it still contains only limited information:

* model_type: The type of model instantiated and running on this instance
* instance_id: A unique integer identifier corresponding to the instance's location in the job queue

API Calls
===

There are only two possible calls for the JobGateway API; they are designed to be easy-to-use and hard to mess up. The trickiest part is making sure to use the correct virtual environment (located at job_gateway/venv/bin/python3).

fetch_job : python3 JobGateway.py fetch_job
---
This API fetches the next available job that's ready for execution, and also downloads all the data necessary for use by that job. This means that after this is called, all remaining data analysis, input, and transformation can take place on the local instance machine.

This produces the following local file structure:

<pre>
job_gateway
	input_data
		[upstream model_type 1]
			dsar.json
			dsir.json
			dsfr.json
		[upstream model_type n]
			...
</pre>			

finish_job : python3 JobGateway.py finish_job
---
This API takes correctly-formatted results and injects them into the database, as well as amanging all the provenance recording and connectivity with the rest of the system.

It expects input to be located at:
<pre>
job_gateway
	output_data
		data.json
</pre>
		
This is simply a JSON file containing a collection of objects with the following structure:

* timestamp: time of the observation, in seconds
* coordinate: 2-item array of [longitude, latitude] of the observation location
* observation: an n-length vector of observed values generated by the model at the time/space intersection above


Calling APIs in Python code
==
This can be somewhat tricky, due to incompatibilities when mixing Python virtual machines. The easiest solution is to execute it externally as a separate process as follows:

<pre>
    try:
        subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as cpe:
        log("JobGateway returned exit code 1 on 'finish_job'")
        with open("~/error_log.txt", "w") as errorlog:
            errorlog.write(json.dumps(str(cpe)))
        return
</pre>

This provides a robust and debuggable interface for Python calls. Of course, since it can be executed simply from the shell, other approaches are also possible. This is only one possible approach.

Logging
===

Fortunately, the JobGateway is quite robust; if you make a mistake in configuration, any of the keys are misconfigured, or the models themselves encounter some problem during API execution, the issues will be clearly and explicitly recorded in a local log file so that they can be corrected.

This log file is the *gateway_log.txt*, located immediately next to the JobGateway.py file itself. This can be an invaluable resource for debugging issues with the model's use of the APIs, or with the APIs themselves. Any request for support with the JobGateway should also include this file to assist with the support.

Note that this file only records the most recent execution; this is an intentional behavior designed to prevent the accumulation of excessively large log files. However, in some cases, this may mask underlying problems. Please consider this fact during your troubleshooting process.