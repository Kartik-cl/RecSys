package com.ibm.dllab.recsysbot.db;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.cloudant.client.api.ClientBuilder;
import com.cloudant.client.api.CloudantClient;
import com.cloudant.client.api.Database;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.ibm.dllab.recsysbot.util.Constants;

@Component
public class CloudantManager {
	Logger logger = LoggerFactory.getLogger(CloudantManager.class);
	ObjectMapper objectMapper = new ObjectMapper();

	private CloudantClient cloudantClient = null;

	@Value(Constants.CLOUDANT_ACCOUNT)
	private String account;

	@Value(Constants.CLOUDANT_USERNAME)
	private String username;

	@Value(Constants.CLOUDANT_PASSWORD)
	private String password;

	public synchronized Database getDatabase(String database) throws JsonProcessingException {
		try {
			if (cloudantClient == null) {
				cloudantClient = ClientBuilder.account(account).username(username).password(password).build();
			}

			return cloudantClient.database(database, true);
		} catch (Exception e) {
			logger.error("An error occurred with Cloudant");
			logger.error(objectMapper.writeValueAsString(e));

			return null;
		}
	}

	public void dropDB(String database) throws JsonProcessingException {
		try {
			if (cloudantClient == null) {
				cloudantClient = ClientBuilder.account(account).username(username).password(password).build();
			}

			cloudantClient.deleteDB(database);
		} catch (Exception e) {
			logger.error("An error occurred with Cloudant");
			logger.error(objectMapper.writeValueAsString(e));
		}
		
	}
}