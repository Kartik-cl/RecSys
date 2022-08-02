package com.ibm.dllab.recsysbot.model;

public class SmeUpdateRequestElementModel {
	//TODO: only _id is needed, get rid of others
	
	private String _id;
	private String _rev;
	private String status;

	public String get_id() {
		return _id;
	}

	public void set_id(String _id) {
		this._id = _id;
	}

	public String get_rev() {
		return _rev;
	}

	public void set_rev(String _rev) {
		this._rev = _rev;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

}
