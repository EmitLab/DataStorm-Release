package com.conn;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.util.ArrayList;
import java.util.List;

//Gson imports
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.bson.Document;
import org.bson.json.JsonMode;
import org.bson.json.JsonWriterSettings;
import org.bson.types.ObjectId;

//Mongo imports
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.mongodb.BasicDBObject;
import com.mongodb.MongoClient;
import com.mongodb.ReadPreference;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;

/**
 * Servlet implementation class Mongoconn
 */
@WebServlet("/Mongoconn")
public class Mongoconn extends HttpServlet {
	private static final long serialVersionUID = 1L;

    /**
     * Default constructor. 
     */	
    public Mongoconn() {
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
//		response.getWriter().append("Served at: ").append(request.getContextPath());
		  
	    String json1 = "";
		//Process the parameters sent from ajax calls and separate out the each key
		JsonObject data = new Gson().fromJson(request.getReader(), JsonObject.class);
		String model_type = data.get("model_type").getAsString();
		long start_time = data.get("start_time").getAsLong();
		long end_time = data.get("end_time").getAsLong();
		float threshold = data.get("threshold").getAsFloat();
		System.out.println(model_type+" "+start_time+" "+end_time);
		
		
		// forwarding ports
		String LOCAL_HOST = "127.0.0.1";
		String REMOTE_HOST =  "";  // Remote Server IP address
		Integer LOCAL_PORT =  "";  // Remote Server Port
		Integer REMOTE_PORT = 27017; // Default mongodb port

		// ssh connection info
		String SSH_USER = ""; // Remote Server User Name
		String SSH_PASSWORD = ""; // Remote Server User password
		String SSH_HOST =  "";  // Remote Server IP address
		Integer SSH_PORT =  "";  // Remote Server Port

		Session SSH_SESSION = null;

		try {
		    java.util.Properties config = new java.util.Properties();
		    config.put("StrictHostKeyChecking", "no");
		    JSch jsch = new JSch();
		    
		    //Path for private key dsworker_rsa file
		    String path = getServletContext().getRealPath(File.separator+"WEB-INF"+File.separator+"dsworker_rsa");
		    System.out.println	("KeyFile path="+path);
		    jsch.addIdentity(path, "passphrase");
		    
		    //Establish secure tunnel with server
		    SSH_SESSION = null;
		    SSH_SESSION = jsch.getSession(SSH_USER, SSH_HOST, SSH_PORT);
		    SSH_SESSION.setConfig(config);
		    SSH_SESSION.connect();
		    System.out.println("Connection established...");
		    SSH_SESSION.setPortForwardingL(LOCAL_PORT, LOCAL_HOST, REMOTE_PORT);
		    System.out.println("Port forwarding done...");

		    //Mongo calls
		    MongoClient mongoClient = new MongoClient(LOCAL_HOST, LOCAL_PORT);
		    mongoClient.setReadPreference(ReadPreference.nearest());
		    System.out.println("Mongo client created...");
		    
//		    //Mongo query to list database names
//		    MongoCursor<String> dbNames = mongoClient.listDatabaseNames().iterator();
//		    System.out.println("Mongo cursor fetched...");
//		    while (dbNames.hasNext()) {
//		    	System.out.println(dbNames.next());
//		    }
		    
		    //Fetch DSIR id for the model type and parent not null
		    System.out.println("Fetching DSIR id");
		    MongoDatabase database = mongoClient.getDatabase("ds_results"); //specify database
			MongoCollection<Document> collection = database
					.getCollection("dsir");  //Specify collection

     	    BasicDBObject whereQuery = new BasicDBObject();
     		whereQuery.put("metadata.model_type", model_type);
     		BasicDBObject parent = new BasicDBObject();
     		parent.put("$ne", null);
     		whereQuery.put("parent", parent);
     		
     		System.out.println("Find Query structure= "+whereQuery.toString());
     		List<Document> documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
     		ObjectId dsir_id = null;
     		if(documents.size()>0){
	     		dsir_id = (ObjectId) documents.get(0).get("_id");
	     		System.out.println("Fetched DSIR documents: size ="+documents.size());
	     		System.out.println("DSIR id = "+dsir_id);
     		}
		    //If call needs hurricane data
		    if(model_type.equals("hurricane"))
		    {
		    	//Mongo query to fetch ds_results database -> dsfr collection
		    	System.out.println("Inside hurricane calls for mongo");
			    database = mongoClient.getDatabase("ds_results"); //specify database
				collection = database
						.getCollection("dsfr");  //Specify collection

	     	    whereQuery = new BasicDBObject();
	     		whereQuery.put("model_type", model_type);
	     		BasicDBObject timestamp = new BasicDBObject();
	     		timestamp.put("$gte", start_time);
	     		timestamp.put("$lt", end_time);
	     		whereQuery.put("timestamp", timestamp);
	     		whereQuery.put("parent", dsir_id);  //TODO: uncomment this once dsir ids are mapped with dsfr for hurricane
	     		whereQuery.put("observation.0", new BasicDBObject("$gte", threshold));
	     		
	     		System.out.println("Find Query structure= "+whereQuery.toString());
	     		documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
				int count = 0;
				String json = "";
				
				//To iterate through each document and make changes in document if required!!!
//	            for(Document document : documents){
////	        	   count++;
////		           System.out.println(document);
//////	        	   document.remove("_id");
//	               JsonWriterSettings writerSettings = new JsonWriterSettings();           //JsonMode.SHELL, true
//	               System.out.println(document.toJson(writerSettings)+",");
////	               	
//	           }
//	           
				//Return all documents from Mongo without change
	           System.out.println("Filtered documents size="+documents.size());
	           JsonWriterSettings writerSettings = new JsonWriterSettings();           //JsonMode.SHELL, true
	           json1 = new Gson().toJson(documents);  //Create JSON from the ALL the documents that were retrieved
	           //At the end of doGet() function we have returned json1 as response to the ajax call
		    	
		    } //END: if(model_type.equals("hurricane"))
		    
		    //If call needs flood data
		    else if(model_type.equals("flood"))
		    {
		    	//Mongo query to fetch ds_results database -> dsfr collection
		    	System.out.println("Inside flood calls for mongo");
			    database = mongoClient.getDatabase("ds_results"); //specify database
				collection = database
						.getCollection("dsfr");  //Specify collection

				whereQuery = new BasicDBObject();
	     		whereQuery.put("model_type", model_type);
	     		BasicDBObject timestamp = new BasicDBObject();
	     		timestamp.put("$gte", start_time);
	     		timestamp.put("$lt", end_time);
	     		whereQuery.put("timestamp", timestamp);
	     		whereQuery.put("observation.0", new BasicDBObject("$gte", threshold));
	     		whereQuery.put("parent", dsir_id);  //TODO: uncomment this once dsir ids are mapped with dsfr for flood
	     		
	     		System.out.println("Find Query structure= "+whereQuery.toString());
	     		documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
				int count = 0;
				String json = "";
			
				//Return all documents from Mongo without change
	           System.out.println("Filtered documents size="+documents.size());
	           JsonWriterSettings writerSettings = new JsonWriterSettings();           //JsonMode.SHELL, true
	           json1 = new Gson().toJson(documents);  //Create JSON from the ALL the documents that were retrieved
	           //At the end of doGet() function we have returned json1 as response to the ajax call
		    	
		    } //END: if(model_type.equals("flood"))
		    
		    //If call needs human mobility data
		    else if(model_type.equals("human_mobility"))
		    {
		    	//Mongo query to fetch ds_results database -> dsfr collection
		    	System.out.println("Inside human mobility calls for mongo");
			    database = mongoClient.getDatabase("ds_results"); //specify database
				collection = database
						.getCollection("dsfr");  //Specify collection

				whereQuery = new BasicDBObject();
	     		whereQuery.put("model_type", model_type);
	     		BasicDBObject timestamp = new BasicDBObject();
	     		timestamp.put("$gte", start_time);
	     		timestamp.put("$lt", end_time);
	     		whereQuery.put("timestamp", timestamp);
	     		//whereQuery.put("parent", dsir_id);  TODO: remove this once dsir ids are mapped with dsfr for hmm
	     		
	     		System.out.println("Find Query structure= "+whereQuery.toString());
	     		documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
				int count = 0;
				String json = "";
			
				//Return all documents from Mongo without change
	           System.out.println("Filtered documents size="+documents.size());
	           JsonWriterSettings writerSettings = new JsonWriterSettings();           //JsonMode.SHELL, true
	           json1 = new Gson().toJson(documents);  //Create JSON from the ALL the documents that were retrieved
	           //At the end of doGet() function we have returned json1 as response to the ajax call
		    	
		    } //END: if(model_type.equals("human_mobility"))
		    
		} catch (Exception e) {
		    e.printStackTrace();
		} finally {

			try {
				SSH_SESSION.delPortForwardingL(LOCAL_PORT);
			} catch (JSchException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
//		    SSH_SESSION.disconnect();
		}

			
		
//		String json = new Gson().toJson("{'key2':'value2'}");
	    response.setContentType("application/json");
	    response.setCharacterEncoding("UTF-8");
	    response.getWriter().write(json1);
	
	}
	
	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		System.out.println("doPost called...");
		doGet(request, response);
	}

}
