This document will explain the requirements and setup process for the visualization project. 

### DataStorm Visualization 
* Map visualization 
  * Visualization plots layers on top of the Google Maps API. 
  * Example- 
   * heatmap based visualization type is used for showing flood regions. 
   * squaremap based visualization type is used for showing rain.
  * Changing the visualization type in visualization.js for specific model will display the details in required format. 
  * Example- heatmap can be changed to squaremap. Also the colors can also be changed to show different layers using same visualization type.

* Map visualization - Data Access 
  * The flow of mongo collections accessed to get the data-
   * Jobs -> DSAR -> DSIR -> DSFR
  * DSFR contains model_type, Time stamp, parent id
  * observation key is used for displaying the actual data
  * DSAR, DSIR contains Job ID
  * For Updating visualization from server side: 
   * Web sockets are used to provide the updates to the visualization. 
   * The socket server on kepler opens a socket and keeps listening on the port. Visualization component establishes a connection using server ip and port. 
   * After sucessful socket binding, data sent from the socket is automatically visualized at the visualization component. 
   * To update data to be sent, make changes in the visualization_config.json
  
* Provenance 
  * D3 collapsible tree is used to display the provenance hierarchy. As we go deep inside hierarchy, more information is displayed.
  * At the top layer - each model type has a separate node that contains configuration nodes
  * At configuration level - Each configuration displays relevance and contribution information and contains parameter node
  * At parameter level - All the parameters related to configuration along with values are displayed for details.
  * Provenance details are displayed in text format and can be downloaded
    
* Provenance - Data Access
  * The flow of mongo collections accessed to get the data- DSFR -> DSIR -> DSAR, Jobs
  * upstream jobs and downstream jobs in all the collections are used
  * variables, weights are identified for each model and each job 
  * Tree structure is constructed for selected model type travesing using above flow chart
  
* State of Models
  * Displays the current state of each instance along with details
  * Indicators (bulb lights) such as Green, yellow are used for showing the idle and running state
  * Collections used: Kepler, Cluster to access these information
  * The cluster information is used for accessing parameters related to instances.
  * Instance information is grouped according to model type.

### Requirements
* Java 7 or later <http://www.oracle.com/technetwork/java/index.html>
* Eclipse Neon <https://www.eclipse.org/neon/>
* Apache Tomcat 8.5 or later <https://tomcat.apache.org/download-80.cgi> 
* Google Maps API key <https://developers.google.com/maps/documentation/javascript/get-api-key>

### Steps to setup project and create WAR file:


1. Clone the DataStorm repository. Visualization code is located in DataStormViz directory.
2. Import project in Eclipse (Neon version or greater)
3. Make following changes:


* Change Google Maps API Key-
  * Location: DataStorm/DataStormViz/DVProj/WebContent/index.jsp
  * Update: https://maps.googleapis.com/maps/api/js?key=<YOUR_GOOGLE_MAPS_KEY>
  * Refer following link for generating your google maps key- https://developers.google.com/maps/documentation/javascript/get-api-key

* Change the mongo connection parameters
  * Location: DataStorm/DataStormViz/DVProj/src/com/conn/
  * Mongoconn.java, ProvenanceConn.java, Stateconn.java
  * Update: 
   * String REMOTE_HOST = "<YOUR_MONGODB_IP_ADDRESS>";
   * String SSH_HOST = "<YOUR_MONGODB_IP_ADDRESS>";

* Add the private key for mongo server access
  * Location: /DVProj/WebContent/WEB-INF/
  * Add your private key dsworker_rsa for mongodb server to this folder
  
4. To create WAR file: 

* Right Click on ‘Project Name’ in ‘Project Explorer’
* Go to ‘Export’ -> ‘WAR file’
 
* Choose the WAR file name and select the options
* Click on Finish to generate the WAR file

* Deploy WAR on apache tomcat server (version >=8.5). Use following link to download the tomcat: https://tomcat.apache.org/download-80.cgi

* Access the URL for visualization: http://<TOMCAT_SERVER_IP>:8080/<WAR_FILE_NAME>
* Access the URL for updates: http://<TOMCAT_SERVER_IP>:8080/<WAR_FILE_NAME>?ip=<KEPLER_SERVER_IP>&port=<SOCKET_PORT_NUM>

* Access following link for detailed instructions- <https://docs.google.com/document/d/1GAP78Hqe-pc9PvBjLXE6WToddiq72QHnTg9ldbej7L4/edit?usp=sharing>




 
 
  
 
 







