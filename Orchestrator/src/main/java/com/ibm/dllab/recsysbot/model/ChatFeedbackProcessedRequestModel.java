package com.ibm.dllab.recsysbot.model;

import java.util.List;

public class ChatFeedbackProcessedRequestModel {
	private List<UnderscoreID> processed;

	public List<UnderscoreID> getProcessed() {
		return processed;
	}

	public void setProcessed(List<UnderscoreID> processed) {
		this.processed = processed;
	}
}
