# -*- coding: utf-8 -*-
"""
Created on Thu Sept 6 15:07:34 2018

@author: Sapna
"""
import numpy as np
import tensorflow as tf
import pandas as pd
from scipy import sparse
import pickle

class RecomendationEngine:
    def __init__(self,list_user_layers, list_prod_txt_layers,list_prod_img_layers,alpha1,alpha2):

        self.ph_user_inp = tf.placeholder("float", [None, 20])
        self.ph_prod_txt_inp = tf.placeholder("float", [None, 855])
        self.ph_prod_img_inp = tf.placeholder("float", [None, 512])
        self.ph_utility_mat = tf.placeholder("float", [None, None])

        ''' Product Audoencoder - includes both text and img embeddings '''  
        self.prod_embeddings,self.prod_txt_reconstruction,self.prod_img_reconstruction = self.model_product(list_prod_txt_layers,list_prod_img_layers)
        
        ''' User Autoencoder '''
        self.user_embeddings,self.user_reconstruction = self.model_user(list_user_layers)
        
        ''' ratings Pred '''
        self.rating_pred = tf.matmul(self.user_embeddings,tf.transpose(self.prod_embeddings))

        self.optimizer = tf.train.AdamOptimizer()
        self.train_step = None
        self.alpha1 = alpha1
        self.alpha2 = alpha2
    
    def model_user(self,list_user_layers):
        ''' User Encoding '''
        inp = self.ph_user_inp
        for ind in range(1,len(list_user_layers)):
            name = "user_"+str(ind)+"_"
            out = self.add_dense_layer(list_user_layers[ind],inp,activation=tf.nn.relu,name=name)
            inp = out
        user_embedding = out
        ''' User Decoding '''
        inp = user_embedding
        for ind in range(len(list_user_layers)-1,-1,-1):
            name = "user_decode_"+str(ind)+"_"
            out = self.add_dense_layer(list_user_layers[ind],inp,activation=tf.nn.relu,name=name)
            inp = out
        user_reconstruction = out
        return user_embedding, user_reconstruction

    def model_product(self,list_txt_layers,list_img_layers):
        ''' Text Model - Encoding '''
        inp = self.ph_prod_txt_inp
        for ind in range(1,len(list_txt_layers)-1):
            name = "prod_txt_"+str(ind)+"_"
            out = self.add_dense_layer(list_txt_layers[ind],inp,activation=tf.nn.relu,name=name)
            inp = out
        txt_embedding = out
        
        ''' Img Model - Encoding '''
        inp = self.ph_prod_img_inp
        for ind in range(1,len(list_img_layers)-1):
            name = "prod_img_"+str(ind)+"_"
            out = self.add_dense_layer(list_img_layers[ind],inp,activation=tf.nn.relu,name=name)
            inp = out
        img_embedding = out

        ''' Merging Both Prod Models '''
        concat_embedding = tf.concat([txt_embedding, img_embedding],axis=1)
        prod_embedding = self.add_dense_layer(list_img_layers[-1],concat_embedding,activation=tf.nn.relu,name="prod_embed_")

        ''' Img Model - Decoding '''
        inp = prod_embedding
        for ind in range(len(list_img_layers)-1,-1,-1):
            name = "prod_img_decode_"+str(ind)+"_"
            out = self.add_dense_layer(list_img_layers[ind],inp,activation=tf.nn.relu,name=name)
            inp = out
        img_reconstruction = out

        ''' Text Model - Decoding '''
        inp = prod_embedding
        for ind in range(len(list_txt_layers)-1,-1,-1):
            name = "prod_txt_decode_"+str(ind)+"_"
            out = self.add_dense_layer(list_txt_layers[ind],inp,activation=tf.nn.relu,name=name)
            inp = out
        txt_reconstruction = out

        return prod_embedding,txt_reconstruction,img_reconstruction

    def add_dense_layer(self,out_dim,inp,activation=tf.nn.relu,name=""):
        layer =  tf.layers.dense(inp,out_dim,activation=tf.nn.relu,name=name)
        return tf.layers.batch_normalization(layer)
    '''
    def init_user_params(self):
        pkl_file = open('user_embeddings.pkl', 'rb')
        weight_list = pickle.load(pkl_file)
        pkl_file.close()
        return weight_list
    '''

    def error(self):
        user_error = tf.losses.mean_squared_error(self.ph_user_inp,self.user_reconstruction)
        prod_error = tf.losses.mean_squared_error(self.ph_prod_img_inp,self.prod_img_reconstruction) + tf.losses.mean_squared_error(self.ph_prod_txt_inp,self.prod_txt_reconstruction)               
        rating_error = tf.losses.mean_squared_error(self.ph_utility_mat,tf.multiply(self.rating_pred,tf.cast(self.ph_utility_mat>=1,tf.float32)))
        error = self.alpha1*prod_error  + self.alpha2*user_error + (1-self.alpha1-self.alpha2)*rating_error
        return error,rating_error
        

    def init_session(self,sess):
        self.error_val,_ = self.error()
        self.train_step = self.optimizer.minimize(self.error_val)
        init = tf.global_variables_initializer()
        sess.run(init)
        
    '''
    def train_prod(self,sess,itemtrain):
        hidden,out = self.model_item_encoding()
        regularizer = tf.nn.l2_loss(self.iWh1) + tf.nn.l2_loss(self.iWh2) + tf.nn.l2_loss(self.iWh3) + tf.nn.l2_loss(self.iWo1) + tf.nn.l2_loss(self.iWo2) + tf.nn.l2_loss(self.iWo3)
        #err_prod = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels = self.ix,logits = out) + 0.01*regularizer) #tf.sqrt(tf.reduce_mean(tf.square(self.ix-out))) #+ 0.01*regularizer  
        err_prod =  tf.losses.sigmoid_cross_entropy( self.ix, out)
        train_step = self.optimizer.minimize(err_prod)#+0.01*regularizer)
        sess.run(train_step,feed_dict={self.ix:itemtrain})
        err_val = sess.run(err_prod,feed_dict={self.ix:itemtrain})
        return err_val
    '''

    def train_model(self,sess,usertrain,item_txt_train,item_img_train,tr_rating_mat):
            _ = sess.run([self.train_step], feed_dict={self.ph_user_inp:usertrain,self.ph_prod_img_inp:item_img_train,self.ph_prod_txt_inp:item_txt_train,self.ph_utility_mat:tr_rating_mat})
        
    def validate_model(self,sess,usertrain,item_txt_train,item_img_train,tr_rating_mat):
        error_val,rating_err = self.error()
        err_val,rating_err_val,user_embedding,prod_embedding,prod_txt_reconstruction,prod_img_recons,rating_pred = sess.run([error_val,rating_err,self.user_embeddings,self.prod_embeddings,self.ph_prod_txt_inp,self.ph_prod_img_inp,self.rating_pred], feed_dict={self.ph_user_inp:usertrain,self.ph_prod_img_inp:item_img_train,self.ph_prod_txt_inp:item_txt_train,self.ph_utility_mat:tr_rating_mat})
        np.savetxt("../data/test/prod_encoding.csv", prod_embedding, delimiter=",")
        np.savetxt("../data/test/user_encoding.csv", user_embedding, delimiter=",")
        np.savetxt("../data/test/rating_pred.csv", rating_pred, delimiter=",")
        #print(uh_mat,ih_mat,pred_mat)
        return rating_err_val
    
    def test_model(self,sess,user_data,item_txt_data,item_img_data):
        pred_mat = sess.run([self.rating_pred], feed_dict={self.ph_user_inp:user_data,self.ph_prod_txt_inp:item_txt_data,self.ph_prod_img_inp:item_img_data})
        return pred_mat

    def save_weights(self,sess):
        # https://www.tensorflow.org/guide/saved_model
        saver = tf.train.Saver()
        save_path = saver.save(sess, "./saved_model/model.ckpt")
        print("Model saved in path: %s" % save_path)


    def restore_model(self,sess):        
        saver = tf.train.Saver()
        saver.restore(sess, "./saved_model/model.ckpt")

    '''
    def validate_and_check_early_stopping(self,sess,val_ratings,usertrain,prodtrain):
        self.save_weights(sess)
        ''VALIDATION ''
        val_userIds = val_ratings['userId'].unique()
        val_prodIds = val_ratings['productId'].unique()
        map_user_id_to_index = dict(zip(val_userIds,range(len(val_userIds))))
        map_prod_id_to_index = dict(zip(val_prodIds,range(len(val_prodIds))))
        
        val_ratings_mat = pd.DataFrame(np.zeros((len(val_userIds),len(val_prodIds))))
        for row_index in range(len(val_ratings)):
            userindex = map_user_id_to_index[val_ratings.loc[row_index]['userId']]
            prodindex = map_prod_id_to_index[val_ratings.loc[row_index]['productId']]
            val_ratings_mat.loc[userindex][prodindex] = val_ratings.loc[row_index]['rating']
        
        val_user = usertrain.loc[val_userIds].values
        val_item = prodtrain.loc[val_prodIds].values
        np.savetxt("../data/test/actual_ratings.csv", val_ratings_mat.values, delimiter=",")
        _,loss_value = self.validate_model(sess,val_user,val_item,val_ratings_mat)
        #print(loss_value,self.best_loss)
        if (loss_value < self.best_loss):
            self.save_weights(sess)
            print("Triggered Early Stopping")
            self.STOP = True
        return loss_value
    '''