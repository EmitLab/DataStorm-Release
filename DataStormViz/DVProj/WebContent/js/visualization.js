//All layer data, can be updated through websocket
var VISUALIZATION_JSON = [];
//All google maps polygon data
var GRIDS = [];
//Cached mongo data based on timestamp
var CACHE = {};
//Event listeners attached to google maps polygons
var LISTENERS = [];
//Layer functions to be called when explain button is clicked
var EXPLANATIONS = {};

//Visualization layer functions
//Takes in data type, data and options json
//Ex. VISUALIZATION_FUNCTIONS["heat_map"](dataJson, optionsJson);
var VISUALIZATION_FUNCTIONS = {
		//Heat map creates rectangles colored according to the value and color scale (defined in VISUALIZATION_JSON)
		"heat_map": function(mapId, data, options) {
			//If polygon layer already exists, delete old layer
			if(GRIDS[mapId][options.name]) clearGrid(mapId, options.name);
			else GRIDS[mapId][options.name] = [];
			
			//Set min and max for color scaling
			var min = options.min || getMinValue(data, options.values["value"]);
			var max = options.max || getMaxValue(data, options.values["value"]);
			
			//For each json object in the data, create google maps api polygon
			for(var i = 0; i < data.length; i++) {
				var json = data[i];

				var lng = parseFloat(json.coordinate[0]);
				var lat = parseFloat(json.coordinate[1]);
				var value = parseFloat(json.observation[options.values["value"]]);
				var color = options.colors[getLegendIndex(value, min, max, options.colors.length)];
				
				//If value is below threshold, do not create polygon
				if(value < min) continue;
				
				//List of coordinates for polygon
				var coords = [
					{lat: lat, lng : lng},
					{lat: lat, lng : lng + options.size},
					{lat: lat + options.size, lng: lng + options.size},
					{lat: lat + options.size, lng: lng}
				];
				
				
				//Create polygon object and store in GRIDS array
				GRIDS[mapId][options.name][i] = new google.maps.Polygon({
					cLat: (lat + lat + options.size) / 2,
					cLng: (lng + lng + options.size) / 2,
					paths: coords,
					fillColor: color,
					fillOpacity: options.opacity || 0.4,
					strokeWeight: 0.0,
					zIndex: 0
				});
				
				
				//Add event listener to this polygon
				addListener({
					mapId: mapId,
					id: json._id,
					name: options.name,
					lng: parseFloat(lng.toFixed(2)),
					lat: parseFloat(lat.toFixed(2)),
					value: value,
					color: color,
					paths: coords
				}, function(content) {
					if ($("#info-graphics").css("display") === "none") $("#info-graphics").css("display", "block");
					
					$(".map").removeClass("active");
					$("#map-instance-" + (content.mapId + 1)).addClass("active");
					
					$("#instance-value").text(content.mapId + 1);
					$("#location-value").text(content.lat + ", " + content.lng);
					$("#flood-value").text(content.value.toFixed(2));
					$("#flood-color").css("background-color", content.color).css("opacity", 0.4);
					
					//Update explain button link
					EXPLANATIONS[content.name] = function() {
						var id = content.id;
						var url = "provenance.jsp?" + "timestamp=" + id.timestamp +  "&machineIdentifier=" + id.machineIdentifier + 
						"&processIdentifier=" + id.processIdentifier + "&counter=" + id.counter;

						if($("#flood-checkbox").get(0).checked) {
							window.open(url + "&model=flood");
						}
					};
				});
			}
		},
		//Heat map creates rectangles sized according to the value and size scale (defined in VISUALIZATION_JSON)
		"square_map": function(mapId, data, options) {
			//If polygon layer already exists, delete old layer
			if(GRIDS[mapId][options.name]) clearGrid(mapId, options.name);
			else GRIDS[mapId][options.name] = [];
			
			//Set min and max for size scaling
			var min = options.min || getMinValue(data, options.values["value"]);
			var max = options.max || getMaxValue(data, options.values["value"]);
			
			//For each json object in the data, create google maps api polygon
			for(var i = 0; i < data.length; i++) {
				var json = data[i];

				var lng = parseFloat(json.coordinate[0]);
				var lat = parseFloat(json.coordinate[1]);
				var value = parseFloat(json.observation[options.values["value"]]);

				var size = options.sizes[getLegendIndex(value, min, max, options.sizes.length)];
				var color = options.colors[getLegendIndex(value, min, max, options.colors.length)];
				
				//If value is below threshold, do not create polygon
				if(value < min) continue;
				
				//List of coordinates for polygon
				var coords = [
					{lat: lat - size / 2 + options.size / 2, lng: lng - size / 2 + options.size / 2},
					{lat: lat - size / 2 + options.size / 2, lng: lng + size / 2 + options.size / 2},
					{lat: lat + size / 2 + options.size / 2, lng: lng + size / 2 + options.size / 2},
					{lat: lat + size / 2 + options.size / 2, lng: lng - size / 2 + options.size / 2}
				];

				if(value > 2) {
				//Create polygon object and store in GRIDS array
					GRIDS[mapId][options.name][i] = new google.maps.Polygon({
						paths: coords,
						fillColor: color,
						fillOpacity: 0.0,
						strokeColor: color,
						strokeOpacity: options.opacity || 0.4,
						strokeWeight: 2.0,
						zIndex: 1
					});
					
					//Add event listener to this polygon
					addListener({
						mapId: mapId,
						id: json._id,
						name: options.name,
						lng: parseFloat(lng.toFixed(2)),
						lat: parseFloat(lat.toFixed(2)),
						value: value,
						color: color,
						paths: coords
					}, function(content) {
						if ($("#info-graphics").css("display") === "none") $("#info-graphics").css("display", "block");
						
						$(".map").removeClass("active");
						$("#map-instance-" + (content.mapId + 1)).addClass("active");
						
						$("#instance-value").text(content.mapId + 1);
						$("#location-value").text(content.lat + ", " + content.lng);
						$("#rain-value").text(content.value.toFixed(2));
						$("#rain-color").css("background-color", content.color).css("opacity", 0.4);
						
						//Update explain button link
						EXPLANATIONS[content.name] = function() {
							var id = content.id;
							var url = "provenance.jsp?" + "timestamp=" + id.timestamp +  "&machineIdentifier=" + id.machineIdentifier + 
							"&processIdentifier=" + id.processIdentifier + "&counter=" + id.counter;

							if($("#hurricane-checkbox").get(0).checked) {
								window.open(url + "&model=hurricane");
							}
						};
					});
				}

			}
		},
		"vector": function(mapId, data, options) {
			//If polygon layer already exists, delete old layer
			if(GRIDS[mapId][options.name]) clearGrid(mapId, options.name);
			else GRIDS[mapId][options.name] = [];
			
			//For each json object in the data, create google maps api polygon
			for (var i = 0; i < data.length; i++) {
				var json = data[i];

				var lng = parseFloat(json.coordinate[0]);
				var lat = parseFloat(json.coordinate[1]);
				var u = parseFloat(json.observation[options.values["u"]]);
				var v = parseFloat(json.observation[options.values["v"]]);
				var value = parseFloat(json.observation[options.values["value"]]);
				var radius = 1250;
				//var radius = parseInt(1250 * (options.sizes[getLegendIndex(value, min, max, options.sizes.length)] / options.size));
				
				//List of coordinates for polygon
				var coords = [
					{lat: lat + options.size / 2, lng: lng + options.size / 2},
					{lat: lat + options.size / 2 + (v / 20), lng: lng + options.size / 2 + (u / 20)}
				];

				if (u != 0){
					//Create polygon object and store in GRIDS array
					GRIDS[mapId][options.name][i] = new google.maps.Polyline({
						path: coords,
						geodesic: true,
						strokeColor: '#FF0000',
						strokeOpacity: 1.0,
						strokeWeight: 1,
						zIndex: 2
					});
					//Create polygon object and store in GRIDS array
					GRIDS[mapId][options.name][i + data.length] = new google.maps.Circle({
						strokeOpacity: 0,
						fillColor: '#FF0000',
						fillOpacity: 0.4,
						center: coords[1],
						radius: radius, //1250
						zIndex: 2
					});
					
					//Add event listener to this polygon
					addListener({
						mapId: mapId,
						id: json._id,
						name: options.name,
						lng: parseFloat(lng.toFixed(2)),
						lat: parseFloat(lat.toFixed(2)),
						u: u.toFixed(2),
						v: v.toFixed(2)
					}, function(content) {
						if ($("#info-graphics").css("display") === "none") $("#info-graphics").css("display", "block");
						
						$("#instance-value").text(content.mapId + 1);
						$("#location-value").text(content.lat + ", " + content.lng);
						$("#wind-value").text(Math.sqrt(content.u * content.u + content.v * content.v).toFixed(2));
						$("#u-wind-value").text(content.u);
						$("#v-wind-value").text(content.v);
					});
				}

			}
		},
		"circle_map": function(mapId, data, options) {
			//If polygon layer already exists, delete old layer
			if(GRIDS[mapId][options.name]) clearGrid(mapId, options.name);
			else GRIDS[mapId][options.name] = [];
			
			//For each json object in the data, create google maps api polygon
			for (var i = 0; i < data.length; i++) {
				var json = data[i];
				
				var lng = parseFloat(json.coordinate[0]);
				var lat = parseFloat(json.coordinate[1]);
				var label = json.observation[options.values["label"]];
				var u = -parseFloat(json.observation[options.values["v"]]);
				var v = -parseFloat(json.observation[options.values["u"]]);
				var magnitude = Math.sqrt(u * u + v * v);
				var nu = u / magnitude;
				var nv = v / magnitude;
				
				var weight = parseInt(label.substring(1)) / 50;
				//var color = "rgba(" + parseInt(255 * weight) + ", " + parseInt(165 * weight) + ", 0, 1)";
				
				var color = "orange";
				
				var radius = 0.027;
				var coords = [
					{lat: lat + nu / 15, lng: lng + nv / 15},
					{lat: lat + nv * radius, lng: lng + -nu * radius},
					{lat: lat + -nv * radius, lng: lng + nu * radius}
				];
				
				GRIDS[mapId][options.name][i] = new google.maps.Polygon({
					path: coords,
					strokeOpacity: 0,
					fillColor: color,
					fillOpacity: options.opacity || 0.4,
					zIndex: 4
				});
				
				//Create polygon object and store in GRIDS array
				GRIDS[mapId][options.name][i + data.length] = new google.maps.Circle({
					strokeOpacity: 0,
					fillColor: color,
					fillOpacity: options.opacity || 0.4,
					center: new google.maps.LatLng(lat, lng),
					radius: 3000,
					zIndex: 4
				});
				
				GRIDS[mapId][options.name][i + data.length * 2] = new google.maps.Circle({
					strokeOpacity: 0,
					fillColor: 'black',
					fillOpacity: options.opacity || 0.4,
					center: new google.maps.LatLng(lat + u, lng + v),
					radius: 1500,
					zIndex: 4
				});
				
				GRIDS[mapId][options.name][i + data.length * 3] = new google.maps.Polyline({
					path: [
						{lat: lat, lng: lng},
						{lat: lat + u, lng: lng + v}
					],
					geodesic: true,
					strokeColor: 'black',
					strokeOpacity: 0.0,
					icons: [{
						icon: {
							path: 'M 0,-1 0,1',
							strokeOpacity: options.opacity || 0.4,
							scale: 2
					    },
			            offset: '0',
			        	repeat: '20px'
			        }],
					zIndex: 2
				});
				
				try {
					GRIDS[mapId][options.name][i + data.length * 4] = new MapLabel({
						text: label,
						position: new google.maps.LatLng(lat, lng + radius * 1.5),
						fontSize: 10,
						align: 'center'
					});
				} catch (err) {
					initMaps();
					GRIDS[mapId][options.name][i + data.length * 4] = new MapLabel({
						text: label,
						position: new google.maps.LatLng(lat, lng + radius * 1.5),
						fontSize: 10,
						align: 'center'
					});
				}
				
				//Add event listener to this polygon
				addListener({
					mapId: mapId,
					id: json._id,
					name: options.name,
					lng: parseFloat(lng.toFixed(2)),
					lat: parseFloat(lat.toFixed(2)),
					label: label
				}, function(content) {
					if ($("#info-graphics").css("display") === "none") $("#info-graphics").css("display", "block");
					
					$(".map").removeClass("active");
					$("#map-instance-" + (content.mapId + 1)).addClass("active");
					
					$("#instance-value").text(content.mapId + 1);
					$("#location-value").text(content.lat + ", " + content.lng);
					$("#human-mobility-value").text(content.label);
					
					//Update explain button link
					EXPLANATIONS[content.name] = function() {
						var id = content.id;
						var url = "provenance.jsp?" + "timestamp=" + id.timestamp +  "&machineIdentifier=" + id.machineIdentifier + 
						"&processIdentifier=" + id.processIdentifier + "&counter=" + id.counter;

						if($("#human-mobility-checkbox").get(0).checked) {
							window.open(url + "&model=human_mobility");
						}
					};
				});
			}
		}
};

