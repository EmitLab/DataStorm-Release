package com.asu.ds.seo.utils;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

import javax.servlet.RequestDispatcher;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class Seo {
	
	public static boolean DEPLOY = false;
	
	public static String PAGE_LOCATION = "/WEB-INF/jsp";
	public static String CONFIG_LOCATION ="/WEB-INF/config";
	
	public static String DS_MONGO_CONFIG_FILE_NAME = "mongo.json";
	public static String DS_KEPLER_CONFIG_FILE_NAME = "kepler.json";
	
	public static String TYPE_JSP = "jsp";
	public static String TYPE_SERV = "serv";
	public static String TYPE_FULL = "full";
	
	public static String ABOUT      = "/about";
	public static String DASHBOARD  = "/dashboard";
	public static String LOGIN      = "/login";
	public static String PROVENANCE = "/provenance";
	public static String SIMULATOR  = "/simulator";
	public static String STATE      = "/state";
	public static String STORE      = "/store";
	public static String SYSTEM     = "/system";
	public static String WELCOME    = "/welcome";
	
	public static String getProjectName() {
		if (DEPLOY) {
			return "/";
		} else {
			return "/datastorm";
		}
	}
	
	public static String getKeplerConfigFilePath(String context_path) {
		Path filePath = Paths.get(context_path, CONFIG_LOCATION, DS_KEPLER_CONFIG_FILE_NAME);
		
		return filePath.toString();
	}
	
	public static String getMongoConfigFilePath(String context_path) {
		Path filePath = Paths.get(context_path, CONFIG_LOCATION, DS_MONGO_CONFIG_FILE_NAME);
		
		return filePath.toString();
	}
	
	public static String getSeoPath(String page_name, String type) {
		if (type.equals("jsp")) {
			return PAGE_LOCATION + page_name + ".jsp";
		} else if (type.equals("serv")){
			return page_name;
		} else {
			if (DEPLOY) {
				return page_name;
			} else {
				return getProjectName() + page_name;	
			}
		}
	}
	
	public static void forward(String address, HttpServletRequest request,
			HttpServletResponse response) throws ServletException, IOException {
		RequestDispatcher dispatcher = request.getRequestDispatcher(address);
		dispatcher.forward(request, response);
	}
	
	public static void sendRedirect(String address,HttpServletResponse response) throws ServletException, IOException {
		response.sendRedirect(address);
	}
	
	public static String getRandomString(){
		/* Random String generator*/
		return UUID.randomUUID().toString().replace("&", "").replace("-", "");	
	}
	
	public static String getRequestVariable(HttpServletRequest request, String variable) {
		if(request.getParameter(variable) != null) {
			return request.getParameter(variable);
		} else {
			return (String) request.getAttribute(variable);
		}
	}
}
