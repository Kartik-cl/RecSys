package com.ibm.dllab.recsysbot.model;

import java.util.List;

public class PredicateModel {
	String question;
	List<String> values;
	public List<String> getValues() {
		return values;
	}
	public void setValues(List<String> values) {
		this.values = values;
	}
	public String getQuestion() {
		return question;
	}
	public void setQuestion(String question) {
		this.question = question;
	}

}
