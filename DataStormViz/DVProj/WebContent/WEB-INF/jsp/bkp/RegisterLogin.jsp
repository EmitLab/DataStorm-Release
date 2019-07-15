<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
 <%@ page import="com.asu.ds.seo.utils.*" %>
<!DOCTYPE html>
<html lang="en">
<head>
    <title>DATA STORM</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link rel="stylesheet"
          href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css">
    <link rel="stylesheet"
          href="https://use.fontawesome.com/releases/v5.2.0/css/all.css">
    <link href="https://fonts.googleapis.com/css?family=Gugi"
          rel="stylesheet">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
</head>
<style>
    .panel-login > .panel-heading {
        color: #00415d;
        background-color: transparent;
        border-color: #fff;
        text-align: center;
    }

        .panel-login > .panel-heading a {
            text-decoration: none;
            color: #666;
            font-weight: bold;
            font-size: 15px;
            -webkit-transition: all 0.1s linear;
            -moz-transition: all 0.1s linear;
            transition: all 0.1s linear;
        }

            .panel-login > .panel-heading a.active {
                color: black;
                font-size: 22px;
            }

        .panel-login > .panel-heading hr {
            margin-top: 10px;
            margin-bottom: 0px;
            clear: both;
            border: 0;
            height: 1px;
            background-image: -webkit-linear-gradient(left,rgba(0, 0, 0, 0),rgba(0, 0, 0, 1.15),rgba(0, 0, 0, 0));
            background-image: -moz-linear-gradient(left,rgba(0,0,0,0),rgba(0,0,0,1.15),rgba(0,0,0,0));
            background-image: -ms-linear-gradient(left,rgba(0,0,0,0),rgba(0,0,0,1.15),rgba(0,0,0,0));
            background-image: -o-linear-gradient(left,rgba(0,0,0,0),rgba(0,0,0,1.15),rgba(0,0,0,0));
        }

    .panel-login input[type="text"], .panel-login input[type="email"], .panel-login input[type="password"] {
        height: 45px;
        border: 0px solid #ddd;
        font-size: 16px;
        -webkit-transition: all 0.1s linear;
        -moz-transition: all 0.1s linear;
        transition: all 0.1s linear;
    }

    .panel-login input:hover,
    .panel-login input:focus {
        outline: none;
        -webkit-box-shadow: none;
        -moz-box-shadow: none;
        box-shadow: none;
        border-color: #ccc;
    }

    .btn-login {
        background-color: lightgray;
        outline: none;
        color: black;
        font-size: 14px;
        height: auto;
        font-weight: normal;
        padding: 14px 0;
        text-transform: uppercase;
        border-color: black;
    }

        .btn-login:hover,
        .btn-login:focus {
            color: #fff;
            background-color: #716666;
            border-color: black;
        }

    .forgot-password {
        text-decoration: underline;
        color: black;
    }

        .forgot-password:hover,
        .forgot-password:focus {
            text-decoration: underline;
            color: #666;
        }

    .btn-register {
        background-color: lightgray;
        outline: none;
        color: black;
        font-size: 14px;
        height: auto;
        font-weight: normal;
        padding: 14px 0;
        text-transform: uppercase;
        border-color: black;
    }

        .btn-register:hover,
        .btn-register:focus {
            color: #fff;
            background-color: #716666;
            border-color: black;
        }

    .panel-heading {
        background-color: #6200ee;
        color: white;
    }

    body {
       /* background-image: url("dust_scratches.png"); */
        background-repeat: repeat;
    }

    .panel {
        border-radius: 0px !important;
        background-color: transparent !important;
        margin-bottom: 20px;
        background-color: #fff;
        border: none !important;
        border-radius: none !important;
        webkit-box-shadow: none !important;
        box-shadow: none !important;
    }

    .btn {
        border-radius: 0px !important;
        display: -webkit-inline-box !important;
        width: 30% !important;
    }

    .form-control {
        border-radius: 0px !important;
        -moz-transition: all .5s !important;
        -webkit-transition: all .5s !important;
        transition: all .5s !important;
    }

    .panel-login input[type="text"]:focus, .panel-login input[type="email"]:focus, .panel-login input[type="password"]:focus {
        border-color: #66afe9 !important;
        outline: 0 !important;
        -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(102, 175, 233, 0.6) !important;
        box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(102, 175, 233, 0.6) !important;
    }

    .highlight {
        -webkit-box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(255, 0, 0, 0.6) !important;
        box-shadow: inset 0 1px 1px rgba(0,0,0,.075), 0 0 8px rgba(255, 0, 0, 0.6) !important;
    }

    .project-name {
        font-family: 'Gugi', cursive;
        padding-right: 2%;
        overflow: hidden;
        white-space: nowrap;
    }

    .tab {
        margin-top: 3%;
    }

    .input-group-addon {
        font-size: 14px;
        font-weight: 400;
        line-height: 1;
        color: rgb(85, 85, 85);
        text-align: center;
        background-color: rgb(238, 238, 238);
        padding: 12px 12px;
        border-width: 1px;
        border-style: solid;
        border-color: rgb(204, 204, 204);
        border-image: initial;
        border-radius: 4px;
    }

    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border: 0;
        border-top: 0px solid rgba(0,0,0,.1);
    }

    .span-wid {
        width: 45px !important;
    }

    .Validation-Error {
        font-size: 80%;
        color: #dc3545;
        min-height: 12px;
    }

    .fa-icon-correct-username, .fa-icon-correct-password, .fa-icon-correct-firstname, .fa-icon-correct-lastname, .fa-icon-correct-userName, .fa-icon-correct-email, .fa-icon-correct-passWord, .fa-icon-correct-confirm-password, .fa-icon-error-username, .fa-icon-error-password, .fa-icon-error-firstname, .fa-icon-error-lastname, .fa-icon-error-userName, .fa-icon-error-email, .fa-icon-error-passWord, .fa-icon-error-confirm-password {
        margin-left: 5px;
    }
