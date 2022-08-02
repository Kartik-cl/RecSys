package com.ibm.dllab.recsysbot.service;

public interface ObjectStoreService {

	public void updateObject(String id, Object obj);

	public Object getObject(String id);
}
