var socket;
var socketFlag = true;

$(document).ready(function() {
	//Socket communication code
	//?ip=127.0.0.1&port=3000
	var urlParams = new URLSearchParams(window.location.search);
	var s_ip = urlParams.get('ip')
	var s_port = urlParams.get('port')
	var ip = "127.0.0.1";
	var port = "3000";
	if(s_ip) 
		ip = s_ip;
	if(s_port)
		port = s_port;
	
	try { 
		socket = new WebSocket("ws://"+ip+":"+port+"/");
		console.log("New Socket opened...."+socket);
		socketFlag = true;
	}
	catch(err) {
		socketFlag = false; //Socket connection failed...
        console.log("Cannot open socket connection...");
    }
	
	socket.onerror = function(e){
	    console.log("Error in socket connection");
	    socketFlag = false; //Socket connection failed...
		setConfig(DEFAULT_CONFIG_JSON);
		setVisualizationConfig(DEFAULT_VISUALIZATION_JSON);
		setGrids();
	}
	
	socket.onmessage = function(e) {
		var data = JSON.parse(e.data);
		var type = data.type;
		var content = data.content;
		switch(type) {
			case 'set_config':
				setConfig(content);
				setGrids();
				break;
			case 'set_visualization_config':
				setVisualizationConfig(content);
				break;
			default:
				break;
		}
	};
	
});
