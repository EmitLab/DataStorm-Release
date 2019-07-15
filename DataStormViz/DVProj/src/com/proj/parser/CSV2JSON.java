package com.proj.parser;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.FileWriter;
import java.util.*;
@WebServlet("/CSV2JSON")
public class CSV2JSON extends HttpServlet {
	private static final long serialVersionUID = 1L;

	public CSV2JSON() {
		super();
	}

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		
		// Calling type: /DVProj/CSV2JSON?useMode=4
		
		try {
			String[] dateArr = {"20160701","20160702"};
			String[] timeArr = {"0","3","6","9","12","15","18","21"};
			String[] modeArr = {"lat","lng","rain","U", "V"};
			int useMode = Integer.parseInt(request.getParameter("useMode").toString());

			String basePath   = "/Users/ygarg/git/DataStorm-Viz/DVProj/WebContent/files/";
			String targetPath = basePath + modeArr[useMode] + ".json";

			int nDates = dateArr.length;
			int nTimes = timeArr.length;

			String fileName = null;
			String filePath = null;

			int nRows = 0;
			int nCols = 0;
			int gridIDX = 1;
			
			BufferedReader br = null;
			String line = "";
			
			JSONObject mode = new JSONObject();
			JSONArray data = new JSONArray();
			JSONArray minArr = new JSONArray();
			JSONArray maxArr = new JSONArray();
			
			for (int i = 0; i < nDates; i++) {
				for (int j = 0; j < nTimes; j++) {
					double minNum = Double.MAX_VALUE;
					double maxNum = Double.MIN_VALUE;
					
					fileName = dateArr[i] + "_" + timeArr[j] + "." + modeArr[useMode] + ".csv";
					filePath = basePath + modeArr[useMode] + "/" + fileName;
					System.out.println(filePath);

					gridIDX = 1;
					JSONObject jObject = new JSONObject();

					br = new BufferedReader(new FileReader(filePath));
					while ((line = br.readLine()) != null) {
						String[] vals = line.split(",");
						int nVals = vals.length;
						nCols = nVals;
						for(int v = 0; v < nVals; v++) {
							jObject.put("g" + Integer.toString(gridIDX), vals[v]);
							gridIDX++;
							
							minNum = (Double.parseDouble(vals[v]) < minNum) ? Double.parseDouble(vals[v]) : minNum;
							maxNum = (Double.parseDouble(vals[v]) > maxNum) ? Double.parseDouble(vals[v]) : maxNum;
						}
					}

					data.put(jObject);
					minArr.put(minNum);
					maxArr.put(maxNum);

				}
			}

			JSONArray dates = new JSONArray(Arrays.asList(dateArr));
			JSONArray times = new JSONArray(Arrays.asList(timeArr));
			
			mode.put("name", modeArr[useMode]);
			mode.put("dates", dates);
			mode.put("times", times);
			mode.put("nTimeStamp", (nDates*nTimes));
			
			mode.put("nRow", ((gridIDX - 1)/nCols));
			mode.put("nCol", nCols);
			
			mode.put("data", data);
			mode.put("min", minArr);
			mode.put("max", maxArr);

			System.out.println(minArr);
			System.out.println(mode.toString());
			FileWriter fw = new FileWriter(targetPath);
			fw.write(mode.toString());
			fw.close();
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		response.getWriter().append("Served at: ").append(request.getContextPath());
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
