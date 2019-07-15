package com.asu.ds.controller;

import javax.servlet.ServletException;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.bson.Document;
import org.json.JSONException;

import com.jcraft.jsch.Session;
import com.asu.ds.Sessions.Sessions;
import com.asu.ds.cookies.Cookies;
import com.asu.ds.db.mongo.MongoConstants;
import com.asu.ds.db.mongo.MongoKeys;
import com.asu.ds.seo.utils.Seo;
import com.mongodb.*;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoDatabase;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;

import static com.mongodb.client.model.Filters.eq;

import java.io.File;
import java.io.IOException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;

public class LoginController {
	
	public Boolean isLoggedIn(HttpServletRequest request, HttpServletResponse response) {
		HttpSession session = request.getSession();
		Cookie[] cookies = request.getCookies();
		byte cookie_count_flag = 0; 
		byte cookie_count = 4;
		boolean letUserLog = false;
		if(cookies != null){
			for (Cookie cookie : cookies){
				if(Cookies.COOKIE_LOGIN_USER_ID.equals(cookie.getName())){
					session.setAttribute(Sessions.SES_USER_ID, cookie.getValue());
					cookie_count_flag++;
					letUserLog = true;
				}
				if(Cookies.COOKIE_LOGIN_USER_EMAIL.equals(cookie.getName())){
					session.setAttribute(Sessions.SES_USER_EMAIL, cookie.getValue());
					cookie_count_flag++;
				}
				if(Cookies.COOKIE_LOGIN_USER_FNAME.equals(cookie.getName())){
					session.setAttribute(Sessions.SES_USER_FNAME, cookie.getValue());
					cookie_count_flag++;
				}
				if(Cookies.COOKIE_LOGIN_USER_STATE.equals(cookie.getName())){
					session.setAttribute(Sessions.SES_USER_LOGIN_STATE, cookie.getValue());
					cookie_count_flag++;
				}
			}
			if (cookie_count_flag == cookie_count && cookie_count_flag != 0 && letUserLog){
				return true;	
			} else {
				return false;	
			}
		} else {
			return false;
		}
	}
	
	
	public void logout(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		HttpSession session = request.getSession();
		session.invalidate();
		Cookie[] cookies = request.getCookies();
		if(cookies != null){
			for (Cookie cookie : cookies){
				if(Cookies.COOKIE_LOGIN_USER_ID.equals(cookie.getName())){
					cookie.setMaxAge(0);
				}
				if(Cookies.COOKIE_LOGIN_USER_EMAIL.equals(cookie.getName())){
					cookie.setMaxAge(0);
				}
				if(Cookies.COOKIE_LOGIN_USER_FNAME.equals(cookie.getName())){
					cookie.setMaxAge(0);
				}
				if(Cookies.COOKIE_LOGIN_USER_STATE.equals(cookie.getName())){
					cookie.setMaxAge(0);
				}
				response.addCookie(cookie);
			}
		}
		Seo.sendRedirect(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL), response);
	}
	
	public void login(HttpServletRequest request, HttpServletResponse response) throws JSONException, IOException, NoSuchAlgorithmException, ServletException {
		HttpSession session = request.getSession();
		String target_url = null;
		if (session.getAttribute(Sessions.SES_TARGET_URL) != null) {
			target_url = session.getAttribute(Sessions.SES_TARGET_URL).toString();
		}
		System.out.println(target_url);
		
		
		String email = Seo.getRequestVariable(request, "login-email");
		String password = Seo.getRequestVariable(request, "login-password");
		
		if (email == null || email.isEmpty() || email.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Email (Username) not provided." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger"; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		if (password == null || password.isEmpty() || password.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Password not entered." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger"; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		String hashPassword = hashPassword(password);
			
		// MongoConstants mongoConstants = new MongoConstants(getServletContext().getRealPath(""));

		// MongoClient mongoClient = MongoClients.create(mongoConstants.get_connection_string());
		MongoClient mongoClient = MongoClients.create();
		
		MongoDatabase db = mongoClient.getDatabase(MongoKeys.DB_USER);
		MongoCollection<Document> coll = db.getCollection(MongoKeys.COL_USER);

		List<Document> users = coll.find(eq(MongoKeys.USER_EMAIL, email)).into(new ArrayList<Document>());
		int num_users = users.size();
		System.out.println("Number of Users:" + num_users);
		System.out.println(users.toString());
		if (num_users == 1) {
			Document user = users.get(0);
			String objId = user.getObjectId(MongoKeys._ID).toString();
			if (hashPassword.equals(user.getString(MongoKeys.USER_PASSWORD))) {
				Cookie ck = new Cookie(Cookies.COOKIE_LOGIN_USER_ID, objId);
				ck.setMaxAge(Cookies.COOKIE_EXP);
				ck.setPath(request.getContextPath());
				ck.setHttpOnly(Cookies.COOKIE_HTTP);
				response.addCookie(ck);

				ck = new Cookie(Cookies.COOKIE_LOGIN_USER_EMAIL, email);
				ck.setMaxAge(Cookies.COOKIE_EXP);
				ck.setPath(request.getContextPath());
				ck.setHttpOnly(Cookies.COOKIE_HTTP);
				response.addCookie(ck);

				ck = new Cookie(Cookies.COOKIE_LOGIN_USER_FNAME, user.getString(MongoKeys.USER_NAME_FIRST));
				ck.setMaxAge(Cookies.COOKIE_EXP);
				ck.setPath(request.getContextPath());
				ck.setHttpOnly(Cookies.COOKIE_HTTP);
				response.addCookie(ck);

				ck = new Cookie(Cookies.COOKIE_LOGIN_USER_STATE, "log");
				ck.setMaxAge(Cookies.COOKIE_EXP);
				ck.setPath(request.getContextPath());
				ck.setHttpOnly(Cookies.COOKIE_HTTP);
				response.addCookie(ck);

				response.isCommitted();
				mongoClient.close();
				
				if (target_url != null && !target_url.equals("")) {
					Seo.sendRedirect(target_url, response);
				} else {
					Seo.sendRedirect(Seo.getSeoPath(Seo.DASHBOARD, Seo.TYPE_FULL), response);	
				}
			} else {
				System.out.println("Found invalid password");
				String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
						"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Invalid password supplied." + 
						"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
								"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_LOGIN; 
				Seo.sendRedirect(redirectURL, response);
			}
		} else {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=User not found." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
							"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_LOGIN; 
			Seo.sendRedirect(redirectURL, response);
		}

	}
	
	public void register(HttpServletRequest request, HttpServletResponse response) throws JSONException, NoSuchAlgorithmException, IOException, ServletException {	
		String email = Seo.getRequestVariable(request, "register-email");
		String password = Seo.getRequestVariable(request, "register-password");
		String re_password = Seo.getRequestVariable(request, "register-re-password");
		String fname = Seo.getRequestVariable(request, "register-first-name");
		String lname = Seo.getRequestVariable(request, "register-last-name");
		
		if (fname == null || fname.isEmpty() || fname.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=First name not entered." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
							"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_REGISTER; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		if (lname == null || lname.isEmpty() || lname.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Last name not entered." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
							"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_REGISTER; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		if (email == null || email.isEmpty() || email.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Email (Username) not provided." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
					"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_REGISTER; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		if (password == null || password.isEmpty() || password.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Password not entered." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
							"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_REGISTER; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		if (re_password == null || re_password.isEmpty() || re_password.equals("")) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Password not entered." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger" +
							"&" + Sessions.SES_USER_LOGIN_ACCORDIAN + "=" + Sessions.SES_USER_LOGIN_ACCORDIAN_REGISTER; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		if (!password.equals(re_password)) {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_REGISTER_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_REGISTER_FLAG_MSG + "=Passwords don't match." + 
					"&" + Sessions.SES_USER_REGISTER_FLAG_DEG + "=danger"; 
			Seo.sendRedirect(redirectURL, response);
		}
		
		String hashedPassword = hashPassword(password);
		
		// MongoConstants mongoConstants = new MongoConstants(getServletContext().getRealPath(""));

		MongoClient mongoClient = MongoClients.create(); // mongoConstants.get_connection_string());

		MongoDatabase db = mongoClient.getDatabase(MongoKeys.DB_USER);
		MongoCollection<Document> coll = db.getCollection(MongoKeys.COL_USER);

		List<Document> users = coll.find(eq(MongoKeys.USER_EMAIL, email)).into(new ArrayList<Document>());
		int num_users = users.size();
		
		if (num_users == 0) {
			Document user = new Document();
			user.append(MongoKeys.USER_EMAIL, email);
			user.append(MongoKeys.USER_PASSWORD, hashedPassword);
			user.append(MongoKeys.USER_NAME_FIRST, fname);
			user.append(MongoKeys.USER_NAME_LAST, lname);
			
			coll.insertOne(user);
			
			request.setAttribute("login-email", email);
			request.setAttribute("login-password", password);
			
			login(request, response);
		} else {
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_REGISTER_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_REGISTER_FLAG_MSG + "=User not found." + 
					"&" + Sessions.SES_USER_REGISTER_FLAG_DEG + "=danger"; 
			Seo.sendRedirect(redirectURL, response);
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

	public void reset_password(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException, JSONException, NoSuchAlgorithmException {
		String email = Seo.getRequestVariable(request, "login-reset-password-email");
		String password = Seo.getRequestVariable(request, "login-reset-password-password");
		String re_password = Seo.getRequestVariable(request, "login-reset-password-re-password");

		if (!email.isEmpty() && email != null) {
			// MongoConstants mongoConstants = new MongoConstants(getServletContext().getRealPath(""));

			MongoClient mongoClient = MongoClients.create(); // mongoConstants.get_connection_string());

			MongoDatabase db = mongoClient.getDatabase(MongoKeys.DB_USER);
			MongoCollection<Document> coll = db.getCollection(MongoKeys.COL_USER);

			List<Document> users = coll.find(eq(MongoKeys.USER_EMAIL, email)).into(new ArrayList<Document>());
			int num_users = users.size();
			
			// Checking if user exists
			if (num_users == 1) { 
				// User found.
				// Checking if password provided.
				if (!password.isEmpty() && !re_password.isEmpty() && password != null && re_password != null) {
					// Checking if passwords match
					if (password.equals(re_password)) {
						 // Passwords matched.
						String hashed_password = hashPassword(password);
						System.out.println(hashed_password);
						
						// BasicDBObject find_query = (BasicDBObject) eq(MongoKeys._ID, users.get(0).getObjectId(MongoKeys._ID));
						Document update_query = new Document("$set", new Document(MongoKeys.USER_PASSWORD, hashed_password));
						
						coll.findOneAndUpdate(eq(MongoKeys._ID, users.get(0).getObjectId(MongoKeys._ID)), update_query);
						
						request.setAttribute("login-email", email);
						request.setAttribute("login-password", password);
						
						login(request, response);
						
					} else {
						// Passwords don't match.
						String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
								"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Passwords  don't match." + 
								"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=warning"; 
						Seo.sendRedirect(redirectURL, response);
					}
				} else {
					// Password not provided.
					String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
							"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=New Pasword not provided." + 
							"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger"; 
					Seo.sendRedirect(redirectURL, response);	
				}
				
			} else {
				// User not found
				String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
						"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=User not found." + 
						"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger"; 
				Seo.sendRedirect(redirectURL, response);
			}
		} else {
			// Email not provided.
			String redirectURL = Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL) + "?" + Sessions.SES_USER_LOGIN_FLAG + "=" + true + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_MSG + "=Username not provided." + 
					"&" + Sessions.SES_USER_LOGIN_FLAG_DEG + "=danger"; 
			Seo.sendRedirect(redirectURL, response);
		}
	}
	
	public void userIsLoggedIn(HttpServletRequest request, HttpServletResponse response) throws JSchException, JSONException, IOException {
		
		HttpSession session = request.getSession();
		Session SSH_SESSION = null;
		
	 	BasicDBObject credentialQuery = new BasicDBObject();
		credentialQuery.put("sessionID",session.getAttribute("sessionID"));
		
		java.util.Properties configure = new java.util.Properties();
		configure.put("StrictHostKeyChecking", "no");
		JSch jsch = new JSch();
		
		//Path for private key dsworker_rsa file
		String path = request.getServletContext().getRealPath(File.separator+"WEB-INF"+File.separator+"dsworker_rsa");
		System.out.println	("KeyFile path="+path);
		jsch.addIdentity(path, "passphrase");

		MongoConstants mongoconstants = new MongoConstants(request.getServletContext().getRealPath(""));
		
		SSH_SESSION = null;
		SSH_SESSION = jsch.getSession(mongoconstants.get_ssh_user(), mongoconstants.get_ssh_host(), mongoconstants.get_ssh_port());
		SSH_SESSION.setConfig(configure);
		SSH_SESSION.connect();
		System.out.println("Connection established index.jsp...");
		
		SSH_SESSION.setPortForwardingL(mongoconstants.get_local_port(), mongoconstants.get_local_host(), mongoconstants.get_remote_port());   
		
		System.out.println("Port forwarding done...");

		// MongoClient mongoClient = new MongoClient(mongoconstants.get_local_host(), mongoconstants.get_local_port());
		MongoClient mongoClient = MongoClients.create();

		MongoDatabase db = mongoClient.getDatabase("Users");
		MongoCollection collection = db.getCollection("user_data");
	}
}
