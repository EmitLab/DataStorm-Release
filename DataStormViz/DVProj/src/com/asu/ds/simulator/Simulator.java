package com.asu.ds.simulator;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.json.JSONException;

import com.asu.ds.kepler.KeplerConstants;
import com.asu.ds.seo.utils.Seo;
import com.jcraft.jsch.Channel;
import com.jcraft.jsch.ChannelExec;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.JSchException;
import com.jcraft.jsch.Session;

@WebServlet({"/simulator", "/simulator/", "/simulator/*"})
public class Simulator extends HttpServlet {
	private static final long serialVersionUID = 1L;

    public Simulator() {
        super();
    }

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		response.getWriter().append("Served at: ").append(request.getContextPath());
		
		KeplerConstants keplerconstants;
		String host = "129.114.110.164";
		try {
			keplerconstants = new KeplerConstants(getServletContext().getRealPath(""));
			host = keplerconstants.getKeplerIP(); 
		} catch (JSONException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
		
		// String host = Seo.getRequestVariable(request, "ds-simulator-ip");	
		
		// Very good reference point.
		// https://www.pixelstech.net/article/1418375956-Remote-execute-command-in-Java-example
	
		try {
			
			String cmd = "/opt/kepler/Kepler-2.5/kepler.sh -runkar -nogui -force ~/DataStorm/ds_modules/DS_HM_FM_HMM_Integration.kar";
			String user = "cc";
			int port = 22;
			
			JSch jsch = new JSch();
			Session session = jsch.getSession(user, host, port);
			
			java.util.Properties configure = new java.util.Properties();
			configure.put("StrictHostKeyChecking", "no");
			
			// String path = request.getServletContext().getRealPath(File.separator+"WEB-INF" + File.separator+"ds-twitter.pem");
			String path = request.getServletContext().getRealPath(File.separator+"WEB-INF" + File.separator+"dsworker_rsa");
			System.out.println	("KeyFile path=" + path);
			jsch.addIdentity(path, "passphrase");
			
			session.setConfig(configure);
			session.connect();
			
			Channel channel = session.openChannel("exec");
            ((ChannelExec)channel).setCommand(cmd);
            channel.setInputStream(null);
            ((ChannelExec)channel).setErrStream(System.err);
             
            InputStream input = channel.getInputStream();
            channel.connect();
             
            System.out.println("Channel Connected to machine " + host + " server with command: " + cmd ); 
             
            InputStreamReader inputReader = new InputStreamReader(input);
            BufferedReader bufferedReader = new BufferedReader(inputReader);
            String line = null;
             
            while((line = bufferedReader.readLine()) != null){
                System.out.println(line);
            }
            bufferedReader.close();
            inputReader.close();
             
            channel.disconnect();
            session.disconnect();
			
		} catch (Exception e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		
		}
		
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
