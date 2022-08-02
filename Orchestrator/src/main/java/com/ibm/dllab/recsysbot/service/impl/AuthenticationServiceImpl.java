package com.ibm.dllab.recsysbot.service.impl;

import static com.cloudant.client.api.query.Expression.eq;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.cloudant.client.api.Database;
import com.cloudant.client.api.query.QueryBuilder;
import com.cloudant.client.api.query.QueryResult;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.ibm.dllab.recsysbot.db.CloudantManager;
import com.ibm.dllab.recsysbot.model.UserModel;
import com.ibm.dllab.recsysbot.service.AuthenticationService;
import com.ibm.dllab.recsysbot.util.Constants;

@Component
public class AuthenticationServiceImpl implements AuthenticationService {
	
	@Autowired
	CloudantManager cloudantManager;
	
	@Value(Constants.CLOUDANT_USER_DATABASE)
	private String userDatabase;
	
	private List<UserModel> validateUser(String userId) throws JsonProcessingException {
		Database db = cloudantManager.getDatabase(userDatabase);
		QueryResult<UserModel> userModel = db.query(
				new QueryBuilder(eq("user_name", userId)).build(), UserModel.class);
		return userModel.getDocs();
	}

	@Override
	public UserModel authenticate(String userId) throws JsonProcessingException {
		UserModel loggedInUser = new UserModel();
	
		List<UserModel> users = validateUser(userId);
		if(users != null && users.size() > 0) {
			loggedInUser = users.get(0);
		}
		return loggedInUser;
	}

}
