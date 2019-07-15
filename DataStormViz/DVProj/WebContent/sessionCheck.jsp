<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
    <%@ page import="com.mongodb.*" %>
    <%@ page import="com.asu.ds.seo.utils.*" %>
<%
System.out.println("hello im here");
 	BasicDBObject credentialQuery = new BasicDBObject();
	credentialQuery.put("sessionID",session.getAttribute("sessionID"));
	
	Mongo mongo = new Mongo("127.0.0.1", 27017);
	DB db = mongo.getDB("mydb");
	DBCollection collection = db.getCollection("users");
	
	if (session.getAttribute("sessionID") == null /*|| collection.find(credentialQuery).count() == 0*/) {
		response.sendRedirect(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_JSP));
	}
	else{
		System.out.println(collection.find(credentialQuery).count());
		response.sendRedirect(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_JSP));
	}
%>