</style>
<script>
    $(function () {
        $('.fa-icon-correct-username, .fa-icon-correct-password, .fa-icon-correct-firstname, .fa-icon-correct-lastname, .fa-icon-correct-userName, .fa-icon-correct-email, .fa-icon-correct-passWord, .fa-icon-correct-confirm-password, .fa-icon-error-username, .fa-icon-error-password, .fa-icon-error-firstname, .fa-icon-error-lastname, .fa-icon-error-userName, .fa-icon-error-email, .fa-icon-error-passWord, .fa-icon-error-confirm-password').css('display', 'none');
        $('#login-form-link').click(function (e) {
            $("#login-form").delay(100).fadeIn(100);
            $("#register-form").fadeOut(100);
            $('#register-form-link').removeClass('active');
            $(this).addClass('active');
            e.preventDefault();
        });
        $('#register-form-link').click(function (e) {
            $("#register-form").delay(100).fadeIn(100);
            $("#login-form").fadeOut(100);
            $('#login-form-link').removeClass('active');
            $(this).addClass('active');
            e.preventDefault();
        });

        $("#login-submit").click(function (e) {
            if ($("#username").val() == "" || $("#username").val() == null) {
                $("#username").addClass('highlight');
                $("#invalid-UserName-error").css("display", "block");
                $("#invalid-UserName-error").text("Invalid Username");
                $('.fa-icon-correct-username').css('color', 'transparent');
                $('.fa-icon-error-username').css('color', '#c44');
                return;

            }
            else {

            	//AJAX FOR LIGIN
                $('#username').removeClass('highlight');
                $("#invalid-UserName-error").css("display", "none");
                $('.fa-icon-correct-username').css('color', '#2c2');
                $('.fa-icon-error-username').css('color', 'transparent');
            }
            if ($("#password").val() == "" || $("#password").val() == null) {
                $("#password").addClass('highlight');
                $("#invalid-Password-error").css("display", "block");
                $("#invalid-Password-error").text("Invalid Password");
                $('.fa-icon-correct-password').css('color', 'transparent');
                $('.fa-icon-error-password').css('color', '#c44');
                return;
            }
            else {
                $('#password').removeClass('highlight');
                $("#invalid-Password-error").text("");
                $("#invalid-Password-error").css("display", "none");
                $('.fa-icon-correct-password').css('color', '#2c2');
                $('.fa-icon-error-password').css('color', 'transparent');
                
                
                   var loginCredentials = {
                		
            			email: $("#username").val(),
            			psw:  $("#password").val()
            		};
                   $.ajax({
                	    type: "POST",
                	    url: "Loginconn",//servlet
                	    contentType: "application/json", // NOT dataType!
                	    data: JSON.stringify(loginCredentials),
                	    success: function(response) {
                	    	
                	    	var r = response.response_code;
                	    	console.log(r);
                	    	var id = response.sessionID;
                	    	if( r == 200){
                	    		//console.log(r);
                	    		console.log("login ajax success");
                	    		window.location.replace("http://localhost:8080/DVProj/");
                	    	}
                	    	if(r == 400){
                	    		console.log("login ajax failure");
                	    	}
                	    	
                	    }
                	});
            }

        });
        $("#email").change(function () {
            var em = $('#email').val();
            if (!isValidEmail(em) || em.length == 0) {
                $("#email").addClass('highlight');
                $("#invalid-email-error").css("display", "block");
                $("#invalid-email-error").text("Please correct Email Id");
                $('.fa-icon-correct-email').css('display', 'none');
                $('.fa-icon-error-email').css('display', 'block');
                $('.fa-icon-error-email').css('color', '#c44');
                return;
            }
            else {
                $('#email').removeClass('highlight');
                $("#invalid-email-error").text("");
                $("#invalid-email-error").css("display", "none");
                $('.fa-icon-error-email').css('display', 'none');
                $('.fa-icon-correct-email').css('display', 'block');
                $('.fa-icon-correct-email').css('color', '#2c2');
            }
        });
        $("#firstname").change(function () {
            if ($("#firstname").val() == "" || $("#firstname").val() == null) {
                $("#firstname").addClass('highlight');
                $("#invalid-firstname-error").css("display", "block");
                $("#invalid-firstname-error").text("First Name cannot be empty");
                $('.fa-icon-correct-firstname').css('display', 'none');
                $('.fa-icon-error-firstname').css('display', 'block');
                $('.fa-icon-error-firstname').css('color', '#c44');
                return;

            }
            else {
                $('#firstname').removeClass('highlight');
                $("#invalid-firstname-error").css("display", "none");
                $('.fa-icon-error-firstname').css('display', 'none');
                $('.fa-icon-correct-firstname').css('display', 'block');
                $('.fa-icon-correct-firstname').css('color', '#2c2');
            }
        });
       
        $("#register-submit").click(function (e) {
            if ($("#firstname").val() == "" || $("#firstname").val() == null) {
                $("#firstname").addClass('highlight');
                $("#invalid-firstname-error").css("display", "block");
                $("#invalid-firstname-error").text("First Name cannot be empty");
                $('.fa-icon-correct-firstname').css('display', 'none');
                $('.fa-icon-error-firstname').css('display', 'block');
                $('.fa-icon-error-firstname').css('color', '#c44');
                return;

            }
            else {
            	//
                $('#firstname').removeClass('highlight');
                $("#invalid-firstname-error").css("display", "none");
                $('.fa-icon-error-firstname').css('display', 'none');
                $('.fa-icon-correct-firstname').css('display', 'block');
                $('.fa-icon-correct-firstname').css('color', '#2c2');
            }
            if ($("#lastname").val() == "" || $("#lastname").val() == null) {
                $("#lastname").addClass('highlight');
                $("#invalid-lastname-error").css("display", "block");
                $("#invalid-lastname-error").text("Last Name cannot be empty");
                $('.fa-icon-correct-lastname').css('display', 'none');
                $('.fa-icon-error-lastname').css('display', 'block');
                $('.fa-icon-error-lastname').css('color', '#c44');
                return;
            }
            else {
                $('#lastname').removeClass('highlight');
                $("#invalid-lastname-error").text("");
                $("#invalid-lastname-error").css("display", "none");
                $('.fa-icon-error-lastname').css('display', 'none');
                $('.fa-icon-correct-lastname').css('display', 'block');
                $('.fa-icon-correct-lastname').css('color', '#2c2');
            }
            if ($("#userName").val() == "" || $("#lastname").val() == null) {
                $("#userName").addClass('highlight');
                $("#invalid-userName-error").css("display", "block");
                $("#invalid-userName-error").text("Last Name cannot be empty");
                $('.fa-icon-correct-userName').css('display', 'none');
                $('.fa-icon-error-userName').css('display', 'block');
                $('.fa-icon-error-userName').css('color', '#c44');
                return;
            }
            else {
                $('#userName').removeClass('highlight');
                $("#invalid-userName-error").text("");
                $("#invalid-userName-error").css("display", "none");
                $('.fa-icon-error-userName').css('display', 'none');
                $('.fa-icon-correct-userName').css('display', 'block');
                $('.fa-icon-correct-userName').css('color', '#2c2');
            }
            if ($("#passWord").val() == "" || $("#lastname").val() == null) {
                $("#passWord").addClass('highlight');
                $("#invalid-passWord-error").css("display", "block");
                $("#invalid-passWord-error").text("Please enter Password");
                $('.fa-icon-correct-passWord').css('display', 'none');
                $('.fa-icon-error-passWord').css('display', 'block');
                $('.fa-icon-error-passWord').css('color', '#c44');
                return;
            }
            else {
                $('#passWord').removeClass('highlight');
                $("#invalid-passWord-error").text("");
                $("#invalid-passWord-error").css("display", "none");
                $('.fa-icon-error-passWord').css('display', 'none');
                $('.fa-icon-correct-passWord').css('display', 'block');
                $('.fa-icon-correct-passWord').css('color', '#2c2');
            }
            if ($("#confirm-password").val() == "" || $("#lastname").val() == null) {
                $("#confirm-password").addClass('highlight');
                $("#invalid-confirm-password-error").css("display", "block");
                $("#invalid-confirm-password-error").text("Please enter Confirm Password");
                $('.fa-icon-correct-confirm-password').css('display', 'none');
                $('.fa-icon-error-confirm-password').css('display', 'block');
                $('.fa-icon-error-confirm-password').css('color', '#c44');
                return;
            }
            else {
                $('#confirm-password').removeClass('highlight');
                $("#invalid-confirm-password-error").text("");
                $("#invalid-confirm-password-error").css("display", "none");
                $('.fa-icon-error-confirm-password').css('display', 'none');
                $('.fa-icon-correct-confirm-password').css('display', 'block');
                $('.fa-icon-correct-confirm-password').css('color', '#2c2');
                
                   var registerCredentials = {
                		
            			first: $("#firstname").val(),
            			last:  $("#lastname").val(),
            			email: $("#email").val(),
            			psw: $("#confirm-password").val()
            			
                   	
            		};
                   console.log(registerCredentials);
                   $.ajax({
                	   
                	    type: "POST",
                	    url: "Registerconn",//servlet
                	    contentType: "application/json", // NOT dataType!
                	    data: JSON.stringify(registerCredentials),
                	    success: function(response) {
                	    	
                	    	var r = response.response_code;
                	    	console.log(r);
                	    	if( r == 200){
                	    		console.log(r);
                	    		location.replace("<%= Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_SERV)%>");
                	    	}
                	    	if(r == 400){
                	    		console.log("hello");
                	    	}
                	    	
                	    }
                	});
                
            }
        });

    });
    function redirectHome(){
    	location.replace("<%= Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_JSP)%>");
    }

    function isValidEmail(emailText) {
        var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
        return pattern.test(emailText);
    };

