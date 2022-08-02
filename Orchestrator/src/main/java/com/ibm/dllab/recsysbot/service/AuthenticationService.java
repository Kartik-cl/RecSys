package com.ibm.dllab.recsysbot.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.ibm.dllab.recsysbot.model.UserModel;


public interface AuthenticationService {
	public UserModel authenticate(String userId)  throws JsonProcessingException;
}
