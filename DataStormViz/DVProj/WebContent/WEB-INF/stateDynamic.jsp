<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
    <%@ page import="common.JSONFiles"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>State Model</title>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">

<!-- jQuery library -->
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

<!-- Latest compiled JavaScript -->
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
<script>
var stateJSON = [];

$.getJSON(<%=JSONFiles.JSON_STATE%>, function(json){
	stateJSON = json;
});
function getStateData(){
  console.log(stateJSON.model_type);
  var modelType = stateJSON.model_type;
  if(modelType == "hurricane"){
    setHurricaneState();
  }
}
function setHurricaneState(){
  console.log(stateJSON.model_type);

  
}
$(window).bind('load', function() {
  try{
    getStateData();
    console.log("testing state data");
    
  }
   catch(err){
  $('#myModal').modal('show');
}

});

</script>
</head>
<body>

</body>
</html>