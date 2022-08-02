package com.ibm.dllab.recsysbot.model;

import java.util.HashMap;
import java.util.List;

public class ProductModel {
	
	private String in_product_inventory;
	private String product_name;
	private Integer product_index;
	private String image_src;
	private String image_location;
	private List<HashMap< String, Object>> similar_products;
	
	public String getProduct_name() {
		return product_name;
	}
	public void setProduct_name(String product_name) {
		this.product_name = product_name;
	}
	public String getImage_src() {
		return image_src;
	}
	public void setImage_src(String image_src) {
		this.image_src = image_src;
	}
	
	
	public String getImage_location() {
		return image_location;
	}
	public void setImage_location(String image_location) {
		this.image_location = image_location;
	}
	public Integer getProduct_index() {
		return product_index;
	}
	public void setProduct_index(Integer product_index) {
		this.product_index = product_index;
	}
	public String getIn_product_inventory() {
		return in_product_inventory;
	}
	public void setIn_product_inventory(String in_product_inventory) {
		this.in_product_inventory = in_product_inventory;
	}
	public List<HashMap<String, Object>> getSimilar_products() {
		return similar_products;
	}
	public void setSimilar_products(List<HashMap<String, Object>> similar_products) {
		this.similar_products = similar_products;
	}
}
