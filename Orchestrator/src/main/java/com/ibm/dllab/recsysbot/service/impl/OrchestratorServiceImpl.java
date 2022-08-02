package com.ibm.dllab.recsysbot.service.impl;

import static com.cloudant.client.api.query.Expression.eq;
import static com.cloudant.client.api.query.Expression.regex;
import static com.cloudant.client.api.query.Operation.and;

import java.io.IOException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.json.Json;
import javax.json.JsonArray;
import javax.json.JsonArrayBuilder;
import javax.json.JsonBuilderFactory;
import javax.json.JsonObject;
import javax.json.JsonObjectBuilder;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;
import org.yaml.snakeyaml.Yaml;

import com.cloudant.client.api.Database;
import com.cloudant.client.api.query.PredicateExpression;
import com.cloudant.client.api.query.PredicatedOperation;
import com.cloudant.client.api.query.QueryBuilder;
import com.cloudant.client.api.query.QueryResult;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.google.gson.Gson;
import com.google.gson.internal.LinkedTreeMap;
import com.ibm.dllab.recsysbot.db.CloudantManager;
import com.ibm.dllab.recsysbot.model.AskSmeListRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackHistoryRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackHistoryResponseModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackProcessedRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackRequestModel;
import com.ibm.dllab.recsysbot.model.ChatFeedbackResponseModel;
import com.ibm.dllab.recsysbot.model.ChatHistoryRequestModel;
import com.ibm.dllab.recsysbot.model.ChatHistoryResponseModel;
import com.ibm.dllab.recsysbot.model.ChatModel;
import com.ibm.dllab.recsysbot.model.ChatRequestModel;
import com.ibm.dllab.recsysbot.model.ChatResponseModel;
import com.ibm.dllab.recsysbot.model.PredicateModel;
import com.ibm.dllab.recsysbot.model.ProductModel;
import com.ibm.dllab.recsysbot.model.SMEDeleteResponseModel;
import com.ibm.dllab.recsysbot.model.SMEDocumentModel;
import com.ibm.dllab.recsysbot.model.SMEResponseModel;
import com.ibm.dllab.recsysbot.model.SmeListModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateRequestElementModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateRequestModel;
import com.ibm.dllab.recsysbot.model.SmeUpdateResponseModel;
import com.ibm.dllab.recsysbot.model.StatusModel;
import com.ibm.dllab.recsysbot.model.UnderscoreID;
import com.ibm.dllab.recsysbot.model.UserModel;
import com.ibm.dllab.recsysbot.model.WecoURLModel;
import com.ibm.dllab.recsysbot.model.smeRequestModel;
import com.ibm.dllab.recsysbot.service.AuthenticationService;
import com.ibm.dllab.recsysbot.service.ContextStoreService;
import com.ibm.dllab.recsysbot.service.ObjectStoreService;
import com.ibm.dllab.recsysbot.service.OrchestratorService;
import com.ibm.dllab.recsysbot.service.WatsonAssistantService;
import com.ibm.dllab.recsysbot.util.Constants;
import com.ibm.dllab.recsysbot.util.RelativeUrls;
import com.ibm.watson.developer_cloud.assistant.v1.model.Context;
import com.ibm.watson.developer_cloud.assistant.v1.model.MessageResponse;
import com.ibm.watson.developer_cloud.assistant.v1.model.RuntimeEntity;

@Component
public class OrchestratorServiceImpl implements OrchestratorService {
	@Autowired
	WatsonAssistantService waService;

	@Autowired
	ContextStoreService contextStore;

	@Autowired
	ObjectStoreService objectStore;

	@Autowired
	CloudantManager cloudantManager;
	
	@Autowired
	AuthenticationService authService;

	@Value(Constants.CLOUDANT_FEEDBACK_DATABASE)
	private String feedbackHistoryDatabase;

	@Value(Constants.CLOUDANT_WECO_URL_DATABASE)
	private String wecoURLDatabase;

	@Value(Constants.CLOUDANT_ASK_SME_DATABASE)
	private String smeDatabase;

	@Value(Constants.CLOUDANT_CHAT_HISTORY_DATABASE)
	private String chatHistoryDatabase;
	
	@Value(Constants.CLOUDANT_ALL_ATTRIBUTES_DATABASE)
	private String all_attributes_database;	
	
	private List<Context> getNextAttributeQuestion(String all_attributes_database, String nextAttribute) throws JsonProcessingException {
		Database db = cloudantManager.getDatabase(all_attributes_database);
		QueryResult<Context> context = db.query(
				new QueryBuilder(eq("attribute", nextAttribute)).build(), Context.class);
		System.out.println("userModel" +context);
		return context.getDocs();
	}
	

	private List<WecoURLModel> getCompleteDocument(String database, String docID, String docName)
			throws JsonProcessingException {
		Database db = cloudantManager.getDatabase(wecoURLDatabase);
		System.out.println();
		QueryResult<WecoURLModel> wecoURLModel = db.query(
				new QueryBuilder(and(regex("doc_id", docID), eq("doc_name", docName)))
						.fields("_id", "_rev", "doc_name", "doc_id", "doc_url", "doc_type", "doc_text").build(),
				WecoURLModel.class);
		return wecoURLModel.getDocs();
	}

