package com.conn;

import com.asu.ds.db.mongo.MongoConstants;

import java.io.File;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

//Gson imports
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.json.JSONException;

//Mongo imports
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;
import com.mongodb.*;


/**
 * Servlet implementation class Registerconn
 */
@WebServlet("/Loginconn")

public class Loginconn extends HttpServlet {

	private static final long serialVersionUID = 1L;

	protected void doPost(HttpServletRequest request,HttpServletResponse response) throws ServletException, IOException {
		HttpSession session = request.getSession(true);
		
		Session SSH_SESSION = null;

		try {

			JsonObject data = new Gson().fromJson(request.getReader(), JsonObject.class);
			String email = data.get("email").getAsString();
			String password = data.get("psw").getAsString();
			System.out.println("email "+email+"psw "+password);

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



			BasicDBObject credentialQuery = new BasicDBObject();
			credentialQuery.put("email",email);
			credentialQuery.put("password", hashTostore);

			DBCursor cursor = collection.find(credentialQuery);
			System.out.println("COUNT: "+ cursor.count());

			if(cursor.count() > 0) {

				DBObject result = cursor.one();

				System.out.println("access granted");
				String sessionID = Double.toString(Math.random());
				System.out.println(sessionID);
				session.setAttribute("sessionID", sessionID);

				result.put("sessionID", sessionID);

				collection.update(credentialQuery, result);

				JsonObject json = new JsonObject();
				json.addProperty("response_code", 200);
				response.setContentType("application/json");
				response.setCharacterEncoding("UTF-8");
				response.getWriter().print(json);



			}
			else {
				System.out.println("does not exist");

				JsonObject json = new JsonObject();
				json.addProperty("response_code", 400);
				response.setContentType("application/json");
				response.setCharacterEncoding("UTF-8");
				response.getWriter().print(json);



			}
			mongoClient.close();
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
