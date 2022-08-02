package com.ibm.dllab.recsysbot.model;

import java.util.List;

public class ChatHistoryResponseModel {
	private String userID;
	private String conversationID;
	private List<ChatModel> results;

	public String getConversationID() {
		return conversationID;
	}

	public void setConversationID(String conversationID) {
		this.conversationID = conversationID;
	}

	public String getUserID() {
		return userID;
	}

	public void setUserID(String userID) {
		this.userID = userID;
	}

	public List<ChatModel> getResults() {
		return results;
	}

	public void setResults(List<ChatModel> results) {
		this.results = results;
	}
	
}