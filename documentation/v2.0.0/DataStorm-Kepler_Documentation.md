# DataStorm - Kepler Platform Documentation
In this document, we describe how to setup Kepler Workflow engine in a Linux environment (Ubuntu), and the related information for DataStorm Project.

## Requirements
* Ubuntu 18.04.1 <https://www.ubuntu.com/>
* Java 7 or later <http://www.oracle.com/technetwork/java/index.html>
* Kepler 2.5 <https://kepler-project.org/>


## Environment Setting
### Operating System: Ubuntu 18.04.01
### Java installation
1. `sudo apt install default-jre`
2. `sudo apt install default-jdk`
### Ubuntu Desktop installation (Gnome)
1. `sudo apt-get install ubuntu-desktop gnome-panel gnome-settings-daemon metacity nautilus gnome-terminal`
### VNC server installation and configuration
1. `sudo apt-get install vnc4server`
2. `vncserver :1` (you will be requestd to setup the password for using vnc remote control)
3. `vncserver -kill :1`
4. `vim ~/.vnc/xstartup` and add following lines at the end of file
    
    4.1 `gnome-panel & gnome-settings-daemon & metacity & nautilus &`, and then store file.
   
5. Connect VNC server with `server_ip_address:1` 
## The Basics for Kepler
### Official Documentations
1. [Kepler 2.5 Getting Started Guide](https://code.kepler-project.org/code/kepler-docs/trunk/outreach/documentation/shipping/2.5/getting-started-guide.pdf)
2. [Kepler 2.5 User Manual](https://code.kepler-project.org/code/kepler-docs/trunk/outreach/documentation/shipping/2.5/UserManual.pdf)
3. [Kepler 2.0 Actor Reference](https://code.kepler-project.org/code/kepler-docs/trunk/outreach/documentation/shipping/2.0/ActorReference.pdf)


### Installation <https://kepler-project.org/users/downloads>
1. Download "Kepler-2.5-linux.tar.gz" for Kepler Project website.
2. Untar "Kepler-2.5-linux.tar.gz" wherever you like and start Kepler.
3. After step 2., there are two folders **"Kepler-2.5"** and **"KeplerData"** will be created.

### Start Kepler
1. Change directory to "Kepler-2.5"
2. ./kepler.sh


## Kepler Provenance Management
### Official Documentations
1. [Getting Started with Kepler Provenance 2.5](https://code.kepler-project.org/code/kepler/trunk/modules/provenance/docs/provenance.pdf)
2. [The relationships within provenance schema](https://github.com/EmitLab/DataStorm/blob/master/model_details/Kepler/Kepler_Provenance_management/Kepler_Provenance_Schema.pdf) (Can also be found in the directory "KeplerData/kepler.modules/provenance-2.5.0/docs/")

### Provenance Database Configuration
* **Using MySQL to store Kepler Provenance Information**

1. Install MySQL. <https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04>

2. Change the value of `sql_mode` variable in MySQL

	a. Editing 
	
	`"/etc/mysql/mysql.conf.d/mysqld.cnf"`
	
	b. Below "[mysql]', add the following line:
	
	 `sql_mode = "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION"`
	 
	c. Restart mysql service: 
	
	`sudo service mysql restart`
	
3. Change Kepler default setting for provenance management

	The configuration file for provenance management should be located in:

	`$HOME/KeplerData/modules/provenance/configuration/configuration.xml`. If this file does not exist, you can edit the provenance configuration file in the Kepler installation directory: $HOME/KeplerData/kepler.modules/provenance-2.5.0/resources/configurations configuration.xml)
	
	a. Editing configuration.xml, set following parameters according to your mysql server setting:
	
	* `DB Host`: "YOUR DB Location (default: localhost)"
	* `DB Type`: "MySQL"
	* `DB User Name`: "YOUR MYSQL USER"
	* `DB Port`: "YOUR MYSQL_PORT (default: 3306)"
	* `Password`: "YOUR MYSQL PASSWORD"

	b. Once you finish above modification, when you drag a “provenance recorder” into your workflow and double click on “provenance recorder”, you should see your MySQL configuration in it.
	
	c. To check provenance information, you can use **phpMyAdmin** or other MySQL GUI tool to check.
		
	* [Install phpMyAdmin in Ubuntu 16.04 (Step 1 is enough for developing)](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-phpmyadmin-on-ubuntu-16-04) 
		

## MySQL operations in Kepler

### Fetch Data from MuSQL Database

* Required Director:

	* SDF Director

* Required Actors:
	
	1. Open Database Connection
	2. Database Query
	3. Close Database Connection

* Required Configurations

	* Setup MySQL server
		
		* Default port: 3306
		* Username
		* Password

	* Setup parameter for **Open Database Connection Actor**
		* database format 
			* Scroll down menu and select MySQL

		* database URL
			* jdbc:mysql://localhost:3306/databaseName

		* Username / Password
			* Same as the setting in MySQL server
	
	* Query Setting

		* Use a “String Parameter” actor in Kepler and set query string (w/o double quote) to parameter’s value, and rename this parameter for differentiation
			* E.g. Given a string parameter, its name is “queryAll”, and it’s value is ” SELECT * from tablename”

		* Use a “Expression” actor in Kepler and set its value to the name of query in last previous step.

	* Connection within actors
		* The output port “dbcon” of “Open Database Connection” actor should be connected to the input port “dbcon” of “Database Query” actor.
		* The output port “output” of “Expression” which indicate our query should be connected to the input port “query” of “Database Query” actor.
		* The output port “result” of  “Database Query” could be connected to next actors as inputs.
	 	
### Insert/Update Data to MySQL

* Required Director:

	* SDF Director

* Required Actors:
	
	1. Open Database Connection
	2. Database Writer
	3. Close Database Connection

* Required Configurations
	* Samm as previous section

* Query setting

	* Use a “String Parameter” actor in Kepler and set query string (w/o double quote) to parameter’s value, and rename this parameter for differentiation.
		* E.g. Given a string parameter, its name is “queryInsert”, and it’s value is ” INSERT INTO tablename (column1’s name, ...) VALUES (value to column1 , ...)”

	* Use a “Expression” actor in Kepler and set its value to the name of query in last previous step.

	* Set up parameters for “Database Writer” actor
		* table: the table name to be updated/inserted
		* autoColumnName: the column Name that having auto-increment.

* Connection within actors
	* The output port “dbcon” of “Open Database Connection” actor should be connected to the input port “dbcon” of “Database Writer” actor.
	* The output port “output” of “Expression” which indicate our query should be connected to the input port “query” of “Database Writer” actor.
	* The output port “result” of  “Database Writer” show how many rows were successfully updated.



### Access Remote MySQL Database

Assume we have two machine, one of them has MySQL server (machine A), and the other one (machine B) want to access the data in machine A.

**Machine A side:**
Here we need to create a new user who has the grant to access MySQL database in machine A, (we don’t use ‘root’ here due to security issue). The following procedure demonstrates how to achieve it.

`mysql> CREATE USER 'monty'@'localhost' IDENTIFIED BY 'some_pass';`

`mysql> GRANT ALL PRIVILEGES ON *.* TO 'monty'@'localhost' 
-> WITH GRANT OPTION; mysql> CREATE USER 'monty'@'%' IDENTIFIED BY 'some_pass';`

`mysql> GRANT ALL PRIVILEGES ON *.* TO 'monty'@'%' -> WITH GRANT OPTION;`

**Machine A side:** Refer "Fetch Data from Database" section.

### Potential Issues

1. MySQL connector in Java

Current built-in mysql connector for java in kepler 2.5 works fine, if there is any db connection problem (e.g. mysql driver not found), try to download the latest mysql-connector for java , and put extracted jar file to /Kepler-2.5/core-2.5.0/lib/jar/dbdrivers

* Mysql connector link:  <https://dev.mysql.com/doc/connector-j/5.1/en/connector-j-installing.html>


### References

1. How to setup LAMP (Linux+Apache+MySQL+PHP) on Ubuntu 16.04
<https://www.linode.com/docs/web-servers/lamp/install-lamp-stack-on-ubuntu-16-04>

2. Kepler User Manual - Section 6.7 Using Data Stored in Relational Database
<https://code.kepler-project.org/code/kepler-docs/trunk/outreach/documentation/shipping/2.5/UserManual.pdf>

3. <https://stackoverflow.com/questions/1559955/host-xxx-xx-xxx-xxx-is-not-allowed-to-connect-to-this-mysql-server>

4. <https://www.infrasightlabs.com/mysql-error-host-is-not-allowed-to-connect-to-this-mysql-server>

5. How to install Java with 'apt' on Ubuntu 18.04 <https://www.digitalocean.com/community/tutorials/how-to-install-java-with-apt-on-ubuntu-18-04>

6. How to install A Desktop and VNC on Ubuntu 16.04 <https://cloudcone.com/docs/article/install-desktop-vnc-ubuntu-16-04/> 

### Editing History

[Last edit: 2019/1/4 by Mao-Lin Li (maolinli@asu.edu)]

 
