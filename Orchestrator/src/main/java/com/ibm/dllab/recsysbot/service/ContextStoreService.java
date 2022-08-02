package com.ibm.dllab.recsysbot.service;

import com.ibm.watson.developer_cloud.assistant.v1.model.Context;

public interface ContextStoreService {

	public void updateContext(String conversationID, Context context);

	public Context getContext(String coversationID);
}
