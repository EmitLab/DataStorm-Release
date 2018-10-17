<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<%@ page import="common.JSONFiles"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>State Models</title>

<title>Server Visualization Blinking</title>
<!-- Latest compiled and minified CSS -->
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

<!-- jQuery library -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

<!-- Latest compiled JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>

<script>
//variables to hold JSON data
 var stateJSON = [];
 var keplerJSON = [];
 var indexCount = 0;
 /*
  $.getJSON(JSONFiles.JSON_STATE%>, function(json){
      stateJSON = json;
      console.log("Hardcoded cluster.json:");
      console.log(stateJSON);
      

 
  });
  /*
   $.getJSON(JSONFiles.JSON_MODEL%>, function(json){
       keplerJSON = json;

       console.log("Hardcoded kepler.json:");
       console.log(JSON.stringify(keplerJSON),null,2);
      
 });*/
   
   /*
   		retrieve model types from JSON.  Goes to setModel()
   */
   function getModelData(){
	   for(var i = 0; i < keplerJSON.length; i++){
		   if(keplerJSON[i].model_type == "hurricane"){
			   var id = "hurricaneModel";
			   setModel(keplerJSON[i],i,id);
		   }
		   if(keplerJSON[i].model_type == "flood"){
			   var id = "floodModel";
			   setModel(keplerJSON[i],i,id);
		   }
		   if(keplerJSON[i].model_type == "human_mobility"){
			   var id = "mobilityModel";
			   setModel(keplerJSON[i],i,id);
			   
			   
		   }
	   } 
   }
 /*
 	Sets the data in the model states
 	Uses HTML tables.  Rows separated by /////////
 */
   function setModel(json,index,id){
   		var node = document.createElement('div');
		node.className = 'table modelNode';
		console.log("1");
		
		   var modelName = document.createElement('h4');
		   var modelType = document.createTextNode(json.model_type);
		   modelName.appendChild(modelType);
		   node.appendChild(modelName);
		   console.log("2");
		
   	////////////////////////////
 		var dsActorRow = document.createElement("tr");
 		
   		var dsActor = document.createElement('td');
   		var dsActorParameter = document.createTextNode("ds_actor:");
   		dsActor.appendChild(dsActorParameter); 
   		var dsActorNode = document.createElement('td');
   		var dsActorValue = document.createTextNode(json.subactor_state);
   		dsActorNode.appendChild(dsActorValue);
   		dsActorRow.appendChild(dsActor);
   		dsActorRow.appendChild(dsActorNode);
   		node.appendChild(dsActorRow);
   		/////////////////////////
   		 var beginRow = document.createElement("tr");
 		
   		var beginParameter = document.createElement('td');
   		var parameterValue = document.createTextNode("begin:");
   		beginParameter.appendChild(parameterValue); 
   		
   		var beginNode = document.createElement('td');
   		var date = getTimeStamp(keplerJSON[index].temporal_context.begin);
   		var beginValue = document.createTextNode(date);
   		beginNode.appendChild(beginValue);
   		beginRow.appendChild(beginParameter);
   		beginRow.appendChild(beginNode);
   		node.appendChild(beginRow);
   		/////////////////////////
   		var endRow = document.createElement("tr");
 		
   		var endParameter = document.createElement('td');
   		var parameterValue = document.createTextNode("end:");
   		endParameter.appendChild(parameterValue); 
   		
   		var endNode = document.createElement('td');
   		//var utcSeconds = keplerJSON[index].temporal_context.end;
   		//var d = new Date(0);
   		//d.setUTCSeconds(utcSeconds);
   		var d = getTimeStamp(keplerJSON[index].temporal_context.end);
   		var endValue = document.createTextNode(d);
   		endNode.appendChild(endValue);
   		endRow.appendChild(endParameter);
   		endRow.appendChild(endNode);
   		node.appendChild(endRow);
   		
   		
   		
   	 document.getElementById(id).appendChild(node);
   }
 /*
 	Converts time stamp to readable date
 */
   function getTimeStamp(t){
	   
	   var d = new Date(t*1000);
	   var date = t + d.getTimezoneOffset() * 60;
	   var GMTvalue = new Date(date*1000);

	   return GMTvalue.toLocaleString();
   }
 /*
 	Retrieves data from JSON to set state instances.  Goes to setHurricaneState()
 */
    function getStateData(){
    	
    for(var i = 0; i < stateJSON.length; i++){
    	if(stateJSON[i].model_type == "hurricane"){
    		var id = "hurricaneData";
    		setHurricaneState(stateJSON[i].pool.running,i,id);
    		indexCount++;
    		
    	}
    	if(stateJSON[i].model_type == "flood"){
    		setFloodState(stateJSON[i].pool.running,i);
    		indexCount++;
    		
    	}
    	if(stateJSON[i].model_type == "human_mobility"){
    		setMobilityState(stateJSON[i].pool.running,i);
    		indexCount++;	
    	}
    	
    }
    }
 /*
 	Sets the data of the hurricane state instances.
 	Uses HTML tables.  Rows separated by /////////
 */
    function setHurricaneState(json,index,id){
    	
    	var node = document.createElement('button');
    	node.className = 'table table1';
    	node.id = index;

    	////////////////////////////
  		var locationRow = document.createElement("tr");
  		
    	var locationIP = document.createElement('td');
    	var locationParameter = document.createTextNode("locationIP:");
    	locationIP.appendChild(locationParameter); 
    	
    	var locationNode = document.createElement('td');
    	var location = document.createTextNode(stringValidate(stateJSON[index].ip));
    	locationNode.appendChild(location);
    	
    	locationRow.appendChild(locationIP);
    	locationRow.appendChild(locationNode);
    	node.appendChild(locationRow);
    	/////////////////////////
    	
    	var statusRow = document.createElement("tr");
    	
    	var statusParameter = document.createElement('td');
    	var statusName = document.createTextNode("status:");
    	statusParameter.appendChild(statusName);
    	
    	var statusValue = document.createElement('td');
    	var status = document.createTextNode(stringValidate(stateJSON[index].status));
    	statusValue.appendChild(status);
    	var ledStatus = document.createElement('div');
    	ledStatus.style.marginRight = "5px";
    	if(stateJSON[index].status == "idle"){
    		ledStatus.className = "led-green";
    		statusValue.appendChild(ledStatus);
    	}
    	else{
    		ledStatus.className = "led-yellow";
    		statusValue.appendChild(ledStatus);
    	}


    	statusRow.appendChild(statusParameter);
    	statusRow.appendChild(statusValue);
    	node.appendChild(statusRow);
    	/////////////////////////
    	var windRow = document.createElement("tr");
    	
    	var windParameter = document.createElement('td');
    	var windName = document.createTextNode("wind_speed:");
    	windParameter.appendChild(windName);
    	var windValue = document.createElement('td');
    	var wind = document.createTextNode(stringValidate(json[0].wind_speed));
    	windValue.appendChild(wind);
    	
    	windRow.appendChild(windParameter);
    	windRow.appendChild(windValue);
    	node.appendChild(windRow);
    	//////////////////////////
    	
    	var humidityRow = document.createElement("tr");
    	
    	var humidityParameter = document.createElement('td');
    	var humidityName = document.createTextNode("humidity:");
    	humidityParameter.appendChild(humidityName);
    	
    	var humidityValue = document.createElement('td');
    	var humidity = document.createTextNode(stringValidate(json[0].humidity));
    	humidityValue.appendChild(humidity);
    	
    	humidityRow.appendChild(humidityParameter);
    	humidityRow.appendChild(humidityValue);
    	node.appendChild(humidityRow);
    	/////////////////////////

     	document.getElementById(id).appendChild(node);

    }
 /*
 	sets the data of the flood states
 	Uses HTML tables.  Rows separated by /////////
 */
    function setFloodState(json,index){
    	
    	var node = document.createElement('button');
    	node.className = 'table table1';
    	node.id = index;

    	////////////////////////////
  		var locationRow = document.createElement("tr");
  		
    	var locationIP = document.createElement('td');
    	var locationParameter = document.createTextNode("locationIP:");
    	locationIP.appendChild(locationParameter); 
    	
    	var locationNode = document.createElement('td');
    	var location = document.createTextNode(stringValidate(stateJSON[index].ip));
    	locationNode.appendChild(location);
    	
    	locationRow.appendChild(locationIP);
    	locationRow.appendChild(locationNode);
    	node.appendChild(locationRow);
    	/////////////////////////
    	
    	var statusRow = document.createElement("tr");
    	
    	var statusParameter = document.createElement('td');
    	var statusName = document.createTextNode("status:");
    	statusParameter.appendChild(statusName);
    	var statusValue = document.createElement('td');
    	var status = document.createTextNode(stringValidate(stateJSON[index].status));
    	statusValue.appendChild(status);
    	var ledStatus = document.createElement('div');
    	ledStatus.style.marginRight = "5px";
    	if(stateJSON[index].status == "idle"){
    		ledStatus.className = "led-green";
    		statusValue.appendChild(ledStatus);
    	}
    	else{
    		ledStatus.className = "led-yellow";
    		statusValue.appendChild(ledStatus);
    	}
    	
    	statusRow.appendChild(statusParameter);
    	statusRow.appendChild(statusValue);
    	node.appendChild(statusRow);
    	/////////////////////////
    	
    	var depthRow = document.createElement("tr");
    	
    	var depthParameter = document.createElement('td');
    	var depthName = document.createTextNode("flood_depth:");
    	depthParameter.appendChild(depthName);
    	var depthValue = document.createElement('td');
    	var depth = document.createTextNode(stringValidate(stateJSON[index].pool.running.flood_depth));
    	depthValue.appendChild(depth);
    	depthRow.appendChild(depthParameter);
    	depthRow.appendChild(depthValue);
    	node.appendChild(depthRow);
    	//////////////////////////
    	
    	var humidityRow = document.createElement("tr");
    	
    	var humidityParameter = document.createElement('td');
    	var humidityName = document.createTextNode("humidity:");
    	humidityParameter.appendChild(humidityName);
    	var humidityValue = document.createElement('td');
    	var humidity = document.createTextNode(stringValidate(stateJSON[index].pool.running.humidity));
    	humidityValue.appendChild(humidity);
    	humidityRow.appendChild(humidityParameter);
    	humidityRow.appendChild(humidityValue);
    	node.appendChild(humidityRow);
    	/////////////////////////
     	document.getElementById("floodData").appendChild(node);	
    }
 /*
 	Sets the data of the mobility states.
 	Uses HTML tables.  Rows separated by /////////
 */
    function setMobilityState(json, index){
    	
    	var node = document.createElement('button');
    	node.className = 'table table1';
    	node.id = index;

    	////////////////////////////
  		var locationRow = document.createElement("tr");
  		
    	var locationIP = document.createElement('td');
    	var locationParameter = document.createTextNode("locationIP:");
    	locationIP.appendChild(locationParameter); 
    	
    	var locationNode = document.createElement('td');
    	var location = document.createTextNode(stringValidate(stateJSON[index].ip));
    	locationNode.appendChild(location);
    	
    	locationRow.appendChild(locationIP);
    	locationRow.appendChild(locationNode);
    	node.appendChild(locationRow);
    	/////////////////////////
    	
    	var statusRow = document.createElement("tr");
    	
    	var statusParameter = document.createElement('td');
    	var statusName = document.createTextNode("status:");
    	statusParameter.appendChild(statusName);
    	var statusValue = document.createElement('td');
    	var status = document.createTextNode(stringValidate(stateJSON[index].status));
    	statusValue.appendChild(status);
    	var ledStatus = document.createElement('div');
    	ledStatus.style.marginRight = "5px";
    	if(stateJSON[index].status == "idle"){
    		ledStatus.className = "led-green";
    		statusValue.appendChild(ledStatus);
    	}
    	else{
    		ledStatus.className = "led-yellow";
    		statusValue.appendChild(ledStatus);
    	}
    	
    	statusRow.appendChild(statusParameter);
    	statusRow.appendChild(statusValue);
    	node.appendChild(statusRow);
    	/////////////////////////
    	
    	var param1Row = document.createElement("tr");
    	
    	var param1Parameter = document.createElement('td');
    	var param1Name = document.createTextNode("paramenter_1:");
    	param1Parameter.appendChild(param1Name);
    	
    	var param1Value = document.createElement('td');
    	var param1 = document.createTextNode(stringValidate(json[0].parameter_1));
    	param1Value.appendChild(param1);
    	param1Row.appendChild(param1Parameter);
    	param1Row.appendChild(param1Value);
    	node.appendChild(param1Row);
    	//////////////////////////
    	
    	var param2Row = document.createElement("tr");
    	
    	var param2Parameter = document.createElement('td');
    	var param2Name = document.createTextNode("parameter_2:");
    	param2Parameter.appendChild(param2Name);
    	var param2Value = document.createElement('td');
    	var param2 = document.createTextNode(stringValidate(json[0].parameter_2));
    	param2Value.appendChild(param2);
    	param2Row.appendChild(param2Parameter);
    	param2Row.appendChild(param2Value);
    	node.appendChild(param2Row);
    	/////////////////////////
     	document.getElementById("mobilityData").appendChild(node);	
     	
    }
    /*
    	creates JSON element to be presented in the data view when clicked on a state instances
    */
    function createDataElem(json){
    	
    	$(".dataView").empty();
    	var data = document.createTextNode(JSON.stringify(json,null,2));
    	console.log(data);
    	document.getElementById("dataView").appendChild(data);

 		
 		
 		
    }
   //window onload
    $(window).bind('load', function() {
    
    	//Parse the query string for time interval ti
    	var urlParams = new URLSearchParams(window.location.search);
    	var timeInterval = urlParams.get('ti')
    	console.log(timeInterval);
    	if(timeInterval>5){ 
    		timeInterval = timeInterval * 1000;
    	}
    	else
    	{
    		timeInterval =1 * 1000;	
    	}
    	console.log("time interval (seconds)="+timeInterval/1000);
    	
  
    	ajaxCallForState();
    	
    	//TODO: For future usage
    	//setInterval(function(){
    		console.log("called...");
    		ajaxCallForState();
    	//},timeInterval);

    });
   //if undefined values are pulled from JSON, write N.A.
    function stringValidate(str){
    	
    	if(typeof str === "undefined"){
    		return "N.A.";
    	}
    	else{
    		return str;
    	}
    }
    
    //function that holds Ajax call to retrieve JSON from Mongo
    function ajaxCallForState()
    {
    	$("body").off("click","button",function(){
    	});
    	
    	
    	console.log("cleared...");
    	var data1 = {
    		    temp: "tempdata"
    		};

    	$.ajax({
    	    type: "POST",
    	    url: "Stateconn",//servlet
    	    contentType: "application/json", // NOT dataType!
    	    data: JSON.stringify(data1),
    	    success: function(response) {
    	    	console.log("response from ajax call="); 
    	    	console.log(JSON.stringify(response["kepler"],null,2)); //Access ALL JS objects from response
    	    	console.log(response);
    	    	
    	    	
    	    	//Hardcode values here 
    	    	var ip = "127.0.0.1";
    	    	response['cluster'][4]['ip'] = ip;
    	    	response['cluster'][5]['ip'] = ip;
    
    	    	response['cluster'][0]['pool']['running'] = [{"flood_depth":24.5,"humidity":0.96}];
    	    	response['cluster'][1]['pool']['running'] = [{"flood_depth":24.5,"humidity":0.96}];
    	    	
    	    	response['cluster'][2]['pool']['running'] = [{"wind_speed":24.5,"humidity":0.96}];
    	    	response['cluster'][3]['pool']['running'] = [{"wind_speed":24.5,"humidity":0.96}];
    	    	
    	    	response['cluster'][4]['pool']['running'] = [{"parameter_1":24.5,"parameter_2":0.96}];
    	    	response['cluster'][5]['pool']['running']= [{"parameter_1":24.5,"parameter_2":0.96}];
    	    	
    	    
    	    	$("#hurricaneData button").remove();
    	    	$("#hurricaneModel").html("");
    	    	$("#floodData button").remove();
    	    	$("#floodModel").html("");
    	    	$("#mobilityData button").remove();
    	    	$("#mobilityModel").html("");
    	    	
    	    	
    	    	if(response.hasOwnProperty('cluster') && response['cluster'].length>=1){
    	    	      try{
    	    	    	  keplerJSON = response['kepler'];
    	    	    	  stateJSON = response['cluster'];
    	    	      	getModelData();
    	    	          getStateData();
    	    	          //TODO: assign class name to #DDD, then assign white to $(this.attr("id")) for better performance
    	    	          
    	    	          //controls changing color when clicking a state instances.  Calls createDataElem() to display values in data view.
    	    	      	$("body").on("click","button",function(){
    	    	      		
    	    	      			for(var i = 0; i < indexCount; i++){
    	    	      				if(i == $(this).attr("id")){
    	    	      					console.log("match");
    	    	      					document.getElementById($(this).attr("id")).style.background="white";
    	    	      				}
    	    	      				else{
    	    	      					document.getElementById(i).style.background="#ddd";
    	    	      				}
    	    	      			}
    	    	      			createDataElem(stateJSON[($(this).attr("id"))]);
    	    	      			
    	    	      	});
    	    	      			
    	    	        }
    	    	         catch(err){
    	    	        $('#myModal').modal('show');
    	    	      }
    	    		
    	    		
    	    		
    	    	}
    	    	
    	    }
    	});
    	var clicked = false;
    }
   