//Takes in visualization layer json and generates polygons
function generate(json, queue, layerId, mapId) {
	queue = queue || [];
	layerId = layerId || 0;
	mapId = mapId || 0;

	if(layerId == 0) {
		clearListeners(mapId);
		for(var j in json) {
			setGridVisibility(mapId, json[j].options.name, false);
		}
	}

	var v = json[layerId];
	
	var offset = mapId * 10800 * 3;
	
	//Query to be passed to mongodb
	var data = JSON.stringify({
		model_type: v.model_type,
		start_time: getTimestamp() + offset,
		end_time: getTimestamp() + 10800 + offset,
		instance: mapId,
		threshold: v.options.min
	});

	if(CACHE[data]) {
		//Data is already cached, use cached data
		//console.log("Getting cached data: " + data);
		VISUALIZATION_FUNCTIONS[v.visual_type](mapId, CACHE[data], v.options);
		if(getFilter(v.options.name)) {
			queue.push(v.options.name);
		}

		if(layerId < json.length - 1) {
			generate(json, queue, layerId + 1, mapId);
			return;
		}
		else {
			for(var j in queue) {
				setGridVisibility(mapId, queue[j], true);
			}
			if(mapId < MAPS.length - 1) {
				generate(json, [], 0, mapId + 1);
			}
		}
	}
	else {
		//Data is not cached, call mongodb for new data
		//console.log("Caching new data: " + data);
		$.ajax({
			type: "POST",
			url: "Mongoconn",
			contentType: "application/json",
			data: data,
			success: function(res) {
				CACHE[data] = res;
				if(res.length > 0) {
					//Make sure mongo data is still relevant to the current timestamp
					var delta = res[0].timestamp - getTimestamp();
					if(delta >= 0 && delta < 10800) {
						//console.log("DATA CORRECT");
						VISUALIZATION_FUNCTIONS[v.visual_type](mapId, res, v.options);
					}
					//If not, attempt to generate grid based on cache
					else {
						var updatedData = JSON.parse(data);
						updatedData.start_time = getTimestamp();
						updatedData.end_time = getTimestamp() + 10800;
						updatedData = JSON.stringify(updatedData);
						if(CACHE[updatedData]) {
							//Data incorrect, but cache with correct data exists, use cached data
							VISUALIZATION_FUNCTIONS[v.visual_type](mapId, CACHE[updatedData], v.options);
						}
						else {
							//Data incorrect and cache does not exist, regenerate again
							generate(json, [], 0, mapId);
							return;
						}
					}

					if(getFilter(v.options.name)) {
						queue.push(v.options.name);
					}
				}
				
				if(layerId < json.length - 1) {
					generate(json, queue, layerId + 1, mapId);
					return;
				}
				else {
					for(var j in queue) {
						setGridVisibility(mapId, queue[j], true);
					}
					if(mapId < MAPS.length - 1) {
						generate(json, [], 0, mapId + 1);
					}
				}
			}
		});
	}
}