	private List<WecoURLModel> getEngineeringDrawing(String database, String docID, String docName, String partNumber)
			throws JsonProcessingException {
		Database db = cloudantManager.getDatabase(wecoURLDatabase);
		if (partNumber.equals("") || partNumber.equals("all")) {
			QueryResult<WecoURLModel> wecoURLModel = db.query(
					new QueryBuilder(and(regex("doc_id", docID), eq("doc_name", "INTENT_4_ANSWER"/* docName */)))
							.fields("_id", "_rev", "doc_name", "doc_id", "doc_url", "doc_type", "doc_text").build(),
					WecoURLModel.class);
			return wecoURLModel.getDocs();
		}
		QueryResult<WecoURLModel> wecoURLModel = db.query(
				new QueryBuilder(and(PredicatedOperation.elemMatch("doc_text", PredicateExpression.eq(partNumber)),
						eq("doc_name", docName), regex("doc_id", docID)))
								.fields("_id", "_rev", "doc_name", "doc_id", "doc_url", "doc_type", "doc_text").build(),
				WecoURLModel.class);
		return wecoURLModel.getDocs();
	}

	private HashMap<String, Object> weather_info(JsonObject postData) {
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		String url = "https://weather-functions.mybluemix.net";

		HttpEntity<String> entity = new HttpEntity<String>(postData.toString(), headers);
		RestTemplate restTemplate = new RestTemplate();
		HashMap<String, Object> answer = restTemplate.postForObject(url, entity, HashMap.class);
		return (HashMap<String, Object>) answer.get("weather_function_output");
	}
	
	private ChatResponseModel callWCS(Context context, ChatResponseModel chatResponse, ChatRequestModel chatRequest, String conversationID) {
		String message = chatRequest.getInputMessage();
		MessageResponse response = waService.getResponse(message, context);
		conversationID = response.getContext().getConversationId();
		context = response.getContext();
		contextStore.updateContext(conversationID, context);
		chatResponse.setConversationID(conversationID);

		if (response.getOutput().getText() != null && response.getOutput().getText().size() != 0) {
			boolean found = false;
			for (String str : response.getOutput().getText()) {
				if (str != null && !str.trim().isEmpty()) {
					found = true;
				}
			}
			if (found) {
				chatResponse.setType("TEXT");
				chatResponse.setOutputMessages(response.getOutput().getText());
			}
		}
		return chatResponse;
	}
	
	private List<ProductModel> callStyleAPI(JsonObject postDataJson) {
		List<MediaType> acceptableMediaTypes = new ArrayList<MediaType>();
        acceptableMediaTypes.add(MediaType.APPLICATION_JSON);
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		headers.setAccept(acceptableMediaTypes);
		
		UriComponentsBuilder builder = UriComponentsBuilder.fromUriString(RelativeUrls.API_STYLE_URL);
		HttpEntity<String> entity = new HttpEntity<String>(postDataJson.toString(), headers);
		
		RestTemplate restTemplate = new RestTemplate();
		ResponseEntity<String> answer = restTemplate.exchange(builder.build().encode().toUri(), HttpMethod.POST, entity, String.class);
		Yaml yaml = new Yaml();
		LinkedHashMap< String, Object> results = (LinkedHashMap<String, Object>) yaml.load(answer.getBody());
		List<HashMap< String, Object>> outfits = (List<HashMap<String, Object>>) results.get("outfit_details");
		List<ProductModel> products = new ArrayList<ProductModel>();
		if(outfits != null && outfits.size() > 0) {
			for(HashMap<String, Object> product : outfits) {
				ProductModel newProduct = new ProductModel();
				newProduct.setImage_src(product.get("display_picture_URI").toString());
				newProduct.setProduct_index(Integer.parseInt(product.get("product_id").toString()));
				newProduct.setProduct_name(product.get("product_name").toString());
				newProduct.setIn_product_inventory(product.get("in_product_inventory").toString());
				newProduct.setSimilar_products((List<HashMap<String, Object>>) product.get("similar_products"));
				products.add(newProduct);
			}
		}
		return products;
	}
	
	private List<HashMap<String, Object>> convertToList(List<HashMap<String, Object>> similarProducts) {
		List<HashMap<String, Object>> newList = new ArrayList<>();
		for(HashMap<String, Object> product : similarProducts) {
			if(product!= null) {
				HashMap<String, Object> similarProduct = new HashMap<>();
				similarProduct.put("product_id", product.get("product_id"));
				newList.add(similarProduct);
			}
		}
		return newList;
	}


	private List<ProductModel> callShowMoreAPI(JsonArray getDataJson) {
		List<MediaType> acceptableMediaTypes = new ArrayList<MediaType>();
        acceptableMediaTypes.add(MediaType.APPLICATION_JSON);
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		headers.setAccept(acceptableMediaTypes);
		
		UriComponentsBuilder builder = UriComponentsBuilder.fromUriString(RelativeUrls.API_SHOW_ALL_URL);
		builder.queryParam("context", getDataJson);
		
		HttpEntity<Object> entity = new HttpEntity<Object>(headers);
		RestTemplate restTemplate = new RestTemplate();
		ResponseEntity<String> answer = restTemplate.exchange(builder.build().encode().toUri(), HttpMethod.GET, entity, String.class);
		Yaml yaml = new Yaml();
		List<HashMap< String, Object>> results = (List<HashMap<String, Object>>) yaml.load(answer.getBody());
		List<ProductModel> products = new ArrayList<ProductModel>();
		if(results != null && results.size() > 0) {
			for(HashMap<String, Object> product : results) {
				ProductModel newProduct = new ProductModel();
				newProduct.setImage_src(product.get("img_src").toString());
				newProduct.setProduct_index((Integer)product.get("product_index"));
				newProduct.setProduct_name(product.get("product_name").toString());
				products.add(newProduct);
			}
		}
		return products;
	}
	
