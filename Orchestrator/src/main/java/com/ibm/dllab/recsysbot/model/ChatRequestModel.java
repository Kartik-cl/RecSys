package com.ibm.dllab.recsysbot.model;

import java.util.HashMap;

public class ChatRequestModel {
	private String userID;
	private Integer channelID;
	private String conversationID;
	private String inputMessage;
	private String chatRequestID;
	private HashMap<String, Object> data;
	private HashMap<String, Object> product;


	public HashMap<String, Object> getData() {
		return data;
	}

	public void setData(HashMap<String, Object> data) {
		this.data = data;
	}


	public String getUserID() {
		return userID;
	}

	public void setUserID(String userID) {
		this.userID = userID;
	}

	public Integer getChannelID() {
		return channelID;
	}

	public void setChannelID(Integer channelID) {
		this.channelID = channelID;
	}

	public String getConversationID() {
		return conversationID;
	}

	public void setConversationID(String conversationID) {
		this.conversationID = conversationID;
	}

	public String getInputMessage() {
		return inputMessage;
	}

	public void setInputMessage(String inputMessage) {
		this.inputMessage = inputMessage;
	}

	public String getChatRequestID() {
		return chatRequestID;
	}

	public void setChatRequestID(String requestID) {
		this.chatRequestID = requestID;
	}

	public HashMap<String, Object> getProduct() {
		return product;
	}

	public void setProduct(HashMap<String, Object> product) {
		this.product = product;
	}
}
