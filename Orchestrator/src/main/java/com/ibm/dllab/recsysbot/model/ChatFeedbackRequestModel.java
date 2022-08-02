package com.ibm.dllab.recsysbot.model;

import java.time.Instant;

public class ChatFeedbackRequestModel {
	private String _id;
	private String _rev;
	private String userID;
	private int channelID;
	private Instant timestamp;
	private String conversationID;
	private String chatRequestID;
	private String chatResponseID;
	private String documentID;
	private String documentTitle;
	private Double documentConfidenceScore;
	private int feedbackRating;
	private int binaryFeedback;
	private String feedbackMessage;
	private String status;

	public String getUserID() {
		return userID;
	}

	public void setUserID(String userID) {
		this.userID = userID;
	}

	public int getChannelID() {
		return channelID;
	}

	public void setChannelID(int channelID) {
		this.channelID = channelID;
	}

	public String getConversationID() {
		return conversationID;
	}

	public void setConversationID(String conversationID) {
		this.conversationID = conversationID;
	}

	public String getChatResponseID() {
		return chatResponseID;
	}

	public void setChatResponseID(String chatResponseID) {
		this.chatResponseID = chatResponseID;
	}

	public int getFeedbackRating() {
		return feedbackRating;
	}

	public void setFeedbackRating(int feedbackRating) {
		this.feedbackRating = feedbackRating;
	}

	public int getBinaryFeedback() {
		return binaryFeedback;
	}

	public void setBinaryFeedback(int binaryFeedback) {
		this.binaryFeedback = binaryFeedback;
	}

	public String getFeedbackMessage() {
		return feedbackMessage;
	}

	public void setFeedbackMessage(String feedbackMessage) {
		this.feedbackMessage = feedbackMessage;
	}

	public String getDocumentID() {
		return documentID;
	}

	public void setDocumentID(String documentID) {
		this.documentID = documentID;
	}

	public String getDocumentTitle() {
		return documentTitle;
	}

	public void setDocumentTitle(String documentTitle) {
		this.documentTitle = documentTitle;
	}

	public String getChatRequestID() {
		return chatRequestID;
	}

	public void setChatRequestID(String chatRequestID) {
		this.chatRequestID = chatRequestID;
	}

	public Instant getTimestamp() {
		return timestamp;
	}

	public void setTimestamp(Instant timestamp) {
		this.timestamp = timestamp;
	}

	public Double getDocumentConfidenceScore() {
		return documentConfidenceScore;
	}

	public void setDocumentConfidenceScore(Double documentConfidenceScore) {
		this.documentConfidenceScore = documentConfidenceScore;
	}

	public String get_id() {
		return _id;
	}

	public void set_id(String _id) {
		this._id = _id;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

	public String get_rev() {
		return _rev;
	}

	public void set_rev(String _rev) {
		this._rev = _rev;
	}

}
