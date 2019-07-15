//Controls html filter toggles in layer tab
function getFilter(id) {
	var filter = $("#" + id + "-toggle");
	return filter.hasClass("fa-toggle-on");
}

function setFilter(id, state) {
	var url = new URL(document.location);
	var filter = $("#" + id + "-toggle");
	if(state) {
		filter.removeClass("fa-toggle-off");
		filter.addClass("fa-toggle-on");
		
		setUrlParam(id, true);
	}
	else {
		filter.addClass("fa-toggle-off");
		filter.removeClass("fa-toggle-on");
		
		setUrlParam(id, false);
	}
	
	for(var i = 0;  i < MAPS.length; i++) {
		setGridVisibility(i, id, state);
	}
}

function toggleFilter(id) {
	setFilter(id, !getFilter(id));
}
