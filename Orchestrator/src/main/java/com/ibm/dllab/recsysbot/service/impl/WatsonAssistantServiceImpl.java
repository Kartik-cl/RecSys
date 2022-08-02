package com.ibm.dllab.recsysbot.service.impl;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.ibm.dllab.recsysbot.service.WatsonAssistantService;
import com.ibm.dllab.recsysbot.util.Constants;
import com.ibm.watson.developer_cloud.assistant.v1.Assistant;
import com.ibm.watson.developer_cloud.assistant.v1.model.Context;
import com.ibm.watson.developer_cloud.assistant.v1.model.InputData;
import com.ibm.watson.developer_cloud.assistant.v1.model.MessageOptions;
import com.ibm.watson.developer_cloud.assistant.v1.model.MessageResponse;

@Component
public class WatsonAssistantServiceImpl implements WatsonAssistantService {

	@Value(Constants.WA_ENDPOINT_URL)
	private String endpointURL;

	@Value(Constants.WA_USERNAME)
	private String username;

	@Value(Constants.WA_PASSWORD)
	private String password;

	@Value(Constants.WA_WORKSPACE_ID)
	private String workspaceID;

	@Override
	public MessageResponse getResponse(String message, Context context) {
		Assistant service = new Assistant(Constants.WA_VERSION_DATE);
		service.setUsernameAndPassword(username, password);

		InputData input = new InputData.Builder(message).build();
		MessageOptions options = new MessageOptions.Builder(workspaceID).input(input).context(context).build();
		MessageResponse response = service.message(options).execute();

		return response;
	}

}
