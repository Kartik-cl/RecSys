package com.ibm.dllab.recsysbot.model;

import java.util.ArrayList;
import java.util.List;

public class ChatResponseModel {
	private String conversationID;
	private String chatRequestID;
	private String chatResponseID;
	private List<String> outputMessages;
	private List<String> type;
	private Object data;
	private PredicateModel nextAttribute;
	private UserModel userDetail;
	private List<ProductModel> products;

	public List<ProductModel> getProducts() {
		return products;
	}

	public void setProducts(List<ProductModel> products) {
		this.products = products;
	}

	public UserModel getUserDetail() {
		return userDetail;
	}

	public void setUserDetail(UserModel userDetail) {
		this.userDetail = userDetail;
	}

	public PredicateModel getNextAttribute() {
		return nextAttribute;
	}

	public void setNextAttribute(PredicateModel nextAttribute) {
		this.nextAttribute = nextAttribute;
	}

	public String getConversationID() {
		return conversationID;
	}

	public void setConversationID(String conversationID) {
		this.conversationID = conversationID;
	}

	public String getChatRequestID() {
		return chatRequestID;
	}

	public void setChatRequestID(String chatRequestID) {
		this.chatRequestID = chatRequestID;
	}

	public String getChatResponseID() {
		return chatResponseID;
	}

	public void setChatResponseID(String chatResponseID) {
		this.chatResponseID = chatResponseID;
	}

	public List<String> getOutputMessages() {
		return outputMessages;
	}

	public void setOutputMessages(List<String> outputMessages) {
		this.outputMessages = outputMessages;
	}

	public Object getData() {
		return data;
	}

	public void setData(Object data) {
		this.data = data;
	}

	public List<String> getType() {
		return type;
	}

	// DO NOT DELETE THIS
	public void setType(String type) {
		if (this.type == null) {
			this.type = new ArrayList<String>();
		}

		if (!this.type.contains(type)) {
			this.type.add(type);
		}
	}
}
