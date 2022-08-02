package com.ibm.dllab.recsysbot.model;

public class ChatFeedbackHistoryRequestModel {
	private String userID;
	private String documentID;

	public String getUserID() {
		return userID;
	}

	public void setUserID(String userID) {
		this.userID = userID;
	}

	public String getDocumentID() {
		return documentID;
	}

	public void setDocumentID(String documentID) {
		this.documentID = documentID;
	}

}