	private List<ProductModel> getRecommendation(JsonObject postData) {
		
		List<MediaType> acceptableMediaTypes = new ArrayList<MediaType>();
        acceptableMediaTypes.add(MediaType.APPLICATION_JSON);
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		headers.setAccept(acceptableMediaTypes);
		
		UriComponentsBuilder builder = UriComponentsBuilder.fromUriString(RelativeUrls.API_RECOMMENDATION_URL);
		builder.queryParam("context", postData);
		
		HttpEntity<Object> entity = new HttpEntity<Object>(headers);
		RestTemplate restTemplate = new RestTemplate();
		ResponseEntity<String> answer = restTemplate.exchange(builder.build().encode().toUri(), HttpMethod.GET, entity, String.class);
		Yaml yaml = new Yaml();
		List<HashMap< String, Object>> results = (List<HashMap<String, Object>>) yaml.load(answer.getBody());
		List<ProductModel> products = new ArrayList<ProductModel>();
		if(results != null && results.size() > 0) {
			for(HashMap<String, Object> product : results) {
				ProductModel newProduct = new ProductModel();
				newProduct.setImage_src(product.get("img_src").toString());
				newProduct.setProduct_index((Integer)product.get("product_index"));
				newProduct.setProduct_name(product.get("product_name").toString());
				products.add(newProduct);
			}
		}
		return products;
	}
	
	private HashMap<String, Object> best_attribute_prediction(JsonObject postData) {
		List<MediaType> acceptableMediaTypes = new ArrayList<MediaType>();
        acceptableMediaTypes.add(MediaType.APPLICATION_JSON);
		
		HttpHeaders headers = new HttpHeaders();
		headers.setContentType(MediaType.APPLICATION_JSON);
		headers.setAccept(acceptableMediaTypes);
		UriComponentsBuilder builder = UriComponentsBuilder.fromUriString(RelativeUrls.API_ATTRIBUTE_PREDICTION_URL);
		builder.queryParam("context", postData);
		
		HttpEntity<Object> entity = new HttpEntity<Object>(headers);
		RestTemplate restTemplate = new RestTemplate();
		ResponseEntity<String> answer = restTemplate.exchange(builder.build().encode().toUri(), HttpMethod.GET, entity, String.class);
		Yaml yaml = new Yaml();
		HashMap< String, Object> result = (HashMap< String, Object>) yaml.load(answer.getBody());
		return result;
	}

	private HashMap<String, Object> query_get_concrete_index(String date, String location) throws IOException {
		if (date.equals("all"))
			date = "";
		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder().add("payload", factory.createObjectBuilder()
				.add("function", "concrete_index").add("location", location).add("date", date)).build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}

	private HashMap<String, Object> query_get_wind_condition(String user_input, String json_entities, String location)
			throws IOException {

		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload", factory.createObjectBuilder().add("function", "wind_condition")
						.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}

	private HashMap<String, Object> query_get_rainfall_last7days_condition(String user_input, String json_entities,
			String location) throws IOException {
		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload",
						factory.createObjectBuilder().add("function", "rainfall_last_7_days_condition")
								.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}

	private HashMap<String, Object> query_get_rainfall_5_year_max_condition(String user_input, String json_entities,
			String location) throws IOException {

		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload",
						factory.createObjectBuilder().add("function", "rainfall_5_year_max_condition")
								.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}

	private HashMap<String, Object> query_get_temperature_condition(String user_input, String json_entities,
			String location) throws IOException {

		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload",
						factory.createObjectBuilder().add("function", "temperature_condition")
								.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);

		List<String> dates = (List<String>) ((List<Map<String, Object>>) result.get("result")).get(0).get("date");
		List<String> formattedDates = new ArrayList<>();

		for (String date : dates) {
			formattedDates.add(date.substring(2, 4) + "/" + date.substring(0, 2));
		}

		((List<Map<String, Object>>) result.get("result")).get(0).put("date", formattedDates);