//Sets the visibility of a grid layer
function setGridVisibility(mapId, name, state) {
	var grid = GRIDS[mapId][name];
	for(var i in grid) grid[i].setMap(state ? MAPS[mapId] : null);
}

//Deletes all polygons in grid
function clearGrid(mapId, name) {
	setGridVisibility(mapId, name, false);
	GRIDS[mapId][name] = [];
}

//Returns GMT timestamp according to slider
function getTimestamp() {
	var date = new Date($("#slider").slider('getValue') * 1000);
	return new Date(date.valueOf() - date.getTimezoneOffset() * 60000).getTime() / 1000;
}

//Returns minimum value in data set, index refers to the observation array
function getMinValue(data, index) {
	if(!data || data.length <= 0) return;
	index = index || 0;

	var min = data[0].observation[index];
	for(var i in data){
		var value = data[i].observation[index];
		if(min > value) min = parseFloat(value);
	}
	return min;
}

//Returns maximum value in data set, index refers to the observation array
function getMaxValue(data, index) {
	if(!data || data.length <= 0) return;
	index = index || 0;

	var max = data[0].observation[index];
	for(var i in data){
		var value = data[i].observation[index];
		if(max < value) max = parseFloat(value);
	}
	return max;
}

function getLegendIndex(val, min, max, size) {
	var bin = 0;
	var notFound = true;
	var start = min + (max / size);
	while (start < max && notFound) {
		if (val < start){
			notFound = false;
		} else {
			start += max / size;
			bin++;
		}
	}
	return bin;
}

