function isBrowser() { 
	var isChrome = false;
	if((navigator.userAgent.indexOf("Opera") || navigator.userAgent.indexOf('OPR')) != -1 ) {
		console.log('Opera');
	} else if(navigator.userAgent.indexOf("Chrome") != -1 ) {
		console.log('Chrome');
		isChrome = true;
	} else if(navigator.userAgent.indexOf("Safari") != -1) {
		console.log('Safari');
	} else if(navigator.userAgent.indexOf("Firefox") != -1 ) {
		console.log('Firefox');
	} else if((navigator.userAgent.indexOf("MSIE") != -1 ) || (!!document.documentMode == true )) {
		console.log('IE'); 
	} else {
		console.log('unknown');
	}
	
	if (!isChrome){
		var $alert = $("<div/>").addClass("alert alert-danger").css("margin-bottom","-5px");
		var $container = $("<div/>").addClass("container").html("<i class=\"fas fa-info-circle fa-fw\"></i> Some functions might not work as intended. Please use the latest version of <b><a href=\"https://www.google.com/chrome/\" class=\"btn-link\" target=\"_blank\">Chrome</a></b>.");
		$alert.append($container);
		$("body").prepend($alert);
	}
}