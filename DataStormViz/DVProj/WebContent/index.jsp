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

</head>
<body>
	<script>
		window.location.href = "<%= Seo.getSeoPath(Seo.WELCOME, Seo.TYPE_FULL)%>";
	</script>
</body>
</html>