</script>

<style>
body{
  background-color:rgba(250,250,250,0.5);
}

.view{
	display: "";
}

.modelNode{
border-style: solid;
border-width: 3px;
border-color: #555;
text-align: center;
background-color: #555;
color: #ddd;
width: 100%;
font-size: 100%;

}
h4{
text-align: center;
}
h1{
text-align: center;

}
.table1{
  height: 145px;
  width: 150px;
  background-color:#555;
  margin-left: auto%;
  border-style: solid;
  border-width: 3px;
  border-color: #555;
  text-align: left;
  font-size: 100%;
  padding: 0;
}
.table1:hover{
background-color: white;
}

#dataView{
  border-style: solid;
  border-width: 3px;
  border-color: #555;
  font-size: 130%;
  padding: 10px;
}
.led-yellow {
    float: left;
  margin-left: 0%;
  width: 12px;
  height: 12px;
  background-color: #FF0;
  border-radius: 50%;
  box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #808002 0 -1px 9px, #FF0 0 2px 12px;
  -webkit-animation: blinkYellow 1s infinite;
  -moz-animation: blinkYellow 1s infinite;
  -ms-animation: blinkYellow 1s infinite;
  -o-animation: blinkYellow 1s infinite;
  animation: blinkYellow 1s infinite;
}

