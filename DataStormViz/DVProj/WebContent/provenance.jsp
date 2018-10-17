<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<%@ page import="common.JSONFiles"%>
<!DOCTYPE html>
<html>
<head>
	<title>Provenance</title>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
	<script src="https://d3js.org/d3.v4.min.js"></script>
	<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">	
	<!--  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css"> -->
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
	            <li class="nav-item">
	                <a class="nav-link" href="./state.jsp" target="_blank">
	            	<span class="fas fa-sync fa-fw"></span>&nbsp;
	               	Model State </a>
	            </li>
	            <li class="nav-item active">
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
	
	<div class="container-fluid">
  <div class="row">
      <div class="col-sm">
        <div id="part1"></div> 

      </div>
      <div class="col-sm">
      <div class="row">
      	<div class="col-sm-8">
        	<h5>Provenance Details</h5>
        </div>
        <div class="col-sm-4">
        	<button type="button" class="btn btn-primary btn-sm" id="btn_download" style="float: right;"><i class="fas fa-download fa-fw"></i> Provenance</button>
        	<!-- <button type="button" class="btn btn-primary btn-sm" id="btn_download_data" style="float: right;">Download Data</button> -->
        </div>
       </div>
        <div>
        <textarea class="form-control" rows="40" id="part2">
		</textarea>
        </div> 
      </div>

    </div>


</div>

<script>

//Download button functionality
$("#btn_download").on("click", function() {
	var content = $("#part2").val();
    // a [save as] dialog will be shown
    window.open("data:application/txt," + encodeURIComponent(content), "_self");
});

//START: Parse the query string for dsfr id => timestamp, machineIdentifier, processIdentifier, counter
var mongoid = 0;
var urlParams = new URLSearchParams(window.location.search);
var ts = urlParams.get('timestamp')
var mi = urlParams.get('machineIdentifier')
var pi = urlParams.get('processIdentifier')
var cn = urlParams.get('counter')

//var idToParse1 = {timestamp: 1534713908, machineIdentifier: 4684564, processIdentifier: 16317, counter: 13089199};
var idToParse1 = {timestamp: Number(ts), machineIdentifier: Number(mi), processIdentifier: Number(pi), counter: Number(cn)};
console.log(idToParse1);
function hex(length, n) {
	 n = n.toString(16);
	 return (n.length===length)? n : "00000000".substring(n.length, length) + n;
}
function jsonToMongoId(idToParse){
	var idString = hex(8,idToParse.timestamp)+hex(6,idToParse.machineIdentifier)+hex(4,idToParse.processIdentifier)+hex(6,idToParse.counter);
	return idString
}

mongoid = jsonToMongoId(idToParse1);
console.log("Mongo ID: "+mongoid);
//END: Parse the query string

//Parse the query string for dsfr id 
//var urlParams = new URLSearchParams(window.location.search);
//var mongoid = urlParams.get('id')
//console.log(mongoid);

//Call mongo servlet for building the hierarchy
//START: For provenance data using mongo servlet connection 
var data = {
    mongoid: mongoid
};

$.ajax({
    type: "POST",
    url: "ProvenanceConn",
    contentType: "application/json", // NOT dataType!
    data: JSON.stringify(data),
    success: function(response) {
    	console.log("response from ajax call="); 
    	console.log(response); //Access ALL JS objects from response
    	if(response.hasOwnProperty('dsir') && response['dsir'].length>=1){
    		console.log("Adding data retrieved to textarea");
    		
    		//Using the documents from mongo, construct_history_json() constructs 
    		//the history_json required by d3 collapsible indent tree
    		provenance_json = construct_history_json(response);
    		console.log(provenance_json);
    		

			//invoke this to draw provenance vis
    		d3_collapsible_indent_tree(provenance_json);
    		
    		//Print data on text area
    		var jsonPrettyPrint = JSON.stringify(response, null, 2);
    		$("#part2").val(jsonPrettyPrint);
    	}
    	
    }
});
//END: For provenance data using mongo servlet connection 


