var map;

//called when google maps js file is loaded
function initMap() {
	map = new google.maps.Map(document.getElementById('map'), {
		center : {
			lat : 26.705,
			lng : -83.03
		},
		zoomControl : true,
		zoom : 7,
		minZoom : 6,
		maxZoom : 9,
		mapTypeControl : false,
		scaleControl : false,
		streetViewControl : false,
		rotateControl : false,
		fullscreenControl : false,
		scrollwheel : true,
		draggable : true,
		styles : [ {
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#f5f5f5"
			} ]
		}, {
			"elementType" : "labels.icon",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#616161"
			} ]
		}, {
			"elementType" : "labels.text.stroke",
			"stylers" : [ {
				"color" : "#f5f5f5"
			} ]
		}, {
			"featureType" : "administrative.land_parcel",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "administrative.land_parcel",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#bdbdbd"
			} ]
		}, {
			"featureType" : "administrative.neighborhood",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "poi",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#eeeeee"
			} ]
		}, {
			"featureType" : "poi",
			"elementType" : "labels.text",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "poi",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#757575"
			} ]
		}, {
			"featureType" : "poi.park",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#e5e5e5"
			} ]
		}, {
			"featureType" : "poi.park",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#9e9e9e"
			} ]
		}, {
			"featureType" : "road",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#ffffff"
			} ]
		}, {
			"featureType" : "road",
			"elementType" : "labels",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "road.arterial",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "road.arterial",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#757575"
			} ]
		}, {
			"featureType" : "road.highway",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#dadada"
			} ]
		}, {
			"featureType" : "road.highway",
			"elementType" : "labels",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "road.highway",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#616161"
			} ]
		}, {
			"featureType" : "road.local",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "road.local",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#9e9e9e"
			} ]
		}, {
			"featureType" : "transit.line",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#e5e5e5"
			} ]
		}, {
			"featureType" : "transit.station",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#eeeeee"
			} ]
		}, {
			"featureType" : "water",
			"elementType" : "geometry",
			"stylers" : [ {
				"color" : "#c9c9c9"
			} ]
		}, {
			"featureType" : "water",
			"elementType" : "labels.text",
			"stylers" : [ {
				"visibility" : "off"
			} ]
		}, {
			"featureType" : "water",
			"elementType" : "labels.text.fill",
			"stylers" : [ {
				"color" : "#9e9e9e"
			} ]
		} ]
	});
	
	var script = document.createElement("script");
	script.src = "https://rawgithub.com/googlemaps/js-map-label/gh-pages/src/maplabel-compiled.js";
	document.body.appendChild(script);
}
