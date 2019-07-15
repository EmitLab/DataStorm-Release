<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ page import="common.Constants"%>
<%@ page import="com.asu.ds.seo.utils.Seo" %>
<%@ page import="com.asu.ds.Sessions.*" %>
<%@ page import="com.asu.ds.seo.utils.*" %>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Dashboard | Welcome to DataStorm</title>

<!-- LOADING CSS FILES -->
<link href="https://fonts.googleapis.com/css?family=Gugi"
	rel="stylesheet">
<link rel="stylesheet"
	href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css">
<link rel="stylesheet"
	href="https://use.fontawesome.com/releases/v5.2.0/css/all.css">
<link rel="stylesheet" href="./css/main.css">
<link rel="stylesheet"
	href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/10.0.2/css/bootstrap-slider.css" />

<!-- LOAD JavaScript Files -->
<script
	src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
<script
	src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.0/umd/popper.min.js"></script>
<script
	src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"></script>
<script
	src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-slider/10.0.2/bootstrap-slider.js"></script>

</head>
<body>
	<nav id="nav" class="navbar navbar-expand-lg navbar-dark bg-dark">
		<div class="container">
			<div class="project-name" style="color: white !important;">
				<span class="fab fa-superpowers"></span>&nbsp;DataStorm-FE
			</div>
			<div class="collapse navbar-collapse" id="navbarSupportedContent">
				<ul class="navbar-nav mr-auto text-white">
					<li class="nav-item active">
						Welcome <span><%=session.getAttribute(Sessions.SES_USER_FNAME) %>,</span>
					</li>
				</ul>
			</div>
			<div class="text-white">
				<div class="dropdown">
					<button class="btn btn-dark btn-sm dropdown-toggle" type="button"
						id="dropdownMenuButton" data-toggle="dropdown"
						aria-haspopup="true" aria-expanded="false">
						<span class="fas fa-cogs fa-fw"></span>
					</button>
					<div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdownMenuButton">
						<a class="dropdown-item" href="#">
							<span class="fas fa-id-badge fa-fw"></span> My Profile</a>
						<div class="dropdown-divider"></div>
						<a class="dropdown-item" href="<%= Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + SessionKey.LOGIN_MODE + "=" + SessionKey.LOGIN_MODE_LOGOUT%>">
							<span class="fas fa-lock fa-fw"></span> Logout
						</a>
					</div>
				</div>
			</div>
		</div>
	</nav>
	<div class="container">
		<div class="row">
			<div class="col">
				<br />
			</div>
		</div>
		<div class="row">
			<div class="col">
				<!-- CARD COLUMN STARTS -->
				<div class="card-columns">
					<!-- DS-Store CARD STARTS -->
					<div class="card bg-danger text-white">
						<h5 class="card-header">
							DS-Store <span class="fas fa-database float-right"></span>
						</h5>
						<div class="card-body">
							<p class="card-text">Scalable data storage engine for storing
								spatio-temporal unstructured data generated through continuous
								simulations.</p>
						</div>

						<div class="card-footer">
							<a href="<%=Seo.getSeoPath(Seo.STORE, Seo.TYPE_FULL)%>"
								class="btn btn-light btn-block"> Manage your data <span
								class="fas fa-angle-right"></span>
							</a>
						</div>
					</div>
					<!-- DS-Store CARD ENDS -->
					<!-- DS-Visualization CARD STARTS -->
					<div class="card bg-success text-white">
						<h5 class="card-header">
							DS-Visualization <span class="fas fa-map-marked-alt float-right"></span>
						</h5>
						<div class="card-body">

							<p class="card-text">Continuous spatio-temporal visualization engine</p>
						</div>

						<div class="card-footer">
							<a href="<%=Seo.getSeoPath(Seo.SYSTEM, Seo.TYPE_FULL)%>"
								class="btn btn-light btn-block"> Visualize data <span
								class="fas fa-angle-right"></span>
							</a>
						</div>
					</div>
					<!-- DS-Visualization CARD ENDS -->
					<!-- DS-Simulator CARD STARTS -->
					<div class="card bg-primary text-white">
						<h5 class="card-header">
							DS-Simulator <span class=" fas fa-draw-polygon float-right"></span>
						</h5>
						<div class="card-body">

							<p class="card-text">Run continuous coupled simulation
								workflow with DataStorm (DS)</p>
						</div>
						<div class="card-footer">
							<input id="ds-simulator-ip" class="form-control text-dark"
								type="text" value="129.114.110.164"
								style="margin-bottom: 10px; display: none;" />
							<div onclick=call_simulator(); class="btn btn-light btn-block">
								Run my workflow <span class="fas fa-angle-right"></span>
							</div>
						</div>
					</div>
					<br />
					<div class="card border-primary" id="ds-simulator-status-tab"
						style="display: none;">
						<h5 class="card-header">
							Simulation Status <span class=" fas fa-tasks float-right"></span>
						</h5>
						<!-- 
						<div class="card-body">
							
							<p class="card-text">Run continuous coupled simulation workflow with DataStorm (DS)</p>
						</div>
						-->
						<div class="card-footer">
							<div onclick=stop_simulator();
								class="btn btn-warning btn-block text-left"
								id="ds-simulator-status-button">Simulation running</div>
						</div>
					</div>
					<!-- DS-Simulator CARD ENDS -->
					<!-- DS Open Source CARD STARTS -->
					<div class="card bg-warning text-white">
						<h5 class="card-header">
							Open-Source <span class="fas fa-code float-right"></span>
						</h5>
						<div class="card-body">
							<p class="card-text">Access the DataStorm codebase and setup
								your own instance.</p>
						</div>

						<div class="card-footer">
							<a href="https://github.com/EmitLab/DataStorm-Release"
								class="btn btn-light btn-block"> Take me to source <span
								class="fas fa-angle-right"></span>
							</a>
						</div>
					</div>
					<!-- DS Open Source CARD ENDS -->
				</div>
				<!-- CARD COLUMN ENDS -->
			</div>
		</div>
	</div>
	<script>
		var sim_ajax;
		function call_simulator(){
			var target_url =  "<%= Seo.getSeoPath(Seo.SIMULATOR, Seo.TYPE_FULL) %>"; // "?ip=" + $('#ds-simulator-ip').val();
			console.log(target_url);
			sim_ajax = $.ajax({
							type: "POST",
							url: target_url,
							beforeSend: function() {
								$("#ds-simulator-status-tab").css("display", "block");
							},
							success : function() {
								console.log("Ran successfully.");
							},
							error : function() {
								console.log("Ran interestingly.");
							},
							complete : function() {
								$("#ds-simulator-status-button").removeClass("btn-warning").addClass("btn-success").text("Simulation finished");
							}
						});
			
		}
		
		function stop_simulator(){
			sim_ajax.abort();
		}
	</script>
</body>
</html>