//Adds an event listener to the google maps polygon
//Makes an invisible grid that pools together nearby polygons so one click will activate all polygon listeners in that grid
function addListener(content, funct) {
	//If event listener already exists in this location, add polygon data to this listener
	for(var i in LISTENERS[content.mapId]) {
		var l = LISTENERS[content.mapId][i];
		if(Math.abs(l.contents[0].lat - content.lat) < .05 && Math.abs(l.contents[0].lng - content.lng) < .05) {
			l.contents.push(content);
			l.functions.push(funct);
			return;
		}
	}
	
	//Make new listener
	LISTENERS[content.mapId].push({
		polygon: null,
		contents: [content],
		functions: [funct]
	});
	var listener = LISTENERS[content.mapId][LISTENERS[content.mapId].length - 1];
	
	//Create invisible polygon on top of the other polygons to hold event listener
	//Allows for more than one layer to be clicked at once
	var polygon = new google.maps.Polygon({
		fillOpacity: 0.0,
		listener: listener,
		//change this
		map: MAPS[content.mapId],
		paths: [
			{lat: content.lat, lng : content.lng},
			{lat: content.lat, lng : content.lng + 0.1},
			{lat: content.lat + 0.1, lng: content.lng + 0.1},
			{lat: content.lat + 0.1, lng: content.lng}
		],
		strokeWeight: 0.0,
		zIndex: 9
	});

	listener.polygon = polygon;

	google.maps.event.addListener(polygon, 'click', function() {
		$('#map').removeClass('col-sm-12');
		$('#map').addClass('col-sm-8');
		$('#sidebar').addClass('col-sm-4');
		$('#sidebar').css('display', 'block');
		
		var l = polygon.listener;
		for(var i in l.contents) {
			l.functions[i](l.contents[i]);
		}
	});
}

