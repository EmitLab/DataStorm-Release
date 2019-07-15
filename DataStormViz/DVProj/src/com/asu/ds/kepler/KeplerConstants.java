package com.asu.ds.kepler;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.json.JSONException;
import org.json.JSONObject;

import com.asu.ds.seo.utils.Seo;

public class KeplerConstants {
	public JSONObject CONFIG = new JSONObject();

	public KeplerConstants() {

	}

	public KeplerConstants(String context_path) throws JSONException, IOException {
		String file_path = Seo.getKeplerConfigFilePath(context_path); 

		this.CONFIG = parseJSONFile(file_path);
		System.out.println(this.CONFIG.toString());
	}

	public static JSONObject parseJSONFile(String filename) throws JSONException, IOException {
		String content = new String(Files.readAllBytes(Paths.get(filename)));
		return new JSONObject(content);
	}
	
	public String getKeplerIP() throws JSONException {
		return this.CONFIG.getString("KEPLER_IP");
	}
}
