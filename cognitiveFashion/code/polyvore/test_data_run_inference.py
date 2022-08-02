# Copyright 2017 Xintong Han. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Run the inference of Bi-LSTM model given input images."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json

import tensorflow as tf
import pickle as pkl
import numpy as np
import configuration
import polyvore_model_bi as polyvore_model

FLAGS = tf.flags.FLAGS

tf.flags.DEFINE_string("checkpoint_path", "",
                       "Model checkpoint file or directory containing a "
                       "model checkpoint file.")
tf.flags.DEFINE_string("json_file", "data/label/test-no-dup.json",
                       "Json file containing the inference data.")
tf.flags.DEFINE_string("image_dir", "data/images_test",
                       "Directory containing images.")
tf.flags.DEFINE_string("feature_file", "data/features/test_features_test.pkl",
                       "Directory to save the features")
tf.flags.DEFINE_string("rnn_type", "", "Type of RNN.")


import os

def load_images_from_folder(image_dir):
    images = {}
    for filename in os.listdir(image_dir):
    	filename1 = os.path.join(FLAGS.image_dir, filename)

        with tf.gfile.GFile(filename1, 'rb') as f:
        	image_feed = f.read()
        	images[filename1] = image_feed
    return images



def main(_):
  if os.path.isfile(FLAGS.feature_file):
    print("Feature file already exist.")
    return
  # Build the inference graph.
  g = tf.Graph()
  with g.as_default():
    model_config = configuration.ModelConfig()
    model_config.rnn_type = FLAGS.rnn_type
    model = polyvore_model.PolyvoreModel(model_config, mode="inference")
    model.build()
    saver = tf.train.Saver()

  g.finalize()
  sess = tf.Session(graph=g)
  saver.restore(sess, FLAGS.checkpoint_path)

  test_json = json.load(open(FLAGS.json_file))
  k = 0

  # Save image ids and features in a dictionary.
  test_features = dict()


  image_feat = []
  image_rnn_feat = []
  ids = []
  k = k + 1
  #print(str(k) + " : " + set_id)
  for image in os.listdir(FLAGS.image_dir):
      filename = os.path.join(FLAGS.image_dir, image)
      with tf.gfile.GFile(filename, 'rb') as f:
        image_feed = f.read()

      [feat, rnn_feat] = sess.run([model.image_embeddings,
                                   model.rnn_image_embeddings],
                                  feed_dict={"image_feed:0": image_feed})
      
      image_name = image
      #image_name = set_id + "_" + str(image["index"])
      test_features[image_name] = dict()
      test_features[image_name]["image_feat"] = np.squeeze(feat)
      test_features[image_name]["image_rnn_feat"] = np.squeeze(rnn_feat)






















  '''images = load_images_from_folder(FLAGS.image_dir)
  image_feat = []
  image_rnn_feat = []
  ids = []
  for image_feed in images:




      [feat, rnn_feat] = sess.run([model.image_embeddings,
                                   model.rnn_image_embeddings],
                                  feed_dict={"image_feed:0": image_feed})
      
      image_name = set_id + "_" + str(image["index"])
      test_features[image_name] = dict()
      test_features[image_name]["image_feat"] = np.squeeze(feat)
      test_features[image_name]["image_rnn_feat"] = np.squeeze(rnn_feat)'''
  
  with open(FLAGS.feature_file, "wb") as f:
    pkl.dump(test_features, f)


if __name__ == "__main__":
  tf.app.run()
