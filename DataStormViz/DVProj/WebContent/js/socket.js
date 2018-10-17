var socket;
var socketFlag = true;

$(document).ready(function() {
	
	//Hardcode for defaults 
	
	VISUALIZATION_JSON = [
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
	            'colors': ["#000DBF", "#1A00C3", "#4400C7", "#6F00CB", "#9C00CF", "#CB00D4", "#D800B4", "#DC008A",
	                       "#E0005F", "#E50031"],
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
	            'values': {"value": 0}
	        }
	    }
	];
	
	//Socket communication code
	//?ip=127.0.0.1&port=3000
	var urlParams = new URLSearchParams(window.location.search);
	var s_ip = urlParams.get('ip')
	var s_port = urlParams.get('port')
	var ip = "127.0.0.1";
	var port = "3000";
	if(s_ip)
	{
		ip = s_ip;
	} 
	if(s_port)
	{
		port = s_port;
	} 
	
	try { 
		socket = new WebSocket("ws://"+ip+":"+port+"/");
		console.log("New Socket opened...."+socket);
		socketFlag = true;
	}
	catch(err) {
		socketFlag = false; //Socket connection failed...
        console.log("Cannot open socket connection...");
    }
	
	socket.onerror=function(event){
	    console.log("Error in socket connection");
	    socketFlag = false; //Socket connection failed...
	    var data = {"type":"set_config","content":{"date":{"begin":"Jul 01 2018 00:00:00","end":"Jul 03 2018 00:00:00"},"filters":{"flood":true,"network":true,"rain":true,"wind":true}}};
		set_config(data);
	}
	
	//Uncomment following 2 lines and also uncomment at the bottom '};' line //Comment 3rd line: var data = {"type".... 
	socket.onmessage = function(event) {
		console.log(event.data);
		var data = JSON.parse(event.data);	
//		var data = {"type":"set_config","content":{"date":{"begin":"Jul 01 2018 00:00:00","end":"Jul 03 2018 00:00:00"},"filters":{"flood":true,"network":true,"rain":true,"wind":true}}};
		set_config(data);
		
	};
	
	function set_config(data){
		
		var type = data.type;
		var content = data.content;
		
		switch(type) {
			case 'set_visualization_config':
				VISUALIZATION_JSON = content;
				break;
			case 'set_config':
				var date = content.date;
				$("#startDate").datepicker('setDate', new Date(date.begin));
				$("#endDate").datepicker('setDate', new Date(date.end));
				$(".input-daterange").datepicker('update');

				//Added for fetching slider values 
				function convertToEpoch2(input) {
					return (input.getTime() / 1000);
				}
				var st_date = convertToEpoch2($("#startDate").datepicker('getDate'))
				var inc = 0;
				if (date.hasOwnProperty("increment_hours"))
				{
					inc = date.increment_hours;
				}
				st_date = st_date + (date.increment_hours *  3600);
				$("#slider").slider('setAttribute', 'value', st_date);
				$("#slider").slider('refresh');
				
				setGrids();
//				var setv = $("#slider").slider('getValue');
//				console.log("###setv:"+setv);
				
				var filters = content.filters;
				for(var filter in filters) {
					if(filters.hasOwnProperty(filter)) {
						setFilter(filter, filters[filter]);
					}
				}
				break;
			default:
				break;
		}
		
	}
	
});

//Controls html filter toggles in layer tab
function getFilter(id) {
	var filter = $("#" + id + "-toggle");
	return filter.hasClass("fa-toggle-on");
}

function setFilter(id, state) {
	var filter = $("#" + id + "-toggle");
	if(state) {
		filter.removeClass("fa-toggle-off");
		filter.addClass("fa-toggle-on");
	}
	else {
		filter.addClass("fa-toggle-off");
		filter.removeClass("fa-toggle-on");
	}
	setGridVisibility(id, state);
}

function toggleFilter(id) {
	setFilter(id, !getFilter(id));
}
