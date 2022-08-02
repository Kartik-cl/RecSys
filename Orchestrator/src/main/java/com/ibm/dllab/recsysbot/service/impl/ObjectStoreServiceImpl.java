package com.ibm.dllab.recsysbot.service.impl;

import java.util.concurrent.TimeUnit;

import org.springframework.stereotype.Component;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.ibm.dllab.recsysbot.service.ObjectStoreService;

@Component
public class ObjectStoreServiceImpl implements ObjectStoreService {

	private static Cache<String, Object> objectStore = Caffeine.newBuilder().maximumSize(50000)
			.expireAfterAccess(1, TimeUnit.HOURS).build();

	@Override
	public void updateObject(String id, Object obj) {
		objectStore.put(id, obj);

	}

	@Override
	public Object getObject(String id) {
		return objectStore.getIfPresent(id);
	}
}
