<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<%@ page import="common.Constants"%>
<%@ page import="com.asu.ds.seo.utils.*" %>
<%@ page import="com.asu.ds.Sessions.Sessions" %>

<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Login | Welcome to DataStorm</title>

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
				<ul class="navbar-nav mr-auto">
					<li class="nav-item active">&nbsp;</li>
				</ul>
			</div>
			<div>&nbsp;</div>
		</div>
	</nav>
	<div class="container">
		<div class="row">
			<div class="col">
				<br />
			</div>
		</div>
		<div class="row">
			<div class="col-lg-3 col-md-2 col-sm-12">&nbsp;</div>
			<div class="col-lg-6 col-md-8 col-sm-12">
				<div id="accordion">
					<div class="card bg-light">
						<div class="card-header" id="headingLogin" data-toggle="collapse"
									data-target="#collapseLogin" aria-expanded="true"
									aria-controls="collapseLogin">
							<h5 class="mb-0">
								<button class="btn btn-link text-dark">
									<strong>Login</strong>
								</button>
								 <span class=" fas fa-sign-in-alt float-right"></span>
							</h5>
						</div>
						
						<div id="collapseLogin" class="collapse"
							aria-labelledby="headingLogin" data-parent="#accordion">
							<div class="card-body">
								<%
									String login_url = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + SessionKey.LOGIN_MODE + "=" + SessionKey.LOGIN_MODE_LOGIN;
								%>
								<form id="login-form" action="<%=login_url %>" method="POST">
									<div class="form-group">
										<label>Email (Username)</label>
										<input type="text" class="form-control" placeholder="Email (Username)" id="login-email" autocomplete="off" name="login-email"/>
									</div>
									<div class="form-group">
										<label>Password</label>
										<input type="password" class="form-control" placeholder="Password" id="login-password" autocomplete="off" name="login-password"/>
									</div>
									<div>
										<div class="text-muted">
											<small style="cursor:pointer;">
												<span id="login-reset-password" data-toggle="modal" data-target="#login-reset-password-modal">
													Forgot password, lets reset it.
												</span>
											</small>
										</div>
										<button type="submit" class="btn btn-success float-right">
											Continue <div class="fas fa-caret-right"></div>
										</button>
										<br/>
									</div>
								</form><br/>
							</div>
							<div class="card-footer" style="display:none;"></div>
						</div>
					</div>
					<div class="card bg-light">
						<div class="card-header" id="headingRegister" data-toggle="collapse"
									data-target="#collapseRegister" aria-expanded="false"
									aria-controls="collapseRegister">
							<h5 class="mb-0">
								<button class="btn btn-link collapsed text-dark">
									<strong>Create your DS-Account</strong>
								</button>
								  <span class="fas fa-user-plus float-right"></span>
							</h5>
						</div>
						<div id="collapseRegister" class="collapse"
							aria-labelledby="headingRegister" data-parent="#accordion">
							<div class="card-body">
								<%
									String register_url = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + SessionKey.LOGIN_MODE + "=" + SessionKey.LOGIN_MODE_REGISTER;
								%>
								<form id="register-form" action="<%=register_url %>" method="POST">
									<div class="form-group">
										<label>Name</label>
										<div class="form-inline">
											<input type="text" class="form-control col-lg-6 col-md-12 col-sm-12" placeholder="First Name" id="register-first-name" name="register-first-name" autocomplete="off"/>
											<input type="text" class="form-control col-lg-6 col-md-12 col-sm-12" placeholder="Last Name" id="register-last-name" name="register-last-name" autocomplete="off"/>
										</div>
									</div>
									<div class="form-group">
										<label>Email (<em>Username</em>)</label>
										<input type="text" class="form-control" placeholder="Email (Username)" id="register-email" name="register-email" autocomplete="off"/>
									</div>
									<div class="form-group">
										<label>Password</label>
										<input type="password" class="form-control" placeholder="Password" id="register-password" name="register-password" autocomplete="off"/>
									</div>
									<div class="form-group">
										<label>Retype Password</label>
										<input type="password" class="form-control" placeholder="Retype Password" id="register-re-password" name="register-re-password" autocomplete="off"/>
									</div>
									<div>
										<div class="text-muted">
											<small>* All fields are required.</small>
										</div>
										<button type="submit" class="btn btn-primary float-right">
											Continue to DS-Account <div class="fas fa-caret-right"></div>
										</button>
										<br/>
									</div>
								</form>
								<br/>
							</div>
							<div class="card-footer" style="display:none;"></div>
						</div>
					</div>
				</div>
			</div>
			<div class="col-lg-3 col-md-2 col-sm-12">&nbsp;</div>
		</div>
		<div class="row">
			<div class="col-lg-3 col-md-2 col-sm-12">&nbsp;</div>
			<div class="col-lg-6 col-md-8 col-sm-12">
				<br/>
				<%
					String error = Seo.getRequestVariable(request, Sessions.SES_USER_LOGIN_FLAG);
					if (error != null && error.equals(Sessions.SES_FLAG_TRUE)){
				%>
				<div class="alert alert-<%=Seo.getRequestVariable(request, Sessions.SES_USER_LOGIN_FLAG_DEG) %>" role="alert"
					style="margin-bottom: 0px;" id="login-error-block">
					<button type="button" class="close" data-dismiss="alert">×</button>
					<span class="fa fa-exclamation-circle fa-fw" style="margin-right:10px;"></span>
					<%=Seo.getRequestVariable(request, Sessions.SES_USER_LOGIN_FLAG_MSG)%>
				</div>
				<%
					} else {
				%>
					<script>
					$('#login-rror-block').hide();
					</script>
				<%		
					}
				%>
			</div>
			<div class="col-lg-3 col-md-2 col-sm-12">&nbsp;</div>
		</div>
		<%
			String f_pwd_url = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + SessionKey.LOGIN_MODE + "=" + SessionKey.LOGIN_MODE_RESET_PASSWORD;
		%>
		<div class="modal" role="dialog" id="login-reset-password-modal">
			<div class="modal-dialog" role="document">
				<div class="modal-content">
					<div class="modal-header">
						<h5 class="modal-title"><span class="fas fa-cogs fa-fw"></span> Reset Password</h5>
						
						<button type="button" class="close" data-dismiss="modal"
							aria-label="Close">
							<span aria-hidden="true">&times;</span>
						</button>
					</div>
					<div class="modal-body">
						<form id="login-reset-password-form" action="<%=f_pwd_url %>" method="POST">
							<div class="form-group">
								<label>Lets Identify Your Account</label>
								<input type="text" class="form-control" placeholder="Email (Username)" id="login-reset-password-email" autocomplete="off" name="login-reset-password-email"/>
							</div>
							<div class="form-group">
								<label>New Password</label>
								<div class="form-inline">
									<input type="text" class="form-control col-lg-6 col-md-12 col-sm-12" 
													   placeholder="Password" 
													   id="login-reset-password-password" 
													   name="login-reset-password-password" 
													   autocomplete="off"/>
									<input type="text" class="form-control col-lg-6 col-md-12 col-sm-12" 
													   placeholder="Retype Password" 
													   id="login-reset-password-re-password" 
													   name="login-reset-password-re-password" 
													   autocomplete="off"/>
								</div>
							</div>
							<div>
								<div class="text-muted">
									<small>
										<span>*All fields are required.</span>
									</small>
								</div>
								<button type="submit" class="btn btn-warning float-right">
									Reset <div class="fas fa-caret-right"></div>
								</button>
							</div>
						</form>
					</div>
				</div>
			</div>
			
		</div>
	</div>
	<script>
	<%
		String accordion = Seo.getRequestVariable(request, Sessions.SES_USER_LOGIN_ACCORDIAN);
		if (accordion == null || accordion.equals(Sessions.SES_USER_LOGIN_ACCORDIAN_LOGIN)){
	%>
		$("#collapseLogin").addClass("show");
	<%
		} else { 
	%>
		$("#collapseRegister").addClass("show");	
	<%
		} 
	%>
	</script>
	<script>
		$(document).ready(function(){
			/*
			$("#login-forgot-password").on('click', function(){
				
			});
			*/
		});
	</script>
</body>
</html>