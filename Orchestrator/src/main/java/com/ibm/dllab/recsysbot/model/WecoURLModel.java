package com.ibm.dllab.recsysbot.model;

import java.util.List;

public class WecoURLModel {
	private String _id;
	private String _rev;
	private String doc_name;
	private String doc_id;
	private List<String> doc_url;
	private List<String> doc_type;
	private List<String> doc_text;

	public String get_id() {
		return _id;
	}

	public void set_id(String _id) {
		this._id = _id;
	}

	public List<String> getDoc_type() {
		return doc_type;
	}

	public void setDoc_type(List<String> doc_type) {
		this.doc_type = doc_type;
	}

	public String get_rev() {
		return _rev;
	}

	public void set_rev(String _rev) {
		this._rev = _rev;
	}

	public String getDoc_name() {
		return doc_name;
	}

	public void setDoc_name(String doc_name) {
		this.doc_name = doc_name;
	}

	public String getDoc_id() {
		return doc_id;
	}

	public void setDoc_id(String doc_id) {
		this.doc_id = doc_id;
	}

	public List<String> getDoc_url() {
		return doc_url;
	}

	public void setDoc_url(List<String> doc_url) {
		this.doc_url = doc_url;
	}

	public List<String> getDoc_text() {
		return doc_text;
	}

	public void setDoc_text(List<String> doc_text) {
		this.doc_text = doc_text;
	}

}