@-webkit-keyframes blinkYellow {
    from { background-color: #FF0; }
    50% { background-color: #AA0; box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #808002 0 -1px 9px, #FF0 0 2px 0; }
    to { background-color: #FF0; }
}
@-moz-keyframes blinkYellow {
    from { background-color: #FF0; }
    50% { background-color: #AA0; box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #808002 0 -1px 9px, #FF0 0 2px 0; }
    to { background-color: #FF0; }
}
@-ms-keyframes blinkYellow {
    from { background-color: #FF0; }
    50% { background-color: #AA0; box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #808002 0 -1px 9px, #FF0 0 2px 0; }
    to { background-color: #FF0; }
}
@-o-keyframes blinkYellow {
    from { background-color: #FF0; }
    50% { background-color: #AA0; box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #808002 0 -1px 9px, #FF0 0 2px 0; }
    to { background-color: #FF0; }
}
@keyframes blinkYellow {
    from { background-color: #FF0; }
    50% { background-color: #AA0; box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #808002 0 -1px 9px, #FF0 0 2px 0; }
    to { background-color: #FF0; }
}
.led-green {
  float: left;
  margin-left: 1%;
  width: 12px;
  height: 12px;
  background-color: #ABFF00;
  border-radius: 50%;
  box-shadow: rgba(0, 0, 0, 0.2) 0 -1px 7px 1px, inset #304701 0 -1px 9px, #89FF00 0 2px 12px;
}

</style>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css">
	<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.2.0/css/all.css">
	<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Gugi">
	<link rel="stylesheet" href="css/main.css">
</head>
<body>
	<nav id="nav" class="navbar navbar-expand-lg navbar-light bg-light">
	    <div class="project-name">
			<span class="fab fa-superpowers"></span>&nbsp;DataStorm&nbsp;Visualization
		</div>
	    <div class="collapse navbar-collapse" id="navbarSupportedContent">
	        <ul class="navbar-nav mr-auto">
	            <li class="nav-item">
	                <a class="nav-link" href="./">
	                <span class="fas fa-map-marked-alt fa-fw"></span>&nbsp;
	                Map View </a>
	            </li>
	            <li class="nav-item active">
	                <a class="nav-link" href="./state.jsp" target="_blank">
	            	<span class="fas fa-sync fa-fw"></span>&nbsp;
	               	Model State </a>
	            </li>
	            <li class="nav-item">
	                <a class="nav-link" href="./provenance.jsp"  target="_blank">
	                <span class="fas fa-sitemap fa-fw"></span>&nbsp;
	                Provenance </a>
	            </li>
	            <li class="nav-item">
	                <a class="nav-link" href="./about.jsp">
	                <span class="fas fa-ellipsis-h fa-fw"></span>&nbsp;
	                About </a>
	            </li>
	        </ul>
	    </div>
	</nav>
<div class="container">

  <div class="row">
    <div class="col-md-8" id="modelStateActivity">
    <h1>Model State Activity</h1>
    <br>
        <div class ="col-md-4" id="hurricaneData">
        <div id = "hurricaneModel"></div>
        <br>
        <h5>Model Instances</h5>
        </div>
          
        <div class = "col-md-4" id="floodData"> 
        <div id="floodModel"></div>
        <br>
        <h5>Model Instances</h5>

        </div>
        <div class = "col-md-4" id="mobilityData">
        <div id="mobilityModel"></div>
        <br>
        <h5>Model Instances</h5>

        
        </div>

    </div>
    <div class="col-md-4">
      <h4> Data File View </h4>
      <textarea id="dataView" class="dataView" rows="20" cols="40">

      </textarea>
    </div>
</div>
</div>

<script>

</script>
<style>

.table1{
  height: 145px;
  width: 100%;
	padding: 0;
  background-color:#ddd;
}

.modelNode{
border-style: solid;
border-width: 3px;
border-color: #555;
text-align: center;
background-color: #555;
color: #ddd;
width: 100%;
font-size: 85%;
padding: 3px;
overflow-x: auto;
}
.modelNode td{
border-color: #555;
}
.table1 td{
border-color: #ddd;
}
.table1:hover td{
border-color: white;
}
.table1:hover{
background-color: white;
}

#nav {
	font-size: 150%;
}
</style>
</body>
</html>