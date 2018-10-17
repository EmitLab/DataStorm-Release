$(document).ready(function() {
	$(".input-daterange").datepicker({
		format : "mm/dd/yyyy",
		clearBtn : true,
		autoclose : true
	});

	$('.input-daterange').on('clearDate', function() {
		$("#startDate").datepicker('setDate', '+0d');
		$("#endDate").datepicker('setDate', '+1d');
		$(".input-daterange").datepicker('update');
	});

	$("#startDate").datepicker('setDate', '+0d');
	$("#endDate").datepicker('setDate', '+1d');
	$(".input-daterange").datepicker('update');

	// default values for start and end dates set to default
	// values of datepickers
	var startDate = convertToEpoch($("#startDate").datepicker('getDate'));
	var endDate = convertToEpoch($("#endDate").datepicker('getDate'));
	
	// global variable for currentFrame reference: default is
	// startDate epoch value
	var currentF = convertToEpoch($("#startDate").datepicker('getDate'));

	function initSlider() {
		$("#slider").slider('setAttribute', 'min', startDate);
		$("#slider").slider('setAttribute', 'max', endDate);
		$("#slider").slider('setAttribute', 'value', startDate);
		$("#slider").slider('refresh');
	}

	function convertToEpoch(input) {
		return (input.getTime() / 1000);
	}

	// Automatically updates slider min when starting date is
	// changed
	$("#startDate").on('changeDate', function() {
		startDate = convertToEpoch($("#startDate").datepicker('getDate'));
		
		initSlider();
//		if(!socketFlag)
//		{
//			setGrids();
//		}
	});
	
	// Automatically updates slider max when ending date is
	// changed
	$('#endDate').on('changeDate', function() {
		endDate = convertToEpoch($("#endDate").datepicker('getDate'));
		
		initSlider();
		//setGrids(); //commented this as it gets called in startdate on(change) event 
	});
	
	$("#slider").slider({
		min : startDate,
		max : endDate,
		value : startDate,
		step : 10800,
		formatter : function() {
			currentF = $("#slider").slider('getValue');
			var currentDate = new Date(currentF * 1000);
			return ((currentDate.getMonth() + 1) + "/" + currentDate.getDate() + "/" + currentDate.getFullYear()
				+ " Hour: " + currentDate.getHours());
		}
	});

	$("#slider").on('change', function() {
		setGrids();
	});
	
	$("#startSlider").on('click', function() {
		var value = $("#slider").slider('getValue') - 10800;
    	$("#slider").slider('setValue', value);
    	setGrids();
	});
	
	$("#endSlider").on('click', function() {
		var value = $("#slider").slider('getValue') + 10800;
    	$("#slider").slider('setValue', value);
    	setGrids();
	});
	
	//Arrow controls
	$(document).on('keydown', function(e) {
	    if(e.keyCode == 37) {
	    	var value = $("#slider").slider('getValue') - 10800;
	    	$("#slider").slider('setValue', value);
	    	setGrids();
	    }
	    if(e.keyCode == 39) {
	    	var value = $("#slider").slider('getValue') + 10800;
	    	$("#slider").slider('setValue', value);
	    	setGrids();
	    }
	});

	$("#slider").slider('refresh');

});

function setGrids() {
	generate(VISUALIZATION_JSON);
}
