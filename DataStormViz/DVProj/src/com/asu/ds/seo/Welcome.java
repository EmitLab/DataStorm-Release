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
import com.asu.ds.seo.utils.Seo;

@WebServlet({"/welcome", "/welcome/", "/welcome/*"})
public class Welcome extends HttpServlet {
	private static final long serialVersionUID = 1L;

    public Welcome() {
        super();
    }

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		LoginController loginController = new LoginController();
		Boolean flag = loginController.isLoggedIn(request, response);
		
		Seo.forward(Seo.getSeoPath(Seo.WELCOME, Seo.TYPE_JSP), request, response);
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
