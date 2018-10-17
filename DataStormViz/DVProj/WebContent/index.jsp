<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ page import="common.Constants"%>
<%@ page import="common.JSONFiles"%>

<!DOCTYPE html>
<html>
<head>
<title>DataStorm-Viz</title>
<meta name="viewport" content="initial-scale=1.0">
<meta charset="utf-8">

<link href="https://fonts.googleapis.com/css?family=Gugi"
	rel="stylesheet">
<link rel="stylesheet"
	href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css">
<link rel="stylesheet"
	href="https://use.fontawesome.com/releases/v5.2.0/css/all.css">
<link rel="stylesheet"
	href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/css/bootstrap-datepicker.min.css">
<link rel="stylesheet" href="css/main.css">
<link rel ="stylesheet"
	href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/10.0.2/css/bootstrap-slider.css"/>


<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/js/bootstrap-datepicker.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/10.0.2/bootstrap-slider.js"></script>
	
<script src="js/visualization.js"></script>
<script>
	$.getJSON(<%=JSONFiles.JSON_HUMAN_MOBILITY%>, function(json){
		humanMobilityJSON = json;
	});
	$.getJSON(<%=JSONFiles.JSON_NODE%>, function(json){
		nodeJSON = json;
	});
	$.getJSON(<%=JSONFiles.JSON_EDGE%>, function(json){
		edgeJSON = json;
	});
</script>

