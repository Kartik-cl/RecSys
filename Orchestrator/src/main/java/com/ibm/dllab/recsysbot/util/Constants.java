package com.ibm.dllab.recsysbot.util;

public class Constants {
	public static final String WA_ENDPOINT_URL = "${recsysbot.wa.endpoint}";
	public static final String WA_WORKSPACE_ID = "${recsysbot.wa.workspace}";
	public static final String WA_USERNAME = "${recsysbot.wa.username}";
	public static final String WA_PASSWORD = "${recsysbot.wa.password}";
	public static final String WA_VERSION_DATE = "2018-02-16";

	public static final String GENERIC_SUCCESS_MESSAGE = "success";
	public static final String GENERIC_FAILURE_MESSAGE = "failure";

	
	public static final String CLOUDANT_ACCOUNT = "${recsysbot.cloudant.account}";
	public static final String CLOUDANT_USERNAME = "${recsysbot.cloudant.username}";
	public static final String CLOUDANT_PASSWORD = "${recsysbot.cloudant.password}";
	public static final String CLOUDANT_FEEDBACK_DATABASE = "${recsysbot.cloudant.database.feedback}";
	public static final String CLOUDANT_WECO_URL_DATABASE = "${recsysbot.cloudant.database.weco_url}";
	public static final String CLOUDANT_CHAT_HISTORY_DATABASE = "${recsysbot.cloudant.database.chat_history}";
	public static final String CLOUDANT_USER_DATABASE = "${recsysbot.cloudant.database.user}";
	public static final String CLOUDANT_ALL_ATTRIBUTES_DATABASE = "${recsysbot.cloudant.database.all_attributes}";
	

	public static final String CHAT_REQUEST = "CHAT_REQUEST";
	public static final String CHAT_RESPONSE = "CHAT_RESPONSE";
	public static final String CLOUDANT_ASK_SME_DATABASE = "${recsysbot.cloudant.database.sme}";

	public static final String ASKSME_ANSWERED = "ANSWERED";
	public static final String ASKSME_NOT_ANSWERED = "NOT_ANSWERED";

	public static final String FEEDBACK_PROCESSED = "PROCESSED";
	public static final String FEEDBACK_NOT_PROCESSED = "NOT_PROCESSED";
}
