var _configState;
setConfigState(getUrlParam("state") || "socket");

var DEFAULT_CONFIG_JSON = {
	'date': {
		'begin': "Jul 01 2018 00:00:00",
		'end': "Jul 03 2018 00:00:00"
	},
	'filters': {
		'flood': true,
		'human_mobility': true,
		'rain': true,
		'wind': true
	},
	'map': {
		'lat': 26.705,
		'lng': -83.03,
		'zoom': 7
	}
};

var DEFAULT_VISUALIZATION_JSON = [
	{
		'model_type': "hurricane",
		'visual_type': "vector",
		'options': {
			'name': "wind",
			'min': 0.2,
			'size': 0.1,
			'sizes': [0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
			'values': {"value": 0, "u": 1, "v": 2}
		}
	},
	{
		'model_type': "hurricane",
	   	'visual_type': "square_map",
	   	'options': {
	   		'name': "rain",
	   		'colors': ["#008000"],
	   		'max': 20,
	   		'min': 0.2,
	   		'opacity': 0.6,
	   		'sizes': [0, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1],
	   		'size': 0.1,
	   		'values': {"value": 0}
	   	}
	},
	{
		'model_type': "flood",
		'visual_type': "heat_map",
		'options': {
			'name': "flood",
			'colors': ["#000DBF", "#1A00C3", "#4400C7", "#6F00CB", "#9C00CF", "#CB00D4", "#D800B4", "#DC008A", "#E0005F", "#E50031"],
			'max': 180,//60000, //change this to fix flood color
			'min': .1,
			'opacity': 0.4,
			'size': 0.1,
			'values': {"value": 0}
		}
	},
	{
		'model_type': "human_mobility",
		'visual_type': "circle_map",
		'options': {
			'name': "human_mobility",
			'color': "#8B0000",
			'min': 0.1,
			'opacity': 0.6,
			'size': 0.1,
			'values': {"label": 0, "window": 1, "u": 2, "v": 3}
		}
	}
];

function getConfigState() {
	return _configState;
}

function setConfigState(value) {
	_configState = value;
	setUrlParam("state", value);
	updateUrl();
	
	var filter = $("#config-toggle")
	if(getConfigState() == "url") {
		filter.removeClass("fa-toggle-off");
		filter.addClass("fa-toggle-on");
	}
	else {
		filter.removeClass("fa-toggle-on");
		filter.addClass("fa-toggle-off");
	}
}

function toggleConfigState() {
	if(getConfigState() == "socket") {
		setConfigState("url");
	}
	else {
		setConfigState("socket");
	}
}

function setConfig(json) {
	if(getConfigState() != "socket") {
		return;
	}
	
	var date = json.date;
	$("#startDate").datepicker('setDate', new Date(date.begin));
	$("#endDate").datepicker('setDate', new Date(date.end));
	$(".input-daterange").datepicker('update');

	/*//Added for fetching slider values 
	function convertToEpoch2(input) {
		return (input.getTime() / 1000);
	}
	var st_date = convertToEpoch2($("#startDate").datepicker('getDate'));
	var inc = 0;
	if (date.hasOwnProperty("increment_hours")) {
		inc = date.increment_hours;
	}
	st_date = st_date + (date.increment_hours *  3600);
	$("#slider").slider('setAttribute', 'value', st_date);
	$("#slider").slider('refresh');
	setGrids();*/
			
	var filters = json.filters;
	for(var filter in filters) {
		if(filters.hasOwnProperty(filter)) {
			setFilter(filter, filters[filter]);
		}
	}
	
	for(var i = 0; i < MAPS.length; i++) {
		MAPS[i].setCenter({lat: json.map.lat, lng: json.map.lng});
		MAPS[i].setZoom(json.map.zoom);
	}
}

function setConfigFromUrl() {
	if(getConfigState() != "url") {
		return;
	}
	
	var start = parseInt(getUrlParam("start-date")) * 1000;
	var end = parseInt(getUrlParam("end-date")) * 1000;
	var timestamp = parseInt(getUrlParam("timestamp"));
	if(start && end) {
		$("#startDate").datepicker('setDate', new Date(start));
		$("#endDate").datepicker('setDate', new Date(end));
		$(".input-daterange").datepicker('update');
	}
	if(timestamp) {
		$("#slider").slider('setValue', timestamp);
	}
	
	setFilter("rain", getUrlParam("rain") == "true" ? true : false);
	setFilter("flood", getUrlParam("flood") == "true" ? true : false);
	setFilter("wind", getUrlParam("wind") == "true" ? true : false);
	setFilter("human_mobility", getUrlParam("human_mobility") == "true" ? true : false);
	
	for(var i = 0; i < MAPS.length; i++) {
		MAPS[i].setCenter({lat: parseFloat(getUrlParam("lat-" + i)), lng: parseFloat(getUrlParam("lng-" + i))});
		MAPS[i].setZoom(parseInt(getUrlParam("z-" + i)));
	}
}

function setVisualizationConfig(json) {
	VISUALIZATION_JSON = json;
}

$(document).ready(function() {
	setVisualizationConfig(DEFAULT_VISUALIZATION_JSON);
	if(getConfigState() == "url") {
		setConfigFromUrl();
		setGrids();
	}
});