</head>
<body id="body">
	<nav id="nav" class="navbar navbar-expand-lg navbar-light bg-light">
	    <div class="project-name">
			<span class="fab fa-superpowers"></span>&nbsp;DataStorm&nbsp;Visualization
		</div>
	    <div class="collapse navbar-collapse" id="navbarSupportedContent">
	        <ul class="navbar-nav mr-auto">
	            <li class="nav-item active">
	                <a class="nav-link" href="./">
	                <span class="fas fa-map-marked-alt fa-fw"></span>&nbsp;
	                Map View </a>
	            </li>
	            <li class="nav-item">
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
	<div id="container" class="container h-90">
		<div class="row h-100">
			<div class="col-sm-8 h-100" style="padding-right: 0">
				<div id="map"></div>
			</div>
			<div id="sidebar" class="col-sm-4" style="overflow-y: scroll; padding-left: 0; padding-right: 0;max-height:90vh;">
				<ul class="nav nav-pills margin-bottom-15">
					<li class="active"><a class="h5 tab-link" href="#tab1" data-toggle="tab">
						<span class="fas fa-bars fa-fw"></span>
						&nbsp;Layers
					</a></li>
					<li><a class="h5 tab-link" href="#tab2" data-toggle="tab">
						<span class="fas fa-info-circle fa-fw"></span>
						&nbsp;Details
					</a></li>
				</ul>
				<div class="tab-content clearfix" style="padding-left: 15px; padding-right: 15px">
					<div class="tab-pane active" id="tab1">
						<div class="row">
							<div id="overlapSidebar" class="col-sm-12">
								<div class="row">
									<div class="col margin-bottom-15">
										<span class="fas fa-tint fa-fw"></span>
										<span class="data-layer-name">Rain</span>
										<div class="fas fa-toggle-off fa-fw text-default float-right"
											id="rain-toggle" onclick="toggleFilter('rain')"
											style="cursor: pointer;"></div>
									</div>
								</div>
								<div class="row">
									<div class="col margin-bottom-15">
										<span class="fas fa-ruler-vertical fa-fw"></span>
										<span class="data-layer-name">Flood</span>
										<div class="btn-group btn-sm" id="flood-control"
											style="display: none;">
											<div class="btn btn-outline-dark btn-sm" id="flood-control-down">
												<span class="fas fa-minus fa-fw" style="margin-top: 5px;"></span>
											</div>
											<div class="btn btn-dark btn-sm" id="flood-control-value">
												<span>25</span>
											</div>
											<div class="btn btn-outline-dark btn-sm" id="flood-control-up">
												<span class="fas fa-plus fa-fw" style="margin-top: 3px;"></span>
											</div>
										</div>
										<div class="fas fa-toggle-off fa-fw text-default float-right"
											id="flood-toggle" onclick="toggleFilter('flood')"
											style="cursor: pointer;"></div>
									</div>
								</div>
								<div class="row">
									<div class="col margin-bottom-15">
										<span class="far fa-compass fa-fw"></span> <span
											class="data-layer-name">Wind</span>
										<div class="fas fa-toggle-off fa-fw text-default float-right"
											id="wind-toggle" onclick="toggleFilter('wind')"
											style="cursor: pointer;"></div>
									</div>
								</div>
								<div class="row">
									<div class="col margin-bottom-15">
										<span class="fas fa-share-alt fa-fw"></span> <span
											class="data-layer-name">Human Mobility</span>
										<div class="fas fa-toggle-off fa-fw text-default float-right"
											id="human_mobility-toggle" onclick="toggleFilter('human_mobility')"
											style="cursor: pointer;"></div>
									</div>
								</div>
								<div class="row">
									<div class="col-sm-12">
										<div class="row">
											<div class="input-group input-daterange" id="datePicker">
												<div class="col-sm-12">
													<div class="row">
														<div class="col-sm-6">
															<span class="far fa-calendar-alt fa-fw"></span>
															<span class="data-layer-name">Start Date</span>
														</div>
														<div class="col-sm-6">
															<input type="text" class="form-control" id="startDate" style="float: right" readonly>
															<div class="input-group-addon">
																<span class="glyphicon glyphicon-calendar" id="startCalendar"></span>
															</div>
														</div>
													</div>
												</div>
												<div class="col-sm-12">
													<div class="row">
														<div class="col-sm-6">
															<span class="far fa-calendar-alt fa-fw"></span>
															<span class="data-layer-name">End Date</span>
														</div>
														<div class="col-sm-6">
															<input type="text" class="form-control" id="endDate" readonly>
															<div class="input-group-addon">
																<span class="glyphicon glyphicon-calendar" id="startCalendar"></span>
															</div>
														</div>
													</div>
												</div>
											</div>
											<div class="col-sm-12" style="padding-top: 32px; text-align: center;">
												<div id="startSlider" style="float: left;">
													<span class="far fa-clock fa-fw"></span>
													<span>Start</span>
												</div>
												<input id="slider" style="width: 180px;"/>
												<div id="endSlider" style="float: right;">
													<span class="far fa-clock fa-fw"></span>
													<span>End</span>
												</div>
											</div>
											
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
					<div class="tab-pane" id="tab2">
						<div class="row">
							<div id="info-graphics" class="col-sm-12" style="display: none;">
								<div class="row margin-bottom-15" id="location-info-graphics">
									<div class="col">
										<div class="float-left">Geographic Location</div>
										<div class="float-right">
											<div id="location-value" class="btn btn-sm btn-outline-dark">00.00, -00.00</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="hurricane-info-graphics">
									<div class="col">
										<div class="custom-control custom-checkbox">
										  <input type="checkbox" class="custom-control-input" id="hurricane-checkbox" checked>
										  <label class="custom-control-label" for="hurricane-checkbox">Hurricane</label>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="rain-value-info-graphics">
									<div class="col">
										<div class="float-left">Rain Value (cm)</div>
										<div class="float-right">
											<div class="btn-group">
												<div id="rain-value" class="btn btn-sm btn-outline-dark">0.00</div>
												<div id="rain-color" class="btn btn-sm">&nbsp;</div>
											</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="rain-legend-info-graphics">
									<div class="col">
										<div class="float-left">Rain Legend</div>
										<div class="float-right">
											<canvas id="rain-legend-value" class="legend-value" data-toggle="tooltop" data-placement="top" title="Legend"></canvas>
										</div>
									</div>
								</div>
								<!-- <div class="row margin-bottom-15" id="wind-info-graphics">
									<div class="col">
										<div class="custom-control custom-checkbox">
										  <input type="checkbox" class="custom-control-input" id="wind-checkbox" checked>
										  <label class="custom-control-label" for="wind-checkbox">Wind</label>
										</div>
									</div>
								</div> -->
								<div class="row margin-bottom-15" id="wind-directed-info-graphics">
									<div class="col">
										<div class="float-left">Wind - Directed (m/sec)</div>
										<div class="float-right">
											<div class="btn-group">
												<div id="wind-value" class="btn btn-sm btn-outline-dark">0.00</div>
											</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="wind-u-info-graphics">
									<div class="col">
										<div class="float-left">U Wind - Directed (m/sec)</div>
										<div class="float-right">
											<div class="btn-group">
												<div id="u-wind-value" class="btn btn-sm btn-outline-dark">0.00</div>
											</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="wind-v-info-graphics">
									<div class="col">
										<div class="float-left">V Wind - Directed (m/sec)</div>
										<div class="float-right">
											<div class="btn-group">
												<div id="v-wind-value" class="btn btn-sm btn-outline-dark">0.00</div>
											</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="wind-legend-info-graphics">
									<div class="col margin-bottom-15">
										<div class="float-left">Wind Legend</div>
										<div class="float-right">
											<canvas id="wind-legend-value" class="legend-value" data-toggle="tooltop" data-placement="top" title="Legend"></canvas>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="flood-info-graphics">
									<div class="col">
										<div class="custom-control custom-checkbox">
										  <input type="checkbox" class="custom-control-input" id="flood-checkbox" checked>
										  <label class="custom-control-label" for="flood-checkbox">Flood</label>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="flood-value-info-graphics">
									<div class="col">
										<div class="float-left">Flood Depth (cm)</div>
										<div class="float-right">
											<div class="btn-group">
												<div id="flood-value" class="btn btn-sm btn-outline-dark">0.00</div>
												<div id="flood-color" class="btn btn-sm">&nbsp;</div>
											</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="flood-legend-info-graphics">
									<div class="col margin-bottom-15">
										<div class="float-left">Flood Legend</div>
										<div class="float-right">
											<canvas id="flood-legend-value" class="legend-value" data-toggle="tooltop" data-placement="top" title="Legend"></canvas>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="human-mobility-info-graphics">
									<div class="col">
										<div class="custom-control custom-checkbox">
										  <input type="checkbox" class="custom-control-input" id="human-mobility-checkbox" checked>
										  <label class="custom-control-label" for="human-mobility-checkbox">Human Mobility</label>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="human-mobility-value-info-graphics">
									<div class="col">
										<div class="float-left">Count</div>
										<div class="float-right">
											<div class="btn-group">
												<div id="human-mobility-value" class="btn btn-sm btn-outline-dark">0</div>
											</div>
										</div>
									</div>
								</div>
								<div class="row margin-bottom-15" id="human-mobility-legend-info-graphics">
									<div class="col margin-bottom-15">
										<div class="float-left">Human Mobility Legend</div>
										<div class="float-right">
											<canvas id="human-mobility-legend-value" class="legend-value" data-toggle="tooltop" data-placement="top" title="Legend"></canvas>
										</div>
									</div>
								</div>
								<button type="button" class="btn btn-primary" id="btn_explain">Explain&nbsp;<span style="color:white !important;" class="fas fa-link fa-fw"></span></button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
	
	<script>
		$(".tab-link").on("click", function() {
			$(".tab-link").parent().css("background-color", "#c9c9c9");
			$(this).parent().css("background-color", $("#sidebar").css("background-color"));
		});
		
		$("#btn_explain").on("click", function() {
			for(var i in EXPLANATIONS) {
				EXPLANATIONS[i]();
			}
		});
		
		$(".legend-value").each(function(index) {
			var canvas = $(this).get(0);
			//temporary until legends auto generate
			if(index == 0) generateLegend(["green"], canvas);
			if(index == 2) generateLegend(["#000DBF", "#1A00C3", "#4400C7", "#6F00CB", "#9C00CF", "#CB00D4", "#D800B4", "#DC008A",
                "#E0005F", "#E50031"], canvas);
			if(index == 1) generateLegend(["red"], canvas);
			if(index == 3) generateLegend(["orange"], canvas);
		});
		$("#rain-color").css("background-color", "green").css("opacity", 0.4);
		$("#flood-color").css("background-color", "#000DBF").css("opacity", 0.4);
		
		function generateLegend(array, canvas) {
	        canvas.width = 100;
	        canvas.height = 20;
	        var context = canvas.getContext("2d");
	        var width = canvas.width / array.length;
	        context.fillStyle = "#c9c9c9";
        	context.globalAlpha = 1.0;
        	context.fillRect(0, 0, canvas.width, canvas.height);
	        for(var i = 0; i < array.length; i++) {
	            context.fillStyle = array[i];
	            context.globalAlpha = 0.4;
	            context.fillRect(i * width, 0, width, canvas.height);
	        }
	    }
	</script>
	<script src="js/ajaxCalls.js"></script> <!-- For Ajax calls to Servlet that fetches results from mongo -->
	<script src="js/calendar.js"></script>
	<script src="js/socket.js"></script>
	<script src="js/map.js"></script>
	<script src="https://maps.googleapis.com/maps/api/js?key=<%=Constants.GOOGLE_MAPS_KEY%>&callback=initMap" async defer></script>
</body>
</html>
