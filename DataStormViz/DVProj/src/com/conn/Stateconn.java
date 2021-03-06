package com.conn;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.bson.Document;
import org.bson.json.JsonWriterSettings;
import org.json.JSONException;

import com.asu.ds.db.mongo.MongoConstants;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.mongodb.MongoClient;
import com.mongodb.ReadPreference;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

/**
 * Servlet implementation class Stateconn
 */
@WebServlet(description = "for fetching state related collections", urlPatterns = { "/Stateconn" })
public class Stateconn extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public Stateconn() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
//		response.getWriter().append("Served at: ").append(request.getContextPath());
		
		String json1 = "";
		HashMap<String, List<Document>> JsonMap = new HashMap<>();
			//Process the parameters sent from ajax calls and separate out the each key
			JsonObject data = new Gson().fromJson(request.getReader(), JsonObject.class);
			String temp = data.get("temp").getAsString();
			
			Session SSH_SESSION = null;

			try {
			    java.util.Properties config = new java.util.Properties();
			    config.put("StrictHostKeyChecking", "no");
			    JSch jsch = new JSch();
			    
			    //Path for private key dsworker_rsa file
			    String path = getServletContext().getRealPath(File.separator+"WEB-INF"+File.separator+"dsworker_rsa");
			    System.out.println	("KeyFile path="+path);
			    jsch.addIdentity(path, "passphrase");
			    
			    MongoConstants mongoconstants = new MongoConstants(getServletContext().getRealPath(""));
			    
			    SSH_SESSION = null;
				SSH_SESSION = jsch.getSession(mongoconstants.get_ssh_user(), mongoconstants.get_ssh_host(), mongoconstants.get_ssh_port());
				SSH_SESSION.setConfig(config);
				SSH_SESSION.connect();
				System.out.println("Connection established index.jsp...");
				
				SSH_SESSION.setPortForwardingL(mongoconstants.get_local_port(), mongoconstants.get_local_host(), mongoconstants.get_remote_port());   
				
				System.out.println("Port forwarding done...");

				MongoClient mongoClient = new MongoClient(mongoconstants.get_local_host(), mongoconstants.get_local_port());
				mongoClient.setReadPreference(ReadPreference.nearest());
			    System.out.println("Mongo client created...");
			    
			    //START: Step1 Fetch kepler collection data
			    
		    	//Mongo query to fetch ds_results database -> dsfr collection
		    	System.out.println("Inside hurricane calls for mongo");
			    MongoDatabase database = mongoClient.getDatabase("ds_state"); //specify database
				MongoCollection<Document> collection = database
						.getCollection("kepler");  //Specify collection

				//Fetch all documents --NO where clause for this query
	     		List<Document> documents = (List<Document>) collection.find().into(new ArrayList<Document>());
				int count = 0;
				String json = "";
			
	            for(Document document : documents){
	            	Document d = (Document) document.get("temporal_context");
		           System.out.println(d.get("begin"));
	           }
	           
				//Return all documents from mongo in hashmap
				JsonMap.put("kepler", documents);
		        System.out.println("kepler Filtered documents size="+documents.size());
		        
		        JsonWriterSettings writerSettings = new JsonWriterSettings();           //JsonMode.SHELL, true
		        
		        //temp Create gson instance
		        GsonBuilder gb = new GsonBuilder().serializeSpecialFloatingPointValues();
//		        String jsontemp = gb.create().toJson(documents);
//		        System.out.println(jsontemp);
		        
//		        json1 = new Gson().toJson(JsonMap);  //Create JSON from the ALL the documents that were retrieved
		        //At the end of doGet() function we have returned json1 as response to the ajax call
		        ///json1 = new Gson().toJson(JsonMap);
		        
		        //END: Fetch kepler data
		        //--------------------------------------------------------------------------------------------------
		        //START: Step2 Fetch cluster data
			    
		    	//Mongo query to fetch ds_results database -> dsir collection
				collection = database
						.getCollection("cluster");  //Specify collection

				//Fetch all documents --NO where clause for this query
	     		documents = (List<Document>) collection.find().into(new ArrayList<Document>());
				count = 0;
				
	            for(Document document : documents){
		           System.out.println(document);
	           }
	           
				//Return all documents from mongo in hashmap
				JsonMap.put("cluster", documents);
		        System.out.println("cluster Filtered documents size="+documents.size());
		    	
		        //END: Fetch cluster data
		      //--------------------------------------------------------------------------------------------------

		        json1 = new Gson().toJson(JsonMap);  //Create JSON from the ALL the documents that were retrieved
		        //At the end of doGet() function we have returned json1 as response to the ajax call
	           
	           
			    
			} catch (Exception e) {
			    e.printStackTrace();
			} finally {

				try {
					MongoConstants mongoconstants = new MongoConstants(getServletContext().getRealPath(""));
					SSH_SESSION.delPortForwardingL(mongoconstants.get_local_port());
				} catch (JSchException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
//			    SSH_SESSION.disconnect();
				catch (JSONException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}

			System.out.println("json1= "+json1);
			String statusJSON = new Gson().toJson("{'status':'success'}");
			
		    response.setContentType("application/json");
		    response.setCharacterEncoding("UTF-8");
		    response.getWriter().write(json1);
		
			  
		
		
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		doGet(request, response);
	}

}
