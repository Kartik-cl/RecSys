package com.ibm.dllab.recsysbot.service.impl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.ibm.dllab.recsysbot.db.CloudantManager;
import com.ibm.dllab.recsysbot.service.ChatHistoryStoreService;

@Component
public class ChatHistoryStoreServiceImpl implements ChatHistoryStoreService {

	@Autowired
	CloudantManager cloudantManager;

	// TODO: concrete implementation of ChatHistoryStoreService
}
