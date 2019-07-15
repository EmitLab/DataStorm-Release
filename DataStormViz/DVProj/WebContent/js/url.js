var URL_PARAMS = {};

function getUrlParam(key) {
	return URL_PARAMS[key];
}

function setUrlParam(key, value) {
	URL_PARAMS[key] = value;
	updateUrl();
}

function initUrlParams() {
    window.location.href.replace(/[#&]+([^=&]+)=([^&]*)/gi, function(m, key, value) {
        URL_PARAMS[key] = value;
    });
}

function updateUrl() {
	if(getConfigState() == "url") {
		var hash = "";
		for(var key in URL_PARAMS) {
			hash += key + "=" + URL_PARAMS[key];
			hash += "&";
		}
		window.location.hash = hash.slice(0, -1);
	}
	else {
		window.location.hash = "";
	}
}

initUrlParams();
