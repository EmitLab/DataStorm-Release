package com.asu.ds.seo;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import com.asu.ds.Sessions.Sessions;
import com.asu.ds.controller.LoginController;
import com.asu.ds.seo.utils.*;

@WebServlet({"/dashboard", "/dashboard/"})
public class Dashboard extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    public Dashboard() {
        super();
    }

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		
		LoginController loginController = new LoginController();
		Boolean flag = loginController.isLoggedIn(request, response);
		
		if (flag) {
			Seo.forward(Seo.getSeoPath(Seo.DASHBOARD, Seo.TYPE_JSP), request, response);
		} else {
			String target_url = Seo.getSeoPath(Seo.DASHBOARD, Seo.TYPE_FULL);
			
			HttpSession session = request.getSession();
			session.setAttribute(Sessions.SES_TARGET_URL, target_url);
			response.sendRedirect(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_FULL));
		}
	}
	
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
