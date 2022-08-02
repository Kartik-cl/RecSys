package com.ibm.dllab.recsysbot;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

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
import com.ibm.dllab.recsysbot.model.SMEDeleteRequestModel;
import com.ibm.dllab.recsysbot.model.SMEDeleteResponseModel;
import com.ibm.dllab.recsysbot.model.SMEResponseModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateRequestModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateResponseModel;
import com.ibm.dllab.recsysbot.model.smeRequestModel;
import com.ibm.dllab.recsysbot.service.OrchestratorService;

@RestController
@CrossOrigin(origins = "*")
@RequestMapping(path = "/api/v1")
public class WecoAPIs {

	@Autowired
	OrchestratorService orchestratorService;

	@RequestMapping(value = "/time", method = RequestMethod.GET, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public String getTime(@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		return "{\"ServerTime\": \"" + Instant.now() + "\"}";
	}

	@RequestMapping(value = "/chat", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public ChatResponseModel chat(@RequestBody ChatRequestModel chatRequest, @RequestHeader HttpHeaders headers)
			throws JsonProcessingException {
		ChatResponseModel chatResponse = orchestratorService.getChatResponse(chatRequest, Instant.now(),
				UUID.randomUUID().toString());
		return chatResponse;
	}

	@RequestMapping(value = "/chat/history", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public ChatHistoryResponseModel chatHistory(@RequestBody ChatHistoryRequestModel chatHistoryRequest,
			@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		ChatHistoryResponseModel chatHistoryResponse = orchestratorService.getChatHistoryResponse(chatHistoryRequest);
		return chatHistoryResponse;
	}
	
	@RequestMapping(value = "/chat/feedback", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public ChatFeedbackResponseModel chatFeedback(@RequestBody ChatFeedbackRequestModel chatFeedback,
			@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		ChatFeedbackResponseModel chatFeedbackResponse = orchestratorService.saveChatFeedback(chatFeedback,
				Instant.now());
		return chatFeedbackResponse;
	}

	@RequestMapping(value = "/chat/feedback/history", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public ChatFeedbackHistoryResponseModel chatFeedbackHistory(
			@RequestBody ChatFeedbackHistoryRequestModel chatFeedbackHistoryRequest, @RequestHeader HttpHeaders headers)
			throws JsonProcessingException {
		ChatFeedbackHistoryResponseModel chatFeedbackHistoryResponse = orchestratorService
				.getChatFeedbackHistory(chatFeedbackHistoryRequest);
		return chatFeedbackHistoryResponse;
	}

	@RequestMapping(value = "/chat/feedback/processed", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public ChatFeedbackResponseModel chatFeedbackHistory(
			@RequestBody ChatFeedbackProcessedRequestModel feedbackProcessedRequest, @RequestHeader HttpHeaders headers)
			throws JsonProcessingException {
		ChatFeedbackResponseModel feedbackProcessedResponse = orchestratorService
				.markFeedbackProcessed(feedbackProcessedRequest);
		return feedbackProcessedResponse;
	}

	@RequestMapping(value = "/sme/save", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public SMEResponseModel smeStore(@RequestBody smeRequestModel smeRequest, @RequestHeader HttpHeaders headers)
			throws JsonProcessingException {
		SMEResponseModel smeResponse = orchestratorService.getsmeResponse(smeRequest, Instant.now());
		return smeResponse;
	}

	@RequestMapping(value = "/sme/list", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public HashMap<String, Object> smeList(@RequestBody AskSmeListRequestModel askSmeRequest,
			@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		HashMap<String, Object> sme_list = orchestratorService.getsmeList(askSmeRequest);
		return sme_list;
	}

	@RequestMapping(value = "/sme/answered", method = RequestMethod.POST, consumes = MediaType.APPLICATION_JSON_UTF8_VALUE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public SmeUpdateResponseModel smeUpdate(@RequestBody SmeUpdateRequestModel sme_update_request,
			@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		SmeUpdateResponseModel sme_update_status = orchestratorService.smeMarkAnswered(sme_update_request);
		return sme_update_status;
	}
	
	@RequestMapping(value = "/chat/history", method = RequestMethod.DELETE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public Map<String, Object> chat(@RequestHeader HttpHeaders headers)
			throws JsonProcessingException {
		Map<String, Object> response = orchestratorService.clearChatHistory();
		return response;
	}

	@RequestMapping(value = "/chat/feedback/history", method = RequestMethod.DELETE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public ChatFeedbackResponseModel feedbackClear(@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		ChatFeedbackResponseModel chatFeedbackResponse = orchestratorService.clearFeedbackHistory();
		return chatFeedbackResponse;
	}
	
	@RequestMapping(value = "/sme/all", method = RequestMethod.DELETE, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public SMEResponseModel clearSMEAll(@RequestHeader HttpHeaders headers) throws JsonProcessingException {
		SMEResponseModel smeResponse = orchestratorService.clearSMEAll();
		return smeResponse;
	}
	
	@RequestMapping(value = "/sme/delete", method = RequestMethod.POST, produces = MediaType.APPLICATION_JSON_UTF8_VALUE)
	public SMEDeleteResponseModel clearSMESpecific(@RequestBody SMEDeleteRequestModel requestModel, @RequestHeader HttpHeaders headers) throws JsonProcessingException {
		SMEDeleteResponseModel smeDeleteResponse = orchestratorService.clearSME(requestModel.getUserID(), requestModel.getIds());
		return smeDeleteResponse;
	}
}