//Function that draws the provenance using D3 js library
function d3_collapsible_indent_tree(js_obj){
//$.getJSON(JSONFiles.JSON_HISTORY%>, function(js_obj){	
	//var prov_json = '{"name":"Provenance","children":[{"name":"flood","children":[{"name":"Config 1 weight 0.7","children":[{"name":"y = 2"}]}]},{"name":"Hurricane_temp","children":[{"name":"Config 2 weight 0.7","children":[{"name":"x = 1"},{"name":"w = 1.5"}]},{"name":"Config 2 weight 0.7","children":[]}]}]}';
	
	//D3 JS code with accessed json from file
	var historyJSON;
	var historyString = "";

	var margin = {top: 30, right: 20, bottom: 30, left: 20},
	width = 400,
	barHeight = 20,
	barWidth = (width - margin.left - margin.right) * 0.8;

	var i = 0,
	duration = 400,
	root;

	var diagonal = d3.linkHorizontal()
	.x(function(d) { return d.y; })
	.y(function(d) { return d.x; });

	var svg = d3.select("#part1").append("svg")
	.attr("width", width) // + margin.left + margin.right)
	.append("g")
	.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
	
	historyJSON = js_obj;

	 //START: D3.js code for Collapsible Indent Tree		
	 root = d3.hierarchy(historyJSON); 
	 root.x0 = 0;
	 root.y0 = 0;
	 update(root);
	 
	 function update(source) {
	
	  // Compute the flattened node list.
	  var nodes = root.descendants();
	
	  var height = Math.max(500, nodes.length * barHeight + margin.top + margin.bottom);
	
	  d3.select("svg").transition()
	      .duration(duration)
	      .attr("height", height);
	
	  d3.select(self.frameElement).transition()
	      .duration(duration)
	      .style("height", height + "px");
	
	  // Compute the "layout". TODO https://github.com/d3/d3-hierarchy/issues/67
	  var index = -1;
	  root.eachBefore(function(n) {
	    n.x = ++index * barHeight;
	    n.y = n.depth * 20;
	  });
	
	  // Update the nodes…
	  var node = svg.selectAll(".node")
	    .data(nodes, function(d) { return d.id || (d.id = ++i); });
	
	  var nodeEnter = node.enter().append("g")
	      .attr("class", "node")
	      .attr("transform", function(d) { return "translate(" + source.y0 + "," + source.x0 + ")"; })
	      .style("opacity", 0);
	
	  // Enter any new nodes at the parent's previous position.
	  nodeEnter.append("rect")
	      .attr("y", -barHeight / 2)
	      .attr("height", barHeight)
	      .attr("width", 300) //AVG changed
	      .style("fill", color)
	      .on("click", click);
	
	  nodeEnter.append("text")
	      .attr("dy", 3.5)
	      .attr("dx", 5.5)
	      .attr("myclass", "custom") //added
	      .attr("mydata", function(d) { return d.data.name; }) //added 
	      .text(function(d) { return d.data.name; });
	
	  // Transition nodes to their new position.
	  nodeEnter.transition()
	      .duration(duration)
	      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
	      .style("opacity", 1);
	
	  node.transition()
	      .duration(duration)
	      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
	      .style("opacity", 1)
	    .select("rect")
	      .style("fill", color);
	
	  // Transition exiting nodes to the parent's new position.
	  node.exit().transition()
	      .duration(duration)
	      .attr("transform", function(d) { return "translate(" + source.y + "," + source.x + ")"; })
	      .style("opacity", 0)
	      .remove();
	
	  // Update the links…
	  var link = svg.selectAll(".link")
	    .data(root.links(), function(d) { return d.target.id; });
	
	  // Enter any new links at the parent's previous position.
	  link.enter().insert("path", "g")
	      .attr("class", "link")
	      .attr("d", function(d) {
	        var o = {x: source.x0, y: source.y0};
	        return diagonal({source: o, target: o});
	      })
	    .transition()
	      .duration(duration)
	      .attr("d", diagonal);
	
	  // Transition links to their new position.
	  link.transition()
	      .duration(duration)
	      .attr("d", diagonal);
	
	  // Transition exiting nodes to the parent's new position.
	  link.exit().transition()
	      .duration(duration)
	      .attr("d", function(d) {
	        var o = {x: source.x, y: source.y};
	        return diagonal({source: o, target: o});
	      })
	      .remove();
	
	  // Stash the old positions for transition.
	  root.each(function(d) {
	    d.x0 = d.x;
	    d.y0 = d.y;
	  });
	}
	
	// Toggle children on click.
	function click(d) {
	  if (d.children) {
	    d._children = d.children;
	    d.children = null;
	  } else {
	    d.children = d._children;
	    d._children = null;
	  }
	  update(d);
	}
	
	function color(d) {
	  return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
	}
	  
	//END: D3.js code for Collapsible Indent Tree		
	  
	  
}//END: function d3_collapsible_indent_tree(json)
//); getJSON

