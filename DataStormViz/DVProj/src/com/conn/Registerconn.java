package com.conn;

import java.io.File;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.*;

import javax.servlet.ServletContext;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import java.util.ArrayList;
import java.util.List;

import com.asu.ds.db.mongo.MongoConstants;
//Gson imports
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.bson.Document;
import org.bson.json.JsonMode;
import org.bson.json.JsonWriterSettings;
import org.bson.types.ObjectId;
import org.json.JSONException;

//Mongo imports
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.mongodb.*;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;


/**
 * Servlet implementation class Registerconn
 */
@WebServlet("/Registerconn")

public class Registerconn extends HttpServlet {

	private static final long serialVersionUID = 1L;

	protected void doPost(HttpServletRequest request,HttpServletResponse response) throws ServletException, IOException {
			Session SSH_SESSION = null;
		
		try {
			JsonObject data = new Gson().fromJson(request.getReader(), JsonObject.class);
			String first = data.get("first").getAsString();
			String last = data.get("last").getAsString();
			String email = data.get("email").getAsString();
			String password = data.get("psw").getAsString();
			

            String hashTostore = hashPassword(password);//hash password
            
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
			DB db = mongoClient.getDB("Users");
		    
		    DBCollection collection = db.getCollection("user_data");
		    
		    
			BasicDBObject emailQuery = new BasicDBObject();
			emailQuery.put("email",email);
		    
            
            /*

			Mongo mongo = new Mongo("127.0.0.1", 27017);
			DB db = mongo.getDB("mydb");
			DBCollection collection = db.getCollection("users");
			
			
			BasicDBObject emailQuery = new BasicDBObject();
			emailQuery.put("email",email);
			
			*/
			if(collection.find(emailQuery).count()>0) {
				
				
				System.out.println("user already exists");

				JsonObject json = new JsonObject();
				json.addProperty("response_code", 400);
			    response.setContentType("application/json");
			    response.setCharacterEncoding("UTF-8");
			    response.getWriter().print(json);
				
			}
			else {
				BasicDBObject document = new BasicDBObject();
				document.put("email", email);
				document.put("password", hashTostore);
				document.put("sessionID", null);
				collection.insert(document);
				
				JsonObject json = new JsonObject();
				json.addProperty("response_code", 200);
			    response.setContentType("application/json");
			    response.setCharacterEncoding("UTF-8");
			    response.getWriter().print(json);
				
			}

		}
		catch(Exception e) {
			
			
		}
		finally {
			try {
				MongoConstants mongoconstants = new MongoConstants(getServletContext().getRealPath(""));
				SSH_SESSION.delPortForwardingL(mongoconstants.get_local_port());
			} catch (JSchException e) {
				e.printStackTrace();
			} catch (JSONException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}

	}
	public String hashPassword(String password) throws NoSuchAlgorithmException {
		
		byte[] salt = new byte[16];
		salt = "ProjectDataStorm".getBytes();
		MessageDigest md = MessageDigest.getInstance("SHA-512");
		md.update(salt);
		byte[] hashedPassword = md.digest(password.getBytes());
		String hashTostore;
        StringBuilder sb = new StringBuilder();
        for(int i=0; i< hashedPassword.length ;i++)
        {
            sb.append(Integer.toString((hashedPassword[i] & 0xff) + 0x100, 16).substring(1));
        }
        
        hashTostore = sb.toString();
        return hashTostore;
		
	}

}
