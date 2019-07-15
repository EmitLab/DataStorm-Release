<%@page import="com.asu.ds.Sessions.Sessions"%>
<%@page import="com.asu.ds.seo.utils.SessionKey"%>
<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ page import="common.Constants"%>
<%@ page import="com.asu.ds.seo.utils.Seo" %>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Welcome to DataStorm</title>

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
<script src="./js/browser.js"></script>
</head>
<body>
	<nav id="nav" class="navbar navbar-expand-lg navbar-dark bg-dark">
		<div class="container">
			<div class="project-name" style="color: white !important;">
				<span class="fab fa-superpowers"></span>&nbsp;DataStorm-FE
			</div>
			<div class="collapse navbar-collapse" id="navbarSupportedContent">
				<ul class="navbar-nav mr-auto">
					<li class="nav-item active">&nbsp;</li>
				</ul>
			</div>
			<div class="text-white">
				&nbsp;
			</div>
		</div>
	</nav>
	<div class="jumbotron">
		<div class="container">
			<h1 class="display-4">Hello from DataStorm-FE!</h1>
			<p class="lead">
				 A Data- and Decision-Flow and Coordination Engine for Coupled Simulation Ensembles
			</p>
			<hr class="my-4">
			<p class="text-justify">
				Data- and model-driven computer simulations are increasingly critical in many application domains. Yet, several
critical data challenges remain in obtaining and leveraging simulations in decision making. Simulations may track
100s of parameters, spanning multiple layers and spatial and temporal frames, affected by complex inter-dependent dynamic processes. Moreover, due to the large numbers of
unknowns, decision makers usually need to generate ensembles of stochastic realizations, requiring 10s-1000s of individual simulation instances. The situation on the ground
evolves unpredictably, requiring continuously adaptive simulation ensembles. We introduce the DataStorm framework
for simulation ensemble management, and demonstrate its
DataStorm-FE data- and decision-flow and coordination engine for creating and maintaining coupled, multi-model simulation ensembles. DataStorm-FE enables end-to-end ensemble planning and optimization, including parameter-space
sampling, output aggregation and alignment, and state and
provenance data management, to improve the overall simulation process. It also aims to work efficiently, producing results while working within a limited simulation budget, and
incorporates a multivariate, spatio-temporal data browser to
empower decision-making based on these improved results.
			</p>
			<a class="btn btn-dark btn-lg" href="<%= Seo.getSeoPath(Seo.DASHBOARD, Seo.TYPE_FULL)%>">
				Continue to DataStorm-FE <span class=" fas fa-chevron-circle-right fa-fw"></span>
			</a>
		</div>
	</div>
	<div class="container">
		
		<div class="row">
			<div class="col">
			
			</div>
		</div>
	</div>
	<nav class="navbar fixed-bottom navbar-light bg-light text-dark">
		<div class="container">
			<div class="project-name">
				<span class="fab fa-superpowers"></span>&nbsp;DataStorm-FE
			</div>
			<div class="collapse navbar-collapse" id="navbarSupportedContent">
				<ul class="navbar-nav mr-auto">
					<li class="nav-item active">
						NSF Grant #<a href="https://www.nsf.gov/awardsearch/showAward?AWD_ID=1610282" target="_blank">1610282</a> 
					</li>
				</ul>
			</div>
			<div class="text-dark">
				<small>
					<em>
						NSF Grant <a href="https://www.nsf.gov/awardsearch/showAward?AWD_ID=1610282" target="_blank">#1610282</a> | Designed and Developed by EmitLab, Arizona State University	
					</em>
				</small>
			</div>
		</div>
	</nav>
	<script>
		isBrowser();
	</script>
</body>
</html>