function construct_history_json(response)
{
	//Added dummy values
	/*
	if (response.hasOwnProperty('upstream') && response['upstream'].length==0 && response['jobs'].length!=0)
	{
		var x = {"humidity":40,"wind":3.2};
		response["jobs"][0]["variables"] = x;
	}
	else 
	if (response.hasOwnProperty('upstream') && response['upstream'].length>=1)
	{
			var x = {"humidity":40,"wind":3.2};
			response["jobs"][0]["variables"] = x;
			x = {"parameter 1":15,"parameter 2":2.5};
			response["upstream"][1]["variables"] = x;
	}*/
	//x = {"c":1,"d":1.5};
	//response["upstream"][0]["variables"] = x;
	//x = {"c":2,"d":2.5};
	//response["upstream"][1]["variables"] = x;
	
	//Construct map with model names and values as weight
	//Traverse current job and upstream and downstream jobs 
	var modelMap = {};
	var cur_jobs = [];
	var config_counter=1;
	var model_type
	for(var i=0; i<response["jobs"].length; i++)
	{
		current_job = response["jobs"][i];
		model_type = current_job["model_type"];
		
		var variables_arr=[]
		
		for (var key in current_job["variables"]) {
				var keyValueStr =  String(key)+" = "+String(current_job["variables"][key]);
				variables_arr.push({name: keyValueStr});
		}
		
		var relevance = 1.0; 
		if(current_job.hasOwnProperty("relevance")){
			var relevance = current_job["relevance"];
			
		}
		
		var contribution = 1.0; 
		if(current_job.hasOwnProperty("output_dsir")){
			var counter = current_job["output_dsir"]["counter"];
			for(var x=0; x<response["contribution"].length; x++)
			{
					var contributionDsirMap = response["contribution"][x];
					console.log("### x="+x+ " counter="+counter);
					console.log(contributionDsirMap["metadata"]);
					if(contributionDsirMap["_id"]["counter"]==counter)
					{
						contribution = contributionDsirMap["metadata"]["contribution"];	
						console.log("Contribution Found:"+contribution);
					}
			}
			
		}
		
		/*
		var wt = 1.0; 
		if(current_job["weights"].length>0){
			var weightsArr = current_job["weights"][i];
			console.log("########wt:");
			wt = weightsArr[1];
			console.log(wt);
			
		}*/
		var config = {
				name: "Configuration "+config_counter+": Relevance = "+relevance.toFixed(2).toString()+" Contribution = "+contribution.toFixed(2).toString(),
				children: variables_arr
		};
		config_counter++;
		cur_jobs.push(config);
		
		if(modelMap.hasOwnProperty(model_type))
		{
			modelMap[model_type].push(config);
		}
		else
		{
			modelMap[model_type] = [config];
		}
			
	}
	

	console.log("modelMap=")
	console.log(modelMap)
	
	//upstream jobs
	var cur_jobs = [];
	for(var i=0; i<response["upstream"].length; i++)
	{
		current_job = response["upstream"][i];
		model_type = current_job["model_type"];
		
		var variables_arr=[]
		
		for (var key in current_job["variables"]) {
				var keyValueStr =  String(key)+" = "+String(current_job["variables"][key]);
				variables_arr.push({name: keyValueStr});
		}
		
		var relevance = 1.0; 
		if(current_job.hasOwnProperty("relevance")){
			var relevance = current_job["relevance"];
			
		}
		var contribution = 1.0; 
		if(current_job.hasOwnProperty("output_dsir")){
			var counter = current_job["output_dsir"]["counter"];
			for(var x=0; x<response["contribution"].length; x++)
			{
					var contributionDsirMap = response["contribution"][x];
					console.log("### x="+x+ " counter="+counter);
					console.log(contributionDsirMap["metadata"]);
					if(contributionDsirMap["_id"]["counter"]==counter)
					{
						contribution = contributionDsirMap["metadata"]["contribution"];	
						console.log("Contribution Found:"+contribution);
					}
			}
			
		}
		
		
		/*
		var wt = 1.0; 
		if(current_job["weights"].length>0){
			var weightsArr = current_job["weights"][i];
			console.log("########wt:");
			wt = weightsArr[1];
			console.log(wt);
		}
		*/
		
		var config = {
				name: "Configuration "+config_counter+": Relevance = "+relevance.toFixed(2).toString()+" Contribution = "+contribution.toFixed(2).toString(),
				children: variables_arr
		};
		//cur_jobs.push(config);
		config_counter++;
		if(modelMap.hasOwnProperty(model_type))
		{
			modelMap[model_type].push(config);
		}
		else
		{
			modelMap[model_type] = [config];
		}
			
	}
	
	//if(response.hasOwnProperty(model_type))
	//{
		//modelMap[model_type] = cur_jobs;
	//}

	console.log("modelMap=")
	console.log(modelMap)
	
	var provenance_js_obj = {
		name: "Provenance",
		children: []
	}
	
	for (var key in modelMap) {
		//console.log(key);
		//console.log(modelMap[key]);
		var models_js_obj = {
				name: key,
				children: modelMap[key]
		}
		
		provenance_js_obj["children"].push(models_js_obj);
				
	}
	
	console.log(provenance_js_obj);
	
	console.log(JSON.stringify(provenance_js_obj));
	return provenance_js_obj;
}


/* Earlier d3 invoke function
d3.json(historyJSON, function(error, flare) {
  if (error) throw error;
  root = d3.hierarchy(historyJSON); 
  root.x0 = 0;
  root.y0 = 0;
  update(root);
//});
*/


</script>

<!-- Added Style for correcting d3 boxes -->
<style>
.node rect {
  cursor: pointer;
  fill: #fff;
  fill-opacity: 0.5;
  stroke: #3182bd;
  stroke-width: 1.5px;
}

.node text {
  font: 11px sans-serif;
  pointer-events: none;
}

.link {
  fill: none;
  stroke: #9ecae1;
  stroke-width: 1.5px;
}


</style>

</body>
</html>

