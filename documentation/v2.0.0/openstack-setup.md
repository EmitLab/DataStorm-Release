Configuring OpenStack
=====
This guide assumes that users have already deployed and configured an OpenStack cluster, have access to its associated dashboard, and sufficient privileges to create instances and assign external IP addresses.



Building DataStorm Structure
===

In order to run DataStorm, you will first need to perform a one-time setup process in order to establish several systems that will be used to execute the system.

These servers will serve as data repositories, cluster orchestrators, simulators, and more. 

Future goals include the automated deployment of a DataStorm cluster through the use of a project configuration file.

Setting Up the ds_worker Key Pair
==
It is crucial that each instance in your cluster is able to communicate with the other machines. More importantly, this communication channel should be (1) easy to use, and (2) secure.

This is accomplished through the deployment of a shared SSH keypair to the machines in the cluster. If you are unfamiliar with how to set up a key pair, you can learn more here:

https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-on-ubuntu-1804

This process can be handled manually by you, or the keys can be loaded into the project for automatic deployment by the system, depending on your preference.


Instantiating Core Servers
==
DataStorm relies on several "core" servers, and a variable number of "instance" servers that are used to execute the desired simulations. Core servers are the following:

* Kepler server
* MongoDB server
* Front end

Server instantiation can be handled through the OpenStack dashboard. Instance sizes are flexible, and will vary depending on the expected load on the server. Additionally, it is important to ensure that (at minimum) the front end server is assigned an external IP address, in order for users to be able to access the server remotely.

To set up a MongoDB instance, you can follow this guide:

https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04

It is important to note that all communication between servers will use port 22 (SSH); this may require changes to the firewall, if you choose to use one. Additionally, the SSH tunneling libraries that provide secure Mongo linkages do not work well with authenticated MongoDB servers. To work around this issue, simply restrict access to localhost, and allow the SSH tunnel to serve as the authentication instead.

For detailed information on the setup and configuration of the Kepler and front end servers, please refer to their respective setup guides.

Instantiating Simulation Servers
==
Once you have decided which simulators to use, their prerequisites, and the number of instances of each that you wish to use, you will also need to instantiate those as well. Instance size will vary based on the requirements of the individual simulators. It is also highly suggested that the deployment process of each individual simulator be carefully documented, or preferably automated using tools such as Ansible, Salt, or Puppet.

These servers also need to be initialized with the shared keypair, in order to allow cluster orchestration by the Kepler-based coordinator. However, the individual simulators do not need to understand anything about the structure of the DataStorm cluster.

Rather, the primary method of integration for individual simulator instances is through the use of the JobGateway API. Information on the installation and use of this API layer can be found in the JobGateway documentation.
