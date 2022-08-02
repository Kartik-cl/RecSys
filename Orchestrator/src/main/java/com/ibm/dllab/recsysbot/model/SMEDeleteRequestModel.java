package com.ibm.dllab.recsysbot.model;

import java.util.List;

public class SMEDeleteRequestModel {
	private String userID;
	private List<String> ids;

	public String getUserID() {
		return userID;
	}

	public void setUserID(String userID) {
		this.userID = userID;
	}

	public List<String> getIds() {
		return ids;
	}

	public void setIds(List<String> ids) {
		this.ids = ids;
	}
}