//Clears all google maps polygon event listeners
//Called when regenerating polygons in generate()
function clearListeners(mapId) {
	for(var i in LISTENERS[mapId]) {
		var l = LISTENERS[mapId][i];
		l.polygon.setMap(null);
	}
	LISTENERS[mapId] = [];
}

function LogOut(){
    $.ajax({
	    type: "POST",
	    url: "Logoutconn",//servlet
	    contentType: "application/json", // NOT dataType!
	    data: null,
	    success: function(response) {

	    	if( r == 200){
	    		//todo
	    	}
	    	if(r == 400){
	    		//todo
	    		
	    	}
	    	
	    }
	});

}

/*function updateFloodThreshold(flag){
	try{
		var $value = $("#flood-control-value");
		var currVal = parseInt($value.text());
		if (flag){
			// Increase Flood Threshold, if flag is true;
			$value.text(currVal+1);
		} else {
			// Decrease Flood Threshold, if flag is true;
			$value.text(currVal-1);
		}
		setFloodGrids();
		toggleBarPlot();
	} catch(err){
		console.error(err);
	}
}

$(window).bind('load', function() {
	try	{
		 COUPLING MOUSE OVER EVENTS 
		$("#flood-control-down").on("click", function(){
			updateFloodThreshold(false);
		});
		$("#flood-control-up").on("click", function(){
			updateFloodThreshold(true);
		});
		$('[data-toggle="tooltip"]').tooltip();	
	} catch(err){
		console.error(err);
	}
});*/