		return result;
	}

	private HashMap<String, Object> query_get_snow_condition(String user_input, String json_entities, String location)
			throws IOException {

		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload", factory.createObjectBuilder().add("function", "snow_condition")
						.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}

	private HashMap<String, Object> query_get_weather_narrative(String user_input, String json_entities,
			String location) throws IOException {

		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload", factory.createObjectBuilder().add("function", "weather_narrative")
						.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}
	
	
	private ChatResponseModel performNextAttributeAndAttributeQuery(MessageResponse response, Context context,
			ChatResponseModel chatResponse, ChatRequestModel chatRequest, String conversationID) throws JsonProcessingException {
		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObjectBuilder postDataBuilder = factory.createObjectBuilder();
		if(response != null) {
			if(context.get("product") != null && !context.get("product").toString().isEmpty() ) {				
				postDataBuilder.add("product", context.get("product").toString());
			}			
		} else {
			HashMap<String, Object> attributes = (HashMap<String, Object>) context.get("attributes");
			attributes.put(context.get("next_attribute").toString(), chatRequest.getInputMessage());
			context.put("attributes", attributes);
			for(Object key : attributes.keySet()) {
				String keyStr = (String)key;
		        Object keyvalue = attributes.get(keyStr);
		        postDataBuilder.add(keyStr, (String)keyvalue);
			}
		}
		
		JsonObject postDataJson = factory.createObjectBuilder()
				.add("attributes", postDataBuilder.build())
				.add("conversation_id", conversationID)
				.add("num_of_call", 1).build();
		HashMap<String, Object> result = best_attribute_prediction(postDataJson);
		List<Context> contexts = getNextAttributeQuestion(all_attributes_database,
		result.get("next_attr").toString());
		
		Context questionContext = new Context();
		if(contexts != null && contexts.size() > 0) {
			questionContext = contexts.get(0);		
			context.put("question", questionContext.get("question"));
			context.put("values", result.get("next_attr_values"));
			context.put("next_attribute", result.get("next_attr").toString());
			context.put("attributes", result.get("attributes"));				
		}
		contextStore.updateContext(conversationID, context);
		
		List<String> messages = new ArrayList<String>();
		if(questionContext.get("question").toString().isEmpty() || context.get("next_attribute").equals("no next attribute")) {
			chatResponse = callWCS(context, chatResponse, chatRequest, conversationID);
			context = contextStore.getContext(conversationID);
			if(context.get("ready_to_query") != null && ((boolean) context.get("ready_to_query"))) {
				LinkedTreeMap<String, Object> attributes = (LinkedTreeMap<String, Object>) context.get("attributes");
				for(Object key : attributes.keySet()) {
					String keyStr = (String)key;
			        Object keyvalue = attributes.get(keyStr);
			        postDataBuilder.add(keyStr, (String)keyvalue);
				}
			
			
			postDataJson = factory.createObjectBuilder()
					.add("attributes", postDataBuilder.build())
					.add("userId", ((Double)context.get("user_id")).intValue())
					/*.add("conversation_id", conversationID)
					.add("num_of_call", 2)*/
					.build();
			List<ProductModel> recommendations = getRecommendation(postDataJson);
			chatResponse.setProducts(recommendations);
			return chatResponse;
		}
			}
		
		PredicateModel predictModel = new PredicateModel();
		predictModel.setQuestion(questionContext.get("question").toString());
		predictModel.setValues((List<String>) result.get("next_attr_values"));
		chatResponse.setType("TEXT");
		chatResponse.setNextAttribute(predictModel);
		return chatResponse;
	}

	@Override
	public ChatResponseModel getChatResponse(ChatRequestModel chatRequest, Instant timestamp, String chatRequestID)
			throws JsonProcessingException {
		UserModel user = authService.authenticate(chatRequest.getUserID());
		Context context;
		Database chatHistoryDB = cloudantManager.getDatabase(chatHistoryDatabase);

		ChatModel chatRequestModel = new ChatModel();
		chatRequestModel.setTimestamp(timestamp);
		chatRequestModel.setChatType(Constants.CHAT_REQUEST);

		chatRequest.setChatRequestID(chatRequestID);
		chatRequestModel.setChatRequest(chatRequest);

		ChatResponseModel chatResponse = new ChatResponseModel();
		chatResponse.setChatRequestID(chatRequestID);

		String conversationID = chatRequest.getConversationID();
		if(conversationID == null || conversationID.isEmpty()) {
			JsonBuilderFactory factory = Json.createBuilderFactory(null);
			JsonObject postData; 
			context = new Context();
			if(user != null) {
				postData = (JsonObject) factory.createObjectBuilder().add("gender", user.getGender())
							.add("first_name", user.getFirst_name())
							.add("age", user.getAge())
							.add("user_type", "known").build();
				context.put("first_name", user.getFirst_name());
				context.put("last_name", user.getLast_name());
				context.put("user_id", user.getUser_id());
				context.put("user_type", "known");
				chatResponse.setUserDetail(user);
			} else {
				postData =  (JsonObject) factory.createObjectBuilder().add("user_type", "unknown").build();
			}
		} else {
			context = contextStore.getContext(conversationID);
		}
		
		HashMap<String, Object> requestParam = chatRequest.getData();	
		HashMap<String, Object> product = chatRequest.getProduct();		
		
		
		if(context.get("product_available") != null && (boolean)context.get("product_available")) {			
			return performNextAttributeAndAttributeQuery(null, context, chatResponse, chatRequest, conversationID);
		} else {
			if(requestParam != null && requestParam.get("viewRelatedProduct") != null 
					&& !requestParam.get("viewRelatedProduct").toString().isEmpty() ) {
				context.put("view_related_products", requestParam.get("viewRelatedProduct").toString());
			}else if(requestParam != null && requestParam.get("showMoreProduct") != null 
					&& !requestParam.get("showMoreProduct").toString().isEmpty() ) {
				context.put("show_more_product", requestParam.get("showMoreProduct").toString());
			}else if(requestParam != null && requestParam.get("purchase") != null 
					&& !requestParam.get("purchase").toString().isEmpty() ) {
				context.put("purchase", requestParam.get("purchase").toString());
			}
		}
//		if(context.get("view_related_products") != null && context.get("view_related_products").toString().equals("yes")) {	
//			System.out.println(context.get("view_related_products").toString());
//			return callWCS(context, chatResponse, chatRequest, conversationID);
//		}
		
		String message = chatRequest.getInputMessage();
		MessageResponse response = waService.getResponse(message, context);
		conversationID = response.getContext().getConversationId();
		context = response.getContext();
		contextStore.updateContext(conversationID, context);
		chatResponse.setConversationID(conversationID);

		if (response.getOutput().getText() != null && response.getOutput().getText().size() != 0) {
			boolean found = false;
			for (String str : response.getOutput().getText()) {
				if (str != null && !str.trim().isEmpty()) {
					found = true;
				}
			}
			if (found) {
				chatResponse.setType("TEXT");
				chatResponse.setOutputMessages(response.getOutput().getText());
			}
		}
		
		if(context.get("ready_to_call_style_API") != null && (Boolean)context.get("ready_to_call_style_API")) {
			JsonBuilderFactory factory = Json.createBuilderFactory(null);
			JsonObjectBuilder postDataBuilder = factory.createObjectBuilder();
			for(Object key : product.keySet()) {
				String keyStr = (String)key;
		        Object keyvalue = product.get(keyStr);
		        if(keyvalue instanceof String) {
		        	postDataBuilder.add(keyStr, (String)keyvalue);
		        }else if(keyvalue instanceof Integer) {
		        	postDataBuilder.add(keyStr, (Integer)keyvalue);
		        }		        
			}		
		
			JsonObject postDataJson = factory.createObjectBuilder()
					.add("key", postDataBuilder.build()).build();
			
			List<ProductModel> styleproducts = callStyleAPI((postDataJson));
			chatResponse.setProducts(styleproducts);
			return chatResponse;
		}
		
		if(context.get("ready_to_call_rec_API_2")!=null && (Boolean)context.get("ready_to_call_rec_API_2")){
		
			JsonBuilderFactory factory = Json.createBuilderFactory(null);
			JsonArrayBuilder jsonArrayBuilder=Json.createArrayBuilder();
			JsonObjectBuilder jsonObjectBuilder=Json.createObjectBuilder();
			List<HashMap< String, Object>> listOfSimilarProducts=(List<HashMap< String, Object>>)requestParam.get("similarProducts");
			for(HashMap< String, Object> similarProductId:listOfSimilarProducts){
				jsonArrayBuilder.add(Json.createObjectBuilder().add("product_index",Integer.parseInt(similarProductId.get("product_id").toString())));
//				jsonObjectBuilder.add("product_index",similarProductId.get("product_id").toString());
							
			}
			jsonArrayBuilder.add(Json.createObjectBuilder().add("userId", ((Double)context.get("user_id")).intValue()));
			JsonArray getDataJson = jsonArrayBuilder.build();
			
			List<ProductModel> similarProducts = callShowMoreAPI((getDataJson));
			chatResponse.setProducts(similarProducts);
			return chatResponse;
		}
		
		if(context.get("product_available") != null && (boolean)context.get("product_available")) {
			chatResponse =  performNextAttributeAndAttributeQuery(response, context, chatResponse, chatRequest, conversationID);
		}

//		if (context.get("ready_to_query") != null && ((Boolean) context.get("ready_to_query")) == true) {
//			String projectName = (String) context.get("project_name");
//			String project_query_filter = "";
//
//			if (projectName != null) {
//				projectName = projectName.toUpperCase();
//				project_query_filter = ", doc_id: " + projectName;
//			} else {
//				projectName = "";
//			}
//
//			List<String> docArray = (List<String>) context.get("doc_array");
//			List<String> docCollection = (List<String>) context.get("doc_collection");
//
//			Map<String, Object> results = new HashMap<>();
//			if (context.get("results") != null) {
//				results = (Map<String, Object>) context.get("results");
//			}
//
//			List<WecoURLModel> cloudant = new ArrayList<>();
//			Boolean skipRestofIt = false;
//
//			if ((!response.getIntents().isEmpty() && response.getIntents().get(0).getIntent().equals("Intent_1"))
//					|| ((String) response.getContext().get("initial_intents")).equals("Intent_1")) {
//				List<WecoURLModel> wecoURLModel = getCompleteDocument(wecoURLDatabase,
//						projectName /* "INTENT_1_ANSWER" */, "INTENT_1_ANSWER");
//				cloudant.addAll(wecoURLModel);
//
//				skipRestofIt = true;
//			}
//
//			if ((!response.getIntents().isEmpty() && response.getIntents().get(0).getIntent().equals("Intent_11"))
//					|| ((String) response.getContext().get("initial_intents")).equals("Intent_11")) {
//				List<WecoURLModel> wecoURLModel = getCompleteDocument(wecoURLDatabase,
//						projectName /* "INTENT_11_ANSWER" */, "INTENT_11_ANSWER");
//				cloudant.addAll(wecoURLModel);
//
//				skipRestofIt = true;
//			}
//
//			if ((!response.getIntents().isEmpty() && response.getIntents().get(0).getIntent().equals("Intent_9"))
//					|| ((String) response.getContext().get("initial_intents")).equals("Intent_9")) {
//				if (docArray.contains("Engineering Drawings")) {
//					String partNumber;
//					try {
//						partNumber = (String) context.get("part_number");
//					} catch (Exception ex) {
//						Integer part_num = ((Double) context.get("part_number")).intValue();
//						partNumber = String.valueOf(part_num);
//					}
//
//					List<WecoURLModel> wecoURLModel = getEngineeringDrawing(wecoURLDatabase, projectName,
//							"Engineering Drawings", partNumber);
//					cloudant.addAll(wecoURLModel);
//
//					docArray.remove("Engineering Drawings");
//					docCollection.remove("Cloudant");
//				}
//			}
//
//			if (cloudant != null && cloudant.size() != 0) {
//				chatResponse.setType("CLOUDANT");
//				results.put("cloudant", cloudant);
//			}
//
//			if (docCollection != null && docArray != null && skipRestofIt != true) {
//				if (docCollection.contains("Cloudant")) {
//					if (docArray.contains("Project Contact List")) {
//						List<WecoURLModel> wecoURLModel = getCompleteDocument(wecoURLDatabase, projectName,
//								"Project Contact List");
//						cloudant.addAll(wecoURLModel);
//						docArray.remove("Project Contact List");
//					}
//
//					if (docArray.contains("Engineering Drawings")) {
//						String partNumber;
//						try {
//							partNumber = (String) context.get("part_number");
//						} catch (Exception ex) {
//							Integer part_num = ((Double) context.get("part_number")).intValue();
//							partNumber = String.valueOf(part_num);
//						}
//
//						List<WecoURLModel> wecoURLModel = getEngineeringDrawing(wecoURLDatabase, projectName,
//								"Engineering Drawings", partNumber);
//						cloudant.addAll(wecoURLModel);
//						docArray.remove("Engineering Drawings");
//					}
//
//					if (cloudant != null && cloudant.size() != 0) {
//						chatResponse.setType("CLOUDANT");
//						results.put("cloudant", cloudant);
//					}
//				}
//
//				if (docCollection.contains("Weather Company")) {
//					String user_input = (String) context.get("input");
//					boolean location_found = false;
//					boolean date_found = false;
//					List<RuntimeEntity> current_entities = response.getEntities();
//					for (Object entity_obj : current_entities) {
//						HashMap<String, Object> entity_map = (HashMap<String, Object>) entity_obj;
//
//						String entity = (String) entity_map.get("entity");
//						if (entity.equals("location"))
//							location_found = true;
//						if (entity.equals("sys-date"))
//							date_found = true;
//					}
//					if (location_found == false || date_found == false) {
//						List<Object> temp = (List<Object>) context.get("initial_entities");
//						for (Object entity_obj : current_entities) {
//							temp.add(entity_obj);
//						}
//						context.put("initial_entities", temp);
//
//						user_input = user_input + (String) context.get("initial_input");
//						location_found = true;
//						date_found = true;
//					}
//					String weather_function = (String) context.get("weather_function");
//
//					if (weather_function.equals("concrete_index")) {
//						try {
//							String date = (String) context.get("weather_date");
//							String location = (String) context.get("weather_location");
//							results.put("weather", query_get_concrete_index(date, location));
//							chatResponse.setType("WEATHER");
//						} catch (IOException e) {
//							e.printStackTrace();
//						}
//					} else {
//						if (location_found == true && date_found == true) {
//							String location = (String) context.get("weather_location");
//							String we_function = (String) context.get("weather_function");
//							List<Object> initial_entity = (List<Object>) context.get("initial_entities");
//							Gson gson = new Gson();
//							String json_entities = gson.toJson(initial_entity);
//							if (we_function.equals("wind_condition")) {
//								try {
//									results.put("weather",
//											query_get_wind_condition(user_input, json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//								;
//
//							} else if (we_function.equals("rainfall_last_7_days_condition")) {
//								try {
//									results.put("weather", query_get_rainfall_last7days_condition(user_input,
//											json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//
//							} else if (we_function.equals("rainfall_5_year_max_condition")) {
//								try {
//									results.put("weather", query_get_rainfall_5_year_max_condition(user_input,
//											json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//							} else if (we_function.equals("temperature_condition")) {
//								try {
//									results.put("weather",
//											query_get_temperature_condition(user_input, json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//							} else if (we_function.equals("snow_condition")) {
//								try {
//									results.put("weather",
//											query_get_snow_condition(user_input, json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//							} else if (we_function.equals("delay_rain_snow")) {
//								try {
//									// System.out.println(location);
//									results.put("weather",
//											query_get_delay_rain_snow(user_input, json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//
//							} else {
//								try {
//									results.put("weather",
//											query_get_weather_narrative(user_input, json_entities, location));
//									chatResponse.setType("WEATHER");
//								} catch (IOException e) {
//									e.printStackTrace();
//								}
//							}
//						}
//					}
//
//				}
//			}
//
//			context.put("results", results);
//
//			response = waService.getResponse("test", context);
//			context = response.getContext();
//
//			contextStore.updateContext(conversationID, context);
//
//			if (response.getOutput().getText() != null && response.getOutput().getText().size() != 0) {
//				boolean found = false;
//
//				for (String str : response.getOutput().getText()) {
//					if (str != null && !str.trim().isEmpty()) {
//						found = true;
//					}
//				}
//
//				if (found) {
//					chatResponse.setType("TEXT");
//					chatResponse.setOutputMessages(response.getOutput().getText());
//				}
//			}
//
//			chatResponse.setData(results);
//		}

		String chatResponseID = UUID.randomUUID().toString();
		chatResponse.setChatResponseID(chatResponseID);

		// storing (chatResponseID, conversationID) in cache for quick lookup
		objectStore.updateObject(chatResponseID, conversationID);

		ChatModel chatResponseModel = new ChatModel();
		chatResponseModel.setTimestamp(Instant.now());
		chatResponseModel.setChatType(Constants.CHAT_RESPONSE);
		chatResponseModel.setChatResponse(chatResponse);

		// save chat request to cloudant
		chatRequestModel.setConversationID(conversationID);
		chatRequestModel.setUserID(chatRequest.getUserID());
		chatHistoryDB.save(chatRequestModel);

		// save chat response to cloudant
		chatResponseModel.setConversationID(conversationID);
		chatHistoryDB.save(chatResponseModel);

		return chatResponse;
	}

	private HashMap<String, Object> query_get_delay_rain_snow(String user_input, String json_entities, String location)
			throws IOException {

		JsonBuilderFactory factory = Json.createBuilderFactory(null);
		JsonObject postData = (JsonObject) factory.createObjectBuilder()
				.add("payload", factory.createObjectBuilder().add("function", "delay_rain_snow")
						.add("user_input", user_input).add("entities", json_entities).add("location", location))
				.build();
		HashMap<String, Object> result = weather_info(postData);
		return result;
	}

	@Override
	public ChatHistoryResponseModel getChatHistoryResponse(ChatHistoryRequestModel chatHistoryRequest)
			throws JsonProcessingException {
		String conversationID = chatHistoryRequest.getConversationID();
		String userID = chatHistoryRequest.getUserID();
		Database chatHistoryDB = cloudantManager.getDatabase(chatHistoryDatabase);

		ChatHistoryResponseModel chatHistory = new ChatHistoryResponseModel();
		chatHistory.setConversationID(conversationID);
		chatHistory.setUserID(userID);
		chatHistory.setResults(null);

		if (chatHistoryDB != null) {
			String query = null;

			if (userID != null && conversationID == null) {
				query = new QueryBuilder(eq("userID", userID)).build();
			} else if (userID != null && conversationID != null) {
				query = new QueryBuilder(and(eq("userID", userID), eq("conversationID", conversationID))).build();
			} else if (userID == null && conversationID != null) {
				query = new QueryBuilder(eq("conversationID", conversationID)).build();
			}

			if (query != null) {
				QueryResult<ChatModel> chatHistoryResults = chatHistoryDB.query(query, ChatModel.class);

				List<ChatModel> results = chatHistoryResults.getDocs();
				results.sort(new Comparator<ChatModel>() {
					@Override
					public int compare(ChatModel o1, ChatModel o2) {
						return o1.getTimestamp().compareTo(o2.getTimestamp());
					}
				});

				chatHistory.setResults(results);
			}

			return chatHistory;
		}

		return null;
	}

	@Override
	public ChatFeedbackResponseModel saveChatFeedback(ChatFeedbackRequestModel chatFeedback, Instant timestamp)
			throws JsonProcessingException {
		StatusModel status = new StatusModel();

		Database feedbackHistoryDB = cloudantManager.getDatabase(feedbackHistoryDatabase);
		chatFeedback.setTimestamp(timestamp);

		if (feedbackHistoryDB != null) {
			chatFeedback.setStatus(Constants.FEEDBACK_NOT_PROCESSED);
			feedbackHistoryDB.save(chatFeedback);

			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);
		} else {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		ChatFeedbackResponseModel chatFeedbackResponse = new ChatFeedbackResponseModel();
		chatFeedbackResponse.setStatus(status);

		return chatFeedbackResponse;
	}

	@Override
	public ChatFeedbackHistoryResponseModel getChatFeedbackHistory(ChatFeedbackHistoryRequestModel request)
			throws JsonProcessingException {
		String userID = request.getUserID();
		String documentID = request.getDocumentID();

		Database chatFeedbackHistoryDB = cloudantManager.getDatabase(feedbackHistoryDatabase);

		ChatFeedbackHistoryResponseModel chatFeedbackHistory = new ChatFeedbackHistoryResponseModel();
		chatFeedbackHistory.setUserID(userID);
		chatFeedbackHistory.setDocumentID(documentID);
		chatFeedbackHistory.setResults(null);

		if (chatFeedbackHistoryDB != null) {
			String query = null;

			if (userID != null && documentID == null) {
				query = new QueryBuilder(eq("userID", userID)).build();
			} else if (userID != null && documentID != null) {
				query = new QueryBuilder(and(eq("userID", userID), eq("documentID", documentID))).build();
			} else if (userID == null && documentID != null) {
				query = new QueryBuilder(eq("documentID", documentID)).build();
			}

			if (query != null) {
				QueryResult<ChatFeedbackRequestModel> chatFeedbackHistoryResults = chatFeedbackHistoryDB.query(query,
						ChatFeedbackRequestModel.class);

				List<ChatFeedbackRequestModel> results = chatFeedbackHistoryResults.getDocs();
				results.sort(new Comparator<ChatFeedbackRequestModel>() {
					@Override
					public int compare(ChatFeedbackRequestModel o1, ChatFeedbackRequestModel o2) {
						return o1.getTimestamp().compareTo(o2.getTimestamp());
					}
				});

				chatFeedbackHistory.setResults(results);
			}

			return chatFeedbackHistory;
		}

		return null;
	}

	@Override
	public ChatFeedbackResponseModel markFeedbackProcessed(ChatFeedbackProcessedRequestModel request)
			throws JsonProcessingException {
		StatusModel status = new StatusModel();
		Database feedbackHistoryDB = cloudantManager.getDatabase(feedbackHistoryDatabase);

		if (feedbackHistoryDB != null) {
			for (UnderscoreID underscoreID : request.getProcessed()) {
				String _id = underscoreID.get_id();

				ChatFeedbackRequestModel chatFeedback = feedbackHistoryDB.find(ChatFeedbackRequestModel.class, _id);
				chatFeedback.setStatus(Constants.FEEDBACK_PROCESSED);

				feedbackHistoryDB.update(chatFeedback);
			}

			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);

		} else {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		ChatFeedbackResponseModel feedbackResponse = new ChatFeedbackResponseModel();
		feedbackResponse.setStatus(status);
		return feedbackResponse;
	}

	@Override
	public SMEResponseModel getsmeResponse(smeRequestModel smeRequest, Instant timestamp)
			throws JsonProcessingException {
		smeRequest.setStatus(Constants.ASKSME_NOT_ANSWERED);

		StatusModel status = new StatusModel();

		Database smeDB = cloudantManager.getDatabase(smeDatabase);
		String conversationID = smeRequest.getConversationID();
		if (conversationID != null && smeDB != null) {
			smeDB.save(smeRequest);
			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);
		} else {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		SMEResponseModel smeResponse = new SMEResponseModel();

		smeResponse.setStatus(status);
		return smeResponse;
	}

	public HashMap<String, Object> getsmeList(AskSmeListRequestModel askSmeRequest) throws JsonProcessingException {
		String user_id = askSmeRequest.getUserID();
		Database smeDB = cloudantManager.getDatabase(smeDatabase);
		if (smeDB != null) {
			List<SmeListModel> cloudant = new ArrayList<>();
			QueryResult<SmeListModel> smeResult = smeDB.query(
					new QueryBuilder(eq("userID", user_id))
							.fields("_id", "_rev", "conversationID", "userID", "timestamp", "projectId", "category",
									"subcategory", "sme", "userQuery", "question", "status")
							.build(),
					SmeListModel.class);
			HashMap<String, Object> result = new HashMap<>();
			result.put("results", smeResult.getDocs());
			return result;
		} else {
			return null;
		}

	}

	public SmeUpdateResponseModel smeMarkAnswered(SmeUpdateRequestModel sme_update_request)
			throws JsonProcessingException {
		StatusModel status = new StatusModel();
		Database smeDB = cloudantManager.getDatabase(smeDatabase);

		if (smeDB != null) {
			for (SmeUpdateRequestElementModel sme_request : sme_update_request.getMarks()) {
				String _id = sme_request.get_id();

				SMEDocumentModel sme = smeDB.find(SMEDocumentModel.class, _id);
				sme.setStatus(Constants.ASKSME_ANSWERED);

				smeDB.update(sme);
			}
			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);

		} else {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		SmeUpdateResponseModel sme_update_response = new SmeUpdateResponseModel();
		sme_update_response.setStatus(status);
		return sme_update_response;
	}

	private void clearDatabse(String database) throws JsonProcessingException {
		cloudantManager.dropDB(database);
		cloudantManager.getDatabase(database);
	}

	@Override
	public ChatFeedbackResponseModel clearFeedbackHistory() throws JsonProcessingException {
		StatusModel status = new StatusModel();

		try {
			clearDatabse(feedbackHistoryDatabase);

			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);
		} catch (Exception e) {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		ChatFeedbackResponseModel chatFeedbackResponse = new ChatFeedbackResponseModel();
		chatFeedbackResponse.setStatus(status);

		return chatFeedbackResponse;
	}

	@Override
	public SMEResponseModel clearSMEAll() throws JsonProcessingException {
		StatusModel status = new StatusModel();

		try {
			clearDatabse(smeDatabase);

			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);
		} catch (Exception e) {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		SMEResponseModel smeResponseModel = new SMEResponseModel();
		smeResponseModel.setStatus(status);

		return smeResponseModel;
	}

	@Override
	public Map<String, Object> clearChatHistory() throws JsonProcessingException {
		StatusModel status = new StatusModel();

		try {
			clearDatabse(chatHistoryDatabase);

			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);
		} catch (Exception e) {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		Map<String, Object> response = new HashMap<>();
		response.put("status", status);

		return response;
	}

	@Override
	public SMEDeleteResponseModel clearSME(String userID, List<String> ids) throws JsonProcessingException {
		StatusModel status = new StatusModel();
		Database smeDB = cloudantManager.getDatabase(smeDatabase);

		if (smeDB != null) {
			status.setCode(200);
			status.setMessage(Constants.GENERIC_SUCCESS_MESSAGE);

			for (String id : ids) {
				QueryResult<SMEDocumentModel> smeDocument = smeDB.query(
						new QueryBuilder(and(eq("userID", userID), eq("_id", id))).build(), SMEDocumentModel.class);

				if (!smeDocument.getDocs().isEmpty()) {
					smeDB.remove(smeDocument.getDocs().get(0));
				} else {
					status.setCode(500);
					status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
					break;
				}
			}
		} else {
			status.setCode(500);
			status.setMessage(Constants.GENERIC_FAILURE_MESSAGE);
		}

		SMEDeleteResponseModel smeDeleteResponse = new SMEDeleteResponseModel();
		smeDeleteResponse.setStatus(status);
		return smeDeleteResponse;
	}

}
