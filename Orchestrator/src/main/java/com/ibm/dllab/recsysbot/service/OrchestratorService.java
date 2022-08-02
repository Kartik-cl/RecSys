package com.ibm.dllab.recsysbot.service;

import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Component;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.ibm.dllab.recsysbot.model.AskSmeListRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackHistoryRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackHistoryResponseModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackProcessedRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackResponseModel;
import com.ibm.dllab.recsysbot.model.ChatHistoryRequestModel;
import com.ibm.dllab.recsysbot.model.ChatHistoryResponseModel;
import com.ibm.dllab.recsysbot.model.ChatRequestModel;
import com.ibm.dllab.recsysbot.model.ChatResponseModel;
import com.ibm.dllab.recsysbot.model.SMEDeleteResponseModel;
import com.ibm.dllab.recsysbot.model.SMEResponseModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateRequestModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateResponseModel;
import com.ibm.dllab.recsysbot.model.smeRequestModel;

@Component
public interface OrchestratorService {

	public ChatResponseModel getChatResponse(ChatRequestModel chatRequest, Instant timestamp, String chatRequestID)
			throws JsonProcessingException;

	public ChatFeedbackResponseModel saveChatFeedback(ChatFeedbackRequestModel chatFeedback, Instant timestamp)
			throws JsonProcessingException;

	public ChatHistoryResponseModel getChatHistoryResponse(ChatHistoryRequestModel chatHistoryRequest)
			throws JsonProcessingException;

	public SMEResponseModel getsmeResponse(smeRequestModel smeRequest, Instant timestamp)
			throws JsonProcessingException;

	public HashMap<String, Object> getsmeList(AskSmeListRequestModel askSmeRequest) throws JsonProcessingException;

	public SmeUpdateResponseModel smeMarkAnswered(SmeUpdateRequestModel sme_update_request)
			throws JsonProcessingException;

	public ChatFeedbackHistoryResponseModel getChatFeedbackHistory(ChatFeedbackHistoryRequestModel chatFeedbackHistoryRequest) throws JsonProcessingException;

	public ChatFeedbackResponseModel markFeedbackProcessed(ChatFeedbackProcessedRequestModel request)
			throws JsonProcessingException;


	public ChatFeedbackResponseModel clearFeedbackHistory() throws JsonProcessingException;

	public SMEResponseModel clearSMEAll() throws JsonProcessingException;

	public Map<String, Object> clearChatHistory() throws JsonProcessingException;

	public SMEDeleteResponseModel clearSME(String userID, List<String> ids) throws JsonProcessingException;

}
