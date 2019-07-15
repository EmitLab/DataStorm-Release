package com.asu.ds.db.mongo;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.json.JSONException;
import org.json.JSONObject;

import com.asu.ds.seo.utils.Seo;

public class MongoConstants {

	/*
	 * MONGO JAVA DRIVER DOWNLOAD : https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/3.9.1/mongo-java-driver-3.9.1.jar
	 * */

	/*
	public String SSH_USER = "cc";
	public String SSH_PASSWORD = "";
	public String SSH_HOST = "129.114.33.117";
	public Integer SSH_PORT = 22;

	public String LOCAL_HOST = "127.0.0.1";
	public String REMOTE_HOST = "129.114.33.117";
	public Integer LOCAL_PORT = 8988;
	public Integer REMOTE_PORT = 27017; // Default mongodb port
	 */

	public JSONObject MONGO_CONFIG = new JSONObject(); 

	public MongoConstants() throws JSONException, IOException{

		/*
		this.SSH_HOST = this.MONGO_CONFIG.getString("SSH_USER");
		this.SSH_PORT = this.MONGO_CONFIG.getInt("SSH_PORT");
		this.SSH_PASSWORD = this.MONGO_CONFIG.getString("SSH_PASSWORD");
		this.SSH_USER = this.MONGO_CONFIG.getString("SSH_USER");

		this.LOCAL_HOST = this.MONGO_CONFIG.getString("LOCAL_HOST");
		this.LOCAL_PORT = this.MONGO_CONFIG.getInt("LOCAL_PORT");
		this.REMOTE_HOST = this.MONGO_CONFIG.getString("REMOTE_HOST");
		this.REMOTE_PORT = this.MONGO_CONFIG.getInt("REMOTE_PORT");
		 */

	}
	public MongoConstants(String context_path) throws JSONException, IOException {
		String file_path = Seo.getMongoConfigFilePath(context_path); 

		this.MONGO_CONFIG = parseJSONFile(file_path);
	}

	public static JSONObject parseJSONFile(String filename) throws JSONException, IOException {
		String content = new String(Files.readAllBytes(Paths.get(filename)));
		return new JSONObject(content);
	}

	public String get_connection_string() throws JSONException {
		return "mongodb://" + this.get_local_host() + ":" + Integer.toString(this.get_local_port());
	}
	
	public String get_ssh_user() throws JSONException {
		return this.MONGO_CONFIG.getString("SSH_USER");
	}

	public String get_ssh_host() throws JSONException {
		return this.MONGO_CONFIG.getString("SSH_HOST");
	}

	public int get_ssh_port() throws JSONException {
		return this.MONGO_CONFIG.getInt("SSH_PORT");
	}

	public String get_ssh_password() throws JSONException {
		return this.MONGO_CONFIG.getString("SSH_PASSWORD");
	}

	public String get_local_host() throws JSONException {
		return this.MONGO_CONFIG.getString("LOCAL_HOST");
	}

	public int get_local_port() throws JSONException {
		return this.MONGO_CONFIG.getInt("LOCAL_PORT");
	}

	public String get_remote_host() throws JSONException {
		return this.MONGO_CONFIG.getString("REMOTE_HOST");
	}

	public int get_remote_port() throws JSONException {
		return this.MONGO_CONFIG.getInt("REMOTE_PORT");
	}
}
