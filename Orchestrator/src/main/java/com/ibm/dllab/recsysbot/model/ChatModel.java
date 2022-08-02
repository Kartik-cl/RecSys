package com.ibm.dllab.recsysbot.model;

import java.time.Instant;

public class ChatModel {
	private String userID;
	private String conversationID;
	private Instant timestamp;
	private String chatType;
	private ChatRequestModel chatRequest;
	private ChatResponseModel chatResponse;

	public String getConversationID() {
		return conversationID;
	}

	public void setConversationID(String conversationID) {
		this.conversationID = conversationID;
	}

	public Instant getTimestamp() {
		return timestamp;
	}

	public void setTimestamp(Instant timestamp) {
		this.timestamp = timestamp;
	}

	public String getChatType() {
		return chatType;
	}

	public void setChatType(String chatType) {
		this.chatType = chatType;
	}

	public ChatRequestModel getChatRequest() {
		return chatRequest;
	}

	public void setChatRequest(ChatRequestModel chatRequest) {
		this.chatRequest = chatRequest;
	}

	public ChatResponseModel getChatResponse() {
		return chatResponse;
	}

	public void setChatResponse(ChatResponseModel chatResponse) {
		this.chatResponse = chatResponse;
	}

	public String getUserID() {
		return userID;
	}

	public void setUserID(String userID) {
		this.userID = userID;
	}

}
