package com.ibm.dllab.recsysbot.model;

import java.util.List;

public class ChatFeedbackHistoryResponseModel {
	private String userID;
	private String documentID;
	private List<ChatFeedbackRequestModel> results;

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

	public List<ChatFeedbackRequestModel> getResults() {
		return results;
	}

	public void setResults(List<ChatFeedbackRequestModel> results) {
		this.results = results;
	}

}
