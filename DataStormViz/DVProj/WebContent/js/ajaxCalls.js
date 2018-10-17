//START: For Hurricane data using mongo servlet connection 
$(document).on("click", "#mongoServletHurricane", function() { // When HTML DOM "click" event is invoked on element with ID "somebutton", execute the following function...
    console.log("Inside Hurricane function.........");

    var data = {
    	    model_type: "hurricane",
    	    start_time: 1530424800,
    	    end_time: 1530424800 + 10800
    	};

    	$.ajax({
    	    type: "POST",
    	    url: "Mongoconn",
    	    contentType: "application/json", // NOT dataType!
    	    data: JSON.stringify(data),
    	    success: function(response) {
    	    	console.log("response from ajax call="); 
    	    	console.log(response); //Access ALL JS objects from response
    	    	console.log("Accessing first object="); 
    	    	console.log(response[0]); //Access one JS object from response
    	    	
    	    	//-------Write your code here-------
    	    	//Invoke your custom function to display the hurricane on map using this response
    	    	
    	    }
    	});
   
    	
    	
    	
/*Another way for Ajax get request 
	$.get("Mongoconn", function(responseText) {   // Execute Ajax GET request on URL of "someservlet" and execute the following function with Ajax response text...
        $("#servletResults").text(responseText);           // Locate HTML DOM element with ID "somediv" and set its text content with the response text.
   		console.log(responseText)
	});*/
});
//END: For Hurricane data using mongo servlet connection 

//START: For Flood data using mongo servlet connection 
$(document).on("click", "#mongoServletFlood", function() { // When HTML DOM "click" event is invoked on element with ID "somebutton", execute the following function...
    console.log("Inside Flood function.........");

    var data = {
    	    model_type: "flood",
    	    start_time: 1533651013,
    	    end_time: 1533653613
    	};

    	$.ajax({
    	    type: "POST",
    	    url: "Mongoconn",
    	    contentType: "application/json", // NOT dataType!
    	    data: JSON.stringify(data),
    	    success: function(response) {
    	    	console.log("response from ajax call="); 
    	    	console.log(response); //Access ALL JS objects from response
    	    	console.log("Accessing first object="); 
    	    	console.log(response[0]); //Access one JS object from response
    	    	
    	    	//-------Write your code here-------
    	    	//Invoke your custom function to display the hurricane on map using this response
    	    	
    	    }
    	});
 
});
//END: For Flood data using mongo servlet connection

//START: For Human Mobility data using mongo servlet connection 
$(document).on("click", "#mongoServletHumanMobility", function() { // When HTML DOM "click" event is invoked on element with ID "somebutton", execute the following function...
    console.log("Inside Human Mobility function.........");

    var data = {
    	    model_type: "human_mobility",
    	    start_time: 1533651013,
    	    end_time: 1533653613
    	};

    	$.ajax({
    	    type: "POST",
    	    url: "Mongoconn",
    	    contentType: "application/json", // NOT dataType!
    	    data: JSON.stringify(data),
    	    success: function(response) {
    	    	console.log("response from ajax call="); 
    	    	console.log(response); //Access ALL JS objects from response
    	    	console.log("Accessing first object="); 
    	    	console.log(response[0]); //Access one JS object from response
    	    	
    	    	var humanMobility = [];
    	    	
                for (var i = 0; i < response.length; i++) {
                	
                	var coordinates = response[i].coordinate;
                	var lng = parseFloat(coordinates[0]);
                	var lat = parseFloat(coordinates[1]);
                	var latlng = new google.maps.LatLng(lat, lng);
                	
                	if (lat >= 25 && lng >= -87) {
	    				humanMobility[i] = new google.maps.Circle({
	    		            strokeOpacity: 0,
	    		            fillColor: '#8B0000',
	    		            fillOpacity: 0.4,
	    		            center: latlng,
	    		            radius: 1000 * response[i].observation
	    		          });
                	}
                	
                	// code for displaying text instead of circles
//                	var mapLabel = new MapLabel({
//                		text: response[i].observation,
//                		position: latlng,
//                		map: map,
//                		fontSize: 12,
//                		align: 'center'
//                	});
//                	mapLabel.set('position', latlng);
                	
//                	var marker = new google.maps.Marker();
//                	marker.bindTo('map', mapLabel);
//                	marker.bindTo('position', mapLabel);
//                	marker.setDraggable(true);
                }
                
                for (l in humanMobility) {
                	humanMobility[l].setMap(map);
                }
    	    	
    	    }
    	});
 
});
//END: For Human Mobility data using mongo servlet connection

