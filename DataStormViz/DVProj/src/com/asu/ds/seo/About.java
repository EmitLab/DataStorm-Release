package com.asu.ds.seo;

import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.asu.ds.seo.utils.Seo;

@WebServlet({"/about", "/about/", "/about/*"})
public class About extends HttpServlet {
	private static final long serialVersionUID = 1L;

    public About() {
        super();
    }

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		Seo.forward(Seo.getSeoPath(Seo.ABOUT, Seo.TYPE_JSP), request, response);
	}

	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		doGet(request, response);
	}

}
