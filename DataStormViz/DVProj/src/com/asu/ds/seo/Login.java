package com.asu.ds.seo;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.asu.ds.controller.LoginController;
import com.asu.ds.seo.utils.Seo;
import com.asu.ds.seo.utils.SessionKey;

@WebServlet({"/login", "/login/"})
public class Login extends HttpServlet {
	private static final long serialVersionUID = 1L;


	public Login() {
		super();
	}
	
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		LoginController loginController = new LoginController();
		
		String login_mode = Seo.getRequestVariable(request, SessionKey.LOGIN_MODE);
		try {
			if (login_mode != null && !login_mode.isEmpty()) {
				if (login_mode.equals(SessionKey.LOGIN_MODE_LOGIN)) {
					loginController.login(request, response);
				}
				if(login_mode.equals(SessionKey.LOGIN_MODE_LOGOUT)) {
					System.out.println("Logout");
					loginController.logout(request, response);
				}
				if (login_mode.equals(SessionKey.LOGIN_MODE_REGISTER)) {
					loginController.register(request, response);
				}
				if(login_mode.equals(SessionKey.LOGIN_MODE_RESET_PASSWORD)) {
					loginController.reset_password(request, response);
				}
			} else {
				Boolean flag = loginController.isLoggedIn(request, response);
				
				if (flag) {
					Seo.sendRedirect(Seo.getSeoPath(Seo.DASHBOARD, Seo.TYPE_FULL), response);
				} else {
					Seo.forward(Seo.getSeoPath(Seo.LOGIN, Seo.TYPE_JSP), request, response);	
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		}	
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
