from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf



class GCMC():
    def __init__(self, placeholders, params):
        self.loss = 0
        self.accuracy = 0
        self.training_op = None

        self.model_name = 'gcmc'
        self.model_dir = params.model_dir
        self.build(placeholders, params)

    def build(self, placeholders, params):
        """
        :param placeholders:
        :param params:
        :return:
        """
        user_features_all = tf.feature_column.input_layer(placeholders['u_features'],
                                                          params.user_features_columns)
        item_features_all = tf.feature_column.input_layer(placeholders['v_features'],
                                                          params.item_features_columns)
        user_features_all = tf.cast(user_features_all, tf.float64)
        item_features_all = tf.cast(item_features_all, tf.float64)

        # get batch
        user_features_batch = tf.sparse.matmul(placeholders['user_id'], user_features_all)
        item_features_batch = tf.sparse.matmul(placeholders['item_id'], item_features_all)

        # get conv
        item_conv, user_conv = [], []
        for star in range(params.classes):
            # TODO: node dropout
            item_conv.append(tf.sparse.matmul(placeholders['item_neigh_conv{}'.format(star)],
                                              user_features_all))
            user_conv.append(tf.sparse.matmul(placeholders['user_neigh_conv{}'.format(star)],
                                              item_features_all))

        # === layers at the first level ===
        # user features
        f_user = tf.layers.dense(user_features_batch,
                                 units=params.dim_user_raw,
                                 activation=tf.nn.relu,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 use_bias=True)
        f_user = tf.layers.dropout(f_user, rate=params.dropout)

        # user convolution TODO: weight sharing
        h_user = []
        for u in user_conv:
            h_u = tf.layers.dense(u,
                                  units=params.dim_user_conv,
                                  activation=tf.nn.relu,
                                  kernel_initializer=tf.glorot_normal_initializer(),
                                  use_bias=False
                                  )
            h_u = tf.layers.dropout(h_u, rate=params.dropout)
            h_user.append(h_u)
        h_user = tf.concat(h_user, axis=1)
        h_user = tf.layers.dropout(h_user, rate=params.dropout)
        # item features
        f_item = tf.layers.dense(item_features_batch,
                                 units=params.dim_item_raw,
                                 activation=tf.nn.relu,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 use_bias=True)
        f_item = tf.layers.dropout(f_item, rate=params.dropout)

        # item convolution TODO: weight sharing
        h_item = []
        for v in item_conv:
            h_v = tf.layers.dense(v,
                                  units=params.dim_item_conv,
                                  activation=tf.nn.relu,
                                  kernel_initializer=tf.glorot_normal_initializer(),
                                  use_bias=False)
            h_v = tf.layers.dropout(h_v, rate=params.dropout)
            h_item.append(h_v)
        h_item = tf.concat(h_item, axis=1)
        h_item = tf.layers.dropout(h_item, rate=params.dropout)

        # === layers at the 2nd level ===
        f_user = tf.layers.dense(f_user,
                                 units=params.dim_user_embedding,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 use_bias=False)
        h_user = tf.layers.dense(h_user,
                                 units=params.dim_user_embedding,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 use_bias=False)
        user_embedding = tf.nn.relu(f_user + h_user)

        f_item = tf.layers.dense(f_item,
                                 units=params.dim_item_embedding,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 use_bias=False)
        h_item = tf.layers.dense(h_item,
                                 units=params.dim_item_embedding,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 use_bias=False)
        item_embedding = tf.nn.relu(f_item + h_item)

        # === decoder ===
        weights_decoder = []
        with tf.variable_scope('decoder'):
            for i in range(params.classes):
                weights = tf.get_variable(name='decoder' + str(i),
                                          shape=[params.dim_user_embedding,
                                                 params.dim_item_embedding],
                                          dtype=tf.float64,
                                          trainable=True,
                                          initializer=tf.glorot_normal_initializer()
                                          )
                weights_decoder.append(weights)

        logits = []
        kernel = 0
        for i, weight in enumerate(weights_decoder):
            kernel += weight
            uQ = tf.matmul(user_embedding, kernel)
            uQv = tf.reduce_sum(tf.multiply(uQ, item_embedding), axis=1)
            logits.append(uQv)

        # predicted labels
        logits = tf.stack(logits, axis=1)
        predicted_classes = tf.argmax(logits, 1)

        # === performance measure ===
        self.loss = tf.losses.sparse_softmax_cross_entropy(labels=placeholders['labels'], logits=logits)
        self.accuracy = tf.contrib.metrics.accuracy(predictions=predicted_classes, labels=placeholders['labels'])

        # summary
        tf.summary.scalar('loss', self.loss)
        tf.summary.scalar('accuracy', self.accuracy)

        # training
        optimizer = tf.train.AdamOptimizer(learning_rate=params.learning_rate)
        self.training_op = optimizer.minimize(self.loss)

    def save(self, sess=None):
        if not sess:
            raise AttributeError("TensorFlow session is not provided.")
        saver = tf.train.Saver()
        save_path = saver.save(sess, '{}{}_{}.ckpt'.format(self.model_dir,
                                                           self.model_name,
                                                           tf.train.get_global_step()
                                                           )
                               )
        print("Model is saved in file: %s" % save_path)




