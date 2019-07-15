$(document).ready(function() {
	$("#startDate").datepicker({
		format : "mm/dd/yy",
		clearBtn : true,
		autoclose : true
	});
	$("#endDate").datepicker({
		format : "mm/dd/yy",
		clearBtn : true,
		autoclose : true
	});

	$('#startDate').on('clearDate', function() {
		$("#startDate").datepicker('setDate', '+0d');
		$("#endDate").datepicker('setDate', '+1d');
		$("#startDate").datepicker('update');
		$("#endDate").datepicker('update');
	});
	
	$('#endDate').on('clearDate', function() {
		$("#startDate").datepicker('setDate', '+0d');
		$("#endDate").datepicker('setDate', '+1d');
		$("#startDate").datepicker('update');
		$("#endDate").datepicker('update');
	});
	
	$("#startDate").datepicker('setDate', '+0d');
	$("#endDate").datepicker('setDate', '+1d');
	$("#startDate").datepicker('update');
	$("#endDate").datepicker('update');

	// default values for start and end dates set to default
	// values of datepickers
	var startDate = convertToEpoch($("#startDate").datepicker('getDate'));
	var endDate = convertToEpoch($("#endDate").datepicker('getDate'));
	
	$("#slider").slider({
		min: startDate,
		max: endDate,
		value: startDate,
		step: 10800,
		formatter: function() {
			var currentDate = new Date($("#slider").slider('getValue') * 1000);
			return ((currentDate.getMonth() + 1) + "/" + currentDate.getDate() + "/" + currentDate.getFullYear()
				+ " Hour: " + currentDate.getHours());
		}
	});
	
	// global variable for currentFrame reference: default is
	// startDate epoch value
	var currentF = convertToEpoch($("#startDate").datepicker('getDate'));

	function initSlider() {
		$("#slider").slider('setAttribute', 'min', startDate);
		$("#slider").slider('setAttribute', 'max', endDate);
		
		var timestamp = $("#slider").slider('getValue');
		if(timestamp < startDate || timestamp >= endDate) {
			$("#slider").slider('setAttribute', 'value', startDate);
			$("#slider").slider('refresh');
			setUrlParam('timestamp', startDate);
		}
		
		setUrlParam('start-date', startDate);
		setUrlParam('end-date', endDate);
	}

	function convertToEpoch(input) {
		return (input.getTime() / 1000);
	}

	// Automatically updates slider min when starting date is
	// changed
	$("#startDate").on('changeDate', function() {
		startDate = convertToEpoch($("#startDate").datepicker('getDate'));
		if(startDate > endDate) {
			var date = $("#startDate").datepicker('getDate');
			date.setDate(date.getDate() + 1);
			$("#endDate").datepicker('setDate', date);
			endDate = convertToEpoch($("#endDate").datepicker('getDate'));
		}
		initSlider();
	});
	
	// Automatically updates slider max when ending date is
	// changed
	$('#endDate').on('changeDate', function() {
		endDate = convertToEpoch($("#endDate").datepicker('getDate'));
		if(startDate > endDate) {
			var date = $("#endDate").datepicker('getDate');
			date.setDate(date.getDate() - 1);
			$("#startDate").datepicker('setDate', date);
			startDate = convertToEpoch($("#startDate").datepicker('getDate'));
		}
		initSlider();
	});

	$("#slider").on('change', function() {
		
		var value = $("#slider").slider('getValue');
		setGrids();
		
		setUrlParam('timestamp', value);
	});
	
	$("#startSlider").on('click', function() {
		var value = $("#slider").slider('getValue') - 10800;
    	$("#slider").slider('setValue', value);
    	setGrids();
    	
    	setUrlParam('timestamp', value);
	});
	
	$("#endSlider").on('click', function() {
		var value = $("#slider").slider('getValue') + 10800;
    	$("#slider").slider('setValue', value);
    	setGrids();
    	
    	setUrlParam('timestamp', value);
	});
	
	//Arrow controls
	$(document).on('keydown', function(e) {
	    if(e.keyCode == 37) {
	    	var value = $("#slider").slider('getValue') - 10800;
	    	$("#slider").slider('setValue', value);
	    	setGrids();
	    	
	    	setUrlParam('timestamp', value);
	    }
	    if(e.keyCode == 39) {
	    	var value = $("#slider").slider('getValue') + 10800;
	    	$("#slider").slider('setValue', value);
	    	setGrids();
	    	
	    	setUrlParam('timestamp', value);
	    }
	});

	$("#slider").slider('refresh');

});

function setGrids() {
	generate(VISUALIZATION_JSON);
}