</script>
<body>
    <div class="">
        <nav id="nav" class="navbar navbar-expand-lg navbar-dark bg-dark text-white rounded" style="margin-bottom: 0!important;">
            <div class="project-name">
                <span class="fab fa-superpowers"></span>&nbsp;DataStorm&nbsp;Visualization
            </div>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav mr-auto">
                    <li class="nav-item">
                        <a class="nav-link">
                            <!--href="./about.jsp">-->
                            <span class="fas fa-ellipsis-h fa-fw"></span>&nbsp;
                            About Us
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
        <div class="">
            <div class="row">
            	<div class="col-lg-4">&nbsp;</div>
                <div class="col-lg-4 tab sticky-top">
                    <div class="col-sm-12">
                        <div class="panel panel-login" style="border: 1px darkgray solid !important; padding:10px;">
                            <div class="panel-heading">
                                <div class="row">
                                    <div class="col-sm-6">
                                        <a href="#" class="active" id="login-form-link">LOGIN</a>
                                    </div>
                                    <div class="col-sm-6">
                                        <a href="#" id="register-form-link">REGISTER</a>
                                    </div>
                                </div>
                                <hr>
                            </div>
                            <hr>
                            <div class="panel-body" style="padding:10px;">
                                <div class="row">
                                    <div class="col-12">
                                        <form id="login-form" role="form" style="display: block;">
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class="input-group">
                                                        <span class="input-group-addon span-wid"><i class="fa fa-user fa" aria-hidden="true"></i></span>
                                                        <input type="text" class="form-control" name="username" id="username" placeholder="User Name" />
                                                        <i class="fa fa-exclamation-circle fn fa-icon-error-username"></i>
                                                        <i class="fa fa-check pn fa-icon-correct-username"></i>
                                                    </div>
                                                </div>
                                                <div class="Validation-Error">
                                                    <span id="invalid-UserName-error" class="invalid-UserName-error" style="display:none;"></span>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class="input-group">
                                                        <span class="input-group-addon span-wid"><i class="fa fa-lock fa-lg" aria-hidden="true"></i></span>
                                                        <input type="password" class="form-control" name="password" id="password" placeholder="Password" />
                                                        <i class="fa fa-exclamation-circle fn fa-icon-error-password"></i>
                                                        <i class="fa fa-check pn fa-icon-correct-password"></i>
                                                    </div>
                                                </div>
                                                <div class="Validation-Error">
                                                    <span id="invalid-Password-error" class="invalid-Password-error" style="display:none;"></span>
                                                </div>
                                            </div>
                                            <hr>
                                            <div class="form-row text-center">
                                                <div class="col-12">
                                                    <input type="button" name="login-submit" id="login-submit" tabindex="4" class="form-control btn btn-login" value="Log In">
                                                </div>
                                            </div>
                                            <hr>
                                            <div class="form-group">
                                                <div class="row">
                                                    <div class="col-12">
                                                        <div class="text-center">
                                                            <a href="#" tabindex="5" class="forgot-password">Forgot Password?</a>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </form>
                                        <form id="register-form" role="form" style="display: none; padding:10px;">
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class="row input-group">
                                                        <div class="col-sm-6" style="padding-right:0px">
                                                            <div class="row input-group">
                                                                <span class="input-group-addon span-wid"><i class="fa fa-user fa" aria-hidden="true"></i></span>
                                                                <input type="text" name="firstname" id="firstname" tabindex="1" class="form-control" style="width:59%" placeholder="First Name *" value="">
                                                                <i class="fa fa-exclamation-circle fn fa-icon-error-firstname"></i>
                                                                <i class="fa fa-check pn fa-icon-correct-firstname"></i>
                                                            </div>
                                                            <div class="row Validation-Error">
                                                                <span id="invalid-firstname-error" class="invalid-firstname-error" style="display:none;"></span>
                                                            </div>
                                                        </div>
                                                        <div class="col-sm-5" style="margin-left:15px;padding-right:0px">
                                                            <div class="row input-group">
                                                                <input type="text" name="lastname" id="lastname" tabindex="1" class="form-control" style="width:59%" placeholder="Last Name *" value="">
                                                                <i class="fa fa-exclamation-circle fn fa-icon-error-lastname"></i>
                                                                <i class="fa fa-check pn fa-icon-correct-lastname"></i>
                                                            </div>
                                                            <div class="row Validation-Error">
                                                                <span id="invalid-lastname-error" class="invalid-lastname-error" style="display:none;"></span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class="row input-group">
                                                        <span class="input-group-addon span-wid"><i class="fa fa-users fa-lg" aria-hidden="true"></i></span>
                                                        <input type="text" name="userName" id="userName" tabindex="1" class="form-control " placeholder="Username *" value="">
                                                        <i class="fa fa-exclamation-circle fn fa-icon-error-userName"></i>
                                                        <i class="fa fa-check pn fa-icon-correct-userName"></i>
                                                    </div>
                                                    <div class="row Validation-Error">
                                                        <span id="invalid-userName-error" class="invalid-userName-error" style="display:none;"></span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class="row input-group">
                                                        <span class="input-group-addon span-wid"><i class="fa fa-envelope fa-lg" aria-hidden="true"></i></span>
                                                        <input type="email" name="email" id="email" class="form-control " placeholder="Email Address *" value="">
                                                        <i class="fa fa-exclamation-circle fn fa-icon-error-email"></i>
                                                        <i class="fa fa-check pn fa-icon-correct-email"></i>
                                                    </div>
                                                    <div class="row Validation-Error">
                                                        <span id="invalid-email-error" class="invalid-email-error" style="display:none;"></span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class="row input-group">
                                                        <span class="input-group-addon span-wid"><i class="fa fa-lock fa-lg" aria-hidden="true"></i></span>
                                                        <input type="password" name="passWord" id="passWord" class="form-control " placeholder="Password *" value="">
                                                        <i class="fa fa-exclamation-circle fn fa-icon-error-passWord"></i>
                                                        <i class="fa fa-check pn fa-icon-correct-passWord"></i>
                                                    </div>
                                                    <div class="row Validation-Error">
                                                        <span id="invalid-passWord-error" class="invalid-passWord-error" style="display:none;"></span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="form-group">
                                                <div class="cols-sm-10">
                                                    <div class=" row input-group">
                                                        <span class="input-group-addon span-wid "><i class="fa fa-lock fa-lg" aria-hidden="true"></i></span>
                                                        <input type="password" name="confirm-password" id="confirm-password" class="form-control " placeholder="Confirm Password *" value="">
                                                        <i class="fa fa-exclamation-circle fn fa-icon-error-confirm-password"></i>
                                                        <i class="fa fa-check pn fa-icon-correct-confirm-password"></i>
                                                    </div>
                                                    <div class="row Validation-Error">
                                                        <span id="invalid-confirm-password-error" class="invalid-confirm-password-error" style="display:none;"></span>
                                                    </div>
                                                </div>
                                            </div>
                                            <hr>
                                            <div class="form-row text-center">
                                                <div class="col-12">
                                                    <input type="button" name="register-submit" id="register-submit" tabindex="4" class="form-control btn btn-register" value="Register">
                                                    
                                                </div>
                                            </div>
                                        </form>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-lg-4">&nbsp;</div>
            </div>
        </div>
    </div>
</body>
</html>