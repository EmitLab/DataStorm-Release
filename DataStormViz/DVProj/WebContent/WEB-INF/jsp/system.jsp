<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ page import="common.Constants"%>
<%@ page import="common.JSONFiles"%>
<%@ page import="com.mongodb.*" %>
<%@ page import= "com.jcraft.jsch.JSch" %>
<%@ page import = "com.jcraft.jsch.Session"%>
<%@ page import= "java.io.File"%>
<%@ page import= "java.io.IOException"%>
<%@ page import= "com.jcraft.jsch.JSchException"%>
<%@ page import="com.asu.ds.seo.*"%>
<%@ page import="com.asu.ds.seo.utils.*"%>
<%@ page import="com.asu.ds.controller.LoginController" %>
<%

	LoginController loginController = new LoginController();
	Boolean flag = loginController.isLoggedIn(request, response);
	
	if (! flag) {
		System.out.println(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL));
		Seo.sendRedirect(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL), response);
	} else {


%>
<!DOCTYPE html>
<html>
<head>
<title>DataStorm-FE</title>
<meta name="viewport" content="initial-scale=1.0">
<meta charset="utf-8">

<link href="https://fonts.googleapis.com/css?family=Gugi"
	rel="stylesheet">
<link rel="stylesheet"
	href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">
<link rel="stylesheet"
	href="https://use.fontawesome.com/releases/v5.2.0/css/all.css">
<link rel="stylesheet"
	href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.8.0/css/bootstrap-datepicker.min.css">
<link rel="stylesheet" href="css/main.css">
<link rel ="stylesheet"
	href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/10.0.2/css/bootstrap-slider.css"/>


<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>
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
<script>

</script>

</head>
<body id="body">
	<nav id="nav" class="navbar navbar-expand-lg navbar-light bg-light">
	    <div class="project-name">
			<span class="fab fa-superpowers"></span>&nbsp;DataStorm&nbsp;FE
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
	             <li class="nav-item">
	               <div onclick=""><a href="" class="nav-link" data-toggle="modal" data-target="#modalLoginForm">
	                <span class="far fa-save"></span>&nbsp;
	                Save </a></div> 
	            </li>
					
	             <li class="nav-item">
	               <div onclick=""><a class="nav-link"  href="<%= Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_JSP)%>">
	                <span class="fas fa-sign-out-alt"></span>&nbsp;
	                Log out </a></div> 
	            </li>
	        </ul>
	    </div>
	    <div>
		    <div class="fas fa-toggle-off fa-fw text-default float-right fa-2x" 
		    	id="config-toggle" onclick="toggleConfigState()" style="cursor: pointer;"></div>
	    </div>
	</nav>
<div class="modal fade" id="modalLoginForm" tabindex="-1" role="dialog" aria-labelledby="myModalLabel"
  aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header text-center">
        <h4 class="modal-title w-100 font-weight-bold">Save Configuration</h4>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body mx-3">
        <div class="md-form mb-5">
          <input type="email" id="defaultForm-email" class="form-control validate">
          <label data-success="right" for="defaultForm-email">Date</label>
        </div>

        <div class="md-form mb-4">
          <input type="text" id="defaultForm-name" class="form-control validate">
          <label data-success="right" for="defaultForm-pass">Configuration Name</label>
        </div>

      </div>
      <div class="modal-footer d-flex justify-content-center">
        <button class="btn btn-default">Save</button>
      </div>
    </div>
  </div>
</div>


	<div id="container" class="container h-90">
		<div class="row layers" style="height: 7.5% !important; max-height: 45px !important;">
			<div class="col-sm-2">
				<span class="fas fa-th-list fa-fw"></span>
				<span>Instance</span>
				<div class="button-group float-right">
					<button type="button" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown"><span class="glyphicon glyphicon-cog"></span> <span class="caret"></span></button>
					<ul id="instance-dropdown" class="dropdown-menu dropdown-menu-right">
						<li class="col">
							<div class="custom-control custom-checkbox">
								<input type="checkbox" class="custom-control-input instance-checkbox" id="instance-1" checked>
								<label class="custom-control-label" for="instance-1">Instance 1</label>
							</div>
						</li>
						<li class="col">
							<div class="custom-control custom-checkbox">
								<input type="checkbox" class="custom-control-input instance-checkbox" id="instance-2">
								<label class="custom-control-label" for="instance-2">Instance 2</label>
							</div>
						</li>
						<li class="col">
							<div class="custom-control custom-checkbox">
								<input type="checkbox" class="custom-control-input instance-checkbox" id="instance-3">
								<label class="custom-control-label" for="instance-3">Instance 3</label>
							</div>
						</li>
						<li class="col">
							<div class="custom-control custom-checkbox">
								<input type="checkbox" class="custom-control-input instance-checkbox" id="aggregate">
								<label class="custom-control-label" for="aggregate">Aggregate</label>
							</div>
						</li>
					</ul>
				</div>
			</div>
			<div class="col-sm-2 col-dark">
				<span class="fas fa-th-list fa-fw"></span>
				<span>Filters</span>
				<div class="button-group float-right">
					<button type="button" class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown"><span class="glyphicon glyphicon-cog"></span> <span class="caret"></span></button>
					<ul class="dropdown-menu dropdown-menu-right">
						<li class="col">
							<span class="fas fa-tint fa-fw"></span>
							<span>Rain</span>
							<div class="fas fa-toggle-off fa-fw text-default float-right"
								id="rain-toggle" onclick="toggleFilter('rain')"
								style="cursor: pointer;"></div>
						</li>
						<li class="col">
							<span class="fas fa-ruler-vertical fa-fw"></span>
							<span>Flood</span>
							<div class="fas fa-toggle-off fa-fw text-default float-right"
								id="flood-toggle" onclick="toggleFilter('flood')"
								style="cursor: pointer;"></div>
						</li>
						<li class="col">
							<span class="far fa-compass fa-fw"></span>
							<span>Wind</span>
							<div class="fas fa-toggle-off fa-fw text-default float-right"
								id="wind-toggle" onclick="toggleFilter('wind')"
								style="cursor: pointer;"></div>
						</li>
						<li class="col">
							<span class="fas fa-share-alt fa-fw"></span>
							<span>Mobility</span>
							<div class="fas fa-toggle-off fa-fw text-default float-right"
								id="human_mobility-toggle" onclick="toggleFilter('human_mobility')"
								style="cursor: pointer;"></div>
						</li>
					</ul>
				</div>
			</div>
			<div class="col-sm-2">
				<span class="far fa-calendar-alt fa-fw"></span>
				<span>Start</span>
				<input type="text" class="form-control" id="startDate" style="float: right; max-width: 60%; max-height: 30px;" readonly>
			</div>
			<div class="col-sm-2 col-dark">
				<span class="far fa-calendar-alt fa-fw"></span>
				<span>End</span>
				<input type="text" class="form-control" id="endDate" style="float: right; max-width: 60%; max-height: 30px;" readonly>
			</div>
			<div class="col-sm-4" style="text-align: center;">
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
		<div class="row" style="height: 92.5% !important">
			<div id="map" class="col-sm-12">
				<div id="map-container" class="row h-100"></div>
			</div>
			<div id="sidebar" style="display: none; overflow-y: scroll; padding-left: 0; padding-right: 0;max-height:90vh;">
				<div>
					<ul class="nav nav-pills margin-bottom-15">
						<li class="active" style="float: left;">
							<a class="h5 tab-link" href="#tab1" data-toggle="tab">
								<span class="fas fa-info-circle fa-fw"></span>
								&nbsp;Details
							</a>
						</li>
						<button id="btn-close" type="button" class="close" aria-label="Close" style="float: right;">
							<span aria-hidden="true">&times;</span>
						</button>
					</ul>
				</div>
				<div class="tab-content clearfix" style="padding-left: 15px; padding-right: 15px">
					<div class="tab-pane active" id="tab1">
						<div class="row">
							<div id="info-graphics" class="col-sm-12" style="display: none;">
								<div class="row margin-bottom-15" id="location-info-graphics">
									<div class="col">
										<div class="float-left">Instance</div>
										<div class="float-right">
											<div id="instance-value" class="btn btn-sm btn-outline-dark"></div>
										</div>
									</div>
								</div>
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
		
		$('.dropdown-menu li').click(function(e) {
		    e.stopPropagation();
		});
		
		$('#instance-dropdown li').click(function(e) {
		    if(e.target.nodeName == "INPUT") {
		    	var list = [];
		    	$('.instance-checkbox').each(function(i, element) {
		    		if(element.checked && list.length < 4) {
		    			list.push(element.id);
		    		}
		    	});
		    	createMaps(list);
		    }
		});
		
		$('#btn-close').on("click", function() {
			$('#map').removeClass('col-sm-8');
			$('#sidebar').removeClass('col-sm-4');
			$('#map').addClass('col-sm-12');
			$('#sidebar').css('display', 'none');
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
	
	<script src="js/calendar.js"></script>
	<script src="js/url.js"></script>
	<script src="js/config.js"></script>
	<script src="js/filter.js"></script>
	<script src="js/socket.js"></script>
	
	<script src="js/map.js"></script>
	<script src="https://maps.googleapis.com/maps/api/js?key=<%=Constants.GOOGLE_MAPS_KEY%>&callback=initMap" async defer></script>
</body>
</html>
<% } %>
