package com.conn;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.bson.Document;
import org.bson.json.JsonWriterSettings;
import org.bson.types.ObjectId;
import org.json.JSONException;

import com.asu.ds.db.mongo.MongoConstants;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.mongodb.BasicDBObject;
import com.mongodb.MongoClient;
import com.mongodb.ReadPreference;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;

/**
 * Servlet implementation class ProvenanceConn
 */
@WebServlet("/ProvenanceConn")
public class ProvenanceConn extends HttpServlet {
	private static final long serialVersionUID = 1L;

	/**
	 * @see HttpServlet#HttpServlet()
	 */
	public ProvenanceConn() {
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
		String mongo_dsfr_id = data.get("mongoid").getAsString();
		System.out.println(mongo_dsfr_id);

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

			//START: Step1 Fetch dsfr data

			//Mongo query to fetch ds_results database -> dsfr collection
			System.out.println("Inside hurricane calls for mongo");
			MongoDatabase database = mongoClient.getDatabase("ds_results"); //specify database
			MongoCollection<Document> collection = database
					.getCollection("dsfr");  //Specify collection

			BasicDBObject whereQuery = new BasicDBObject(); //Build where query object with key value pairs
			whereQuery.put("_id", new ObjectId(mongo_dsfr_id));
			System.out.println("Find Query structure= "+whereQuery.toString());
			List<Document> documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
			int count = 0;
			String json = "";

			//Return all documents from mongo in hashmap
			JsonMap.put("dsfr", documents);
			System.out.println("dsfr Filtered documents size="+documents.size());
			ObjectId dsirId = (ObjectId) documents.get(0).get("parent");

			JsonWriterSettings writerSettings = new JsonWriterSettings();           //JsonMode.SHELL, true
			//		        json1 = new Gson().toJson(JsonMap);  //Create JSON from the ALL the documents that were retrieved
			//At the end of doGet() function we have returned json1 as response to the ajax call

			//END: Fetch dsfr data
			//--------------------------------------------------------------------------------------------------
			//START: Step2 Fetch dsir data

			//Mongo query to fetch ds_results database -> dsir collection
			collection = database
					.getCollection("dsir");  //Specify collection

			whereQuery = new BasicDBObject(); //Build where query object with key value pairs
			whereQuery.put("_id", dsirId);
			System.out.println("Find Query structure= "+whereQuery.toString());
			documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
			count = 0;

			for(Document document : documents){
				System.out.println(document);
			}

			//Return all documents from mongo in hashmap
			JsonMap.put("dsir", documents);
			System.out.println("dsir Filtered documents size="+documents.size());
			ObjectId dsarId = (ObjectId) documents.get(0).get("parent");
			ObjectId jobId = (ObjectId)((Document)documents.get(0).get("metadata")).get("job_id");

			//END: Fetch dsir data
			//--------------------------------------------------------------------------------------------------
			//START: Step3 Fetch dsar data

			//Mongo query to fetch ds_results database -> dsar collection
			collection = database
					.getCollection("dsar");  //Specify collection

			whereQuery = new BasicDBObject(); //Build where query object with key value pairs
			whereQuery.put("_id", dsarId);
			System.out.println("Find Query structure= "+whereQuery.toString());
			documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
			count = 0;

			List<ObjectId> jobsList = new ArrayList<ObjectId>();
			jobsList = (List<ObjectId>)((Document)documents.get(0).get("metadata")).get("jobs");
			System.out.println("DSAR Jobslist: "+jobsList);

			//Return all documents from mongo in hashmap
			JsonMap.put("dsar", documents);
			System.out.println("dsar Filtered documents size="+documents.size());

			//END: Fetch dsar data
			//--------------------------------------------------------------------------------------------------
			//START: Step4 Fetch jobs data

			//Mongo query to fetch ds_results database -> jobs collection
			collection = database
					.getCollection("jobs");  //Specify collection

			whereQuery = new BasicDBObject(); //Build where query object with key value pairs
			//whereQuery.put("_id", jobId);
			whereQuery.put("_id", new BasicDBObject("$in",jobsList)); 

			System.out.println("Find Query structure= "+whereQuery.toString());
			documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
			count = 0;

			//Get upstream jobids and downstreamjobids 
			List<ObjectId> upstreamList = new ArrayList<ObjectId>();
			List<ObjectId> dnstreamList = new ArrayList<ObjectId>();
			List<ObjectId> contributionDsirIdList = new ArrayList<ObjectId>();
			for(Document document : documents){
				System.out.println(document);
				upstreamList = (List<ObjectId>) document.get("upstream_jobs");
				dnstreamList = (List<ObjectId>) document.get("downstream_jobs");
				contributionDsirIdList.add((ObjectId) document.get("output_dsir"));
			}
			//upstreamList.add(new ObjectId("5b73426f4784f40b25641afd")); //ADDED Temporary 

			//Return all documents from mongo in hashmap
			JsonMap.put("jobs", documents);	
			//ObjectId upstreamId = (ObjectId) documents.get(0).get("parent");
			System.out.println("jobs Filtered documents size="+documents.size());
			System.out.println("upstream jobList ="+upstreamList);
			System.out.println("dnstream jobList ="+dnstreamList);

			//END: Fetch jobs data
			//--------------------------------------------------------------------------------------------------
			//START: Step5 Fetch upstream jobs

			//Mongo query to fetch ds_results database -> jobs collection
			collection = database
					.getCollection("jobs");  //Specify collection

			whereQuery = new BasicDBObject(); //Build where query object with key value pairs
			//	     		whereQuery.put("_id", jobId);
			whereQuery.put("_id", new BasicDBObject("$in",upstreamList));  
			System.out.println("Find Query structure= "+whereQuery.toString());
			documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
			count = 0;
			for(Document document : documents){
				System.out.println(document);
				contributionDsirIdList.add((ObjectId) document.get("output_dsir"));
			}


			//Return all documents from mongo in hashmap
			JsonMap.put("upstream", documents);
			System.out.println("jobs Filtered documents size="+documents.size());
			//		    	
			//END: Fetch jobs data
			//--------------------------------------------------------------------------------------------------
			//START: Step6 Fetch dsirIds jobs

			System.out.println("####DSIR contribution ids"+contributionDsirIdList);

			//Mongo query to fetch ds_results database -> jobs collection
			collection = database
					.getCollection("dsir");  //Specify collection

			whereQuery = new BasicDBObject(); //Build where query object with key value pairs
			//	     		whereQuery.put("_id", jobId);
			whereQuery.put("_id", new BasicDBObject("$in",contributionDsirIdList));  
			System.out.println("Find Query structure= "+whereQuery.toString());
			documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
			count = 0;
			/*HashMap<ObjectId,Double> contributionMap = new HashMap<ObjectId,Double>();
				for(Document document : documents){
			           System.out.println(document);
			           contributionMap.put((ObjectId)document.get("_id"), (Double)((Document)document.get("metadata")).get("contribution"));
		        }
			 */

			//Return all documents from mongo in hashmap
			JsonMap.put("contribution", documents);
			System.out.println("jobs Filtered documents size="+documents.size());

			//END: Fetch jobs data
			//--------------------------------------------------------------------------------------------------
			//START: Step6 Fetch downstream jobs
			/*
		    	//Mongo query to fetch ds_results database -> jobs collection
				collection = database
						.getCollection("jobs");  //Specify collection

	     	    whereQuery = new BasicDBObject(); //Build where query object with key value pairs
//	     		whereQuery.put("_id", jobId);
	     		whereQuery.put("_id", new BasicDBObject("$in",dnstreamList));  
	     		System.out.println("Find Query structure= "+whereQuery.toString());
	     		documents = (List<Document>) collection.find(whereQuery).into(new ArrayList<Document>());
				count = 0;


				//Return all documents from mongo in hashmap
				JsonMap.put("downstream", documents);
		        System.out.println("jobs Filtered documents size="+documents.size());
//		    	
		        //END: Fetch jobs data
			 */


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
