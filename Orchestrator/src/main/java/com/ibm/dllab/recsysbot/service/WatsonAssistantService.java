package com.ibm.dllab.recsysbot.service;

import com.ibm.watson.developer_cloud.assistant.v1.model.Context;
import com.ibm.watson.developer_cloud.assistant.v1.model.MessageResponse;

public interface WatsonAssistantService {
	MessageResponse getResponse(String message, Context context);
}
