package com.ibm.dllab.recsysbot.service.impl;

import java.util.concurrent.TimeUnit;

import org.springframework.stereotype.Component;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.ibm.dllab.recsysbot.service.ContextStoreService;
import com.ibm.watson.developer_cloud.assistant.v1.model.Context;

@Component
public class ContextStoreServiceImpl implements ContextStoreService {

	private static Cache<String, Context> contextStore = Caffeine.newBuilder().maximumSize(1000)
			.expireAfterAccess(1, TimeUnit.HOURS).build();

	public void updateContext(String conversationID, Context context) {
		contextStore.put(conversationID, context);
	}

	public Context getContext(String conversationID) {
		return contextStore.getIfPresent(conversationID);
	}
}
