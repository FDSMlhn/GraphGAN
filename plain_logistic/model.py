from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf


class Model:
    def __init__(self, placeholders, params):
        self.loss = 0
        self.accuracy = 0
        self.mse = 0
        self.training_op = None
        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        self.model_dir = params.model_dir
        self.build(placeholders, params)

    def build(self, placeholders, params):
        raise NotImplementedError

    def save(self, sess=None):
        if not sess:
            raise AttributeError("TensorFlow session is not provided.")
        saver = tf.train.Saver()
        save_path = saver.save(sess, '{}{}'.format(self.model_dir, self.model_name), global_step=self.global_step)
        save_path = saver.save(sess, '{}{}-latest'.format(self.model_dir, self.model_name) )
        print("\nModel is saved in file: %s" % save_path)

    def load(self, sess=None, global_step=None):
        if not sess:
            raise AttributeError("TensorFlow session is not provided.")
        saver = tf.train.Saver()
        save_path = '{}{}-latest'.format(self.model_dir, self.model_name)
        if global_step:
            save_path = '{}{}-{}'.format(self.model_dir, self.model_name, global_step)
        saver.restore(sess, save_path)
        print("\nModel restored from file: %s" % save_path)


class BlinearDecoder(Model):
    def __init__(self, placeholders, params):
        super().__init__(placeholders, params)
        self.model_name = 'BilinearDecoder'

    def build(self, placeholders, params):
        # === pass model parameters ===
        user_features_columns = params.user_features_columns
        item_features_columns = params.item_features_columns

        dim_user_raw = params.dim_user_raw
        dim_item_raw = params.dim_item_raw
        dim_user_embedding = params.dim_user_embedding
        dim_item_embedding = params.dim_item_embedding

        num_basis = params.num_basis
        classes = params.classes
        dropout = params.dropout
        regularizer = tf.contrib.layers.l2_regularizer
        regularizer_parameter = params.regularizer_parameter
        learning_rate = params.learning_rate
        loss_function = tf.losses.sparse_softmax_cross_entropy
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)

        # === input data ===
        user_features_all = tf.feature_column.input_layer(placeholders['u_features'],
                                                          user_features_columns)
        item_features_all = tf.feature_column.input_layer(placeholders['v_features'],
                                                          item_features_columns)
        user_features_all = tf.cast(user_features_all, tf.float64)
        item_features_all = tf.cast(item_features_all, tf.float64)

        # get batch
        user_features_batch = tf.sparse.matmul(placeholders['user_id'], user_features_all)
        item_features_batch = tf.sparse.matmul(placeholders['item_id'], item_features_all)

        # === dense layers at the first level ===
        f_user = tf.layers.dense(user_features_batch,
                                 units=dim_user_raw,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=True,
                                 name='user_features')
        f_item = tf.layers.dense(item_features_batch,
                                 units=dim_item_raw,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=True,
                                 name='item_features')

        # batch norm
        f_user = tf.cast(f_user, tf.float32)
        f_item = tf.cast(f_item, tf.float32)

        f_user = tf.contrib.layers.batch_norm(f_user,
                                              is_training=placeholders['training'],
                                              trainable=True)
        f_item = tf.contrib.layers.batch_norm(f_item,
                                              is_training=placeholders['training'],
                                              trainable=True)

        f_user = tf.cast(f_user, tf.float64)
        f_item = tf.cast(f_item, tf.float64)

        # activiation
        f_user = tf.nn.relu(f_user)
        f_item = tf.nn.relu(f_item)

        # dropout
        f_user = tf.layers.dropout(f_user, rate=dropout, training=placeholders['training'])
        f_item = tf.layers.dropout(f_item, rate=dropout, training=placeholders['training'])

        # === dense layers at the 2nd level ===
        f_user = tf.layers.dense(f_user,
                                 units=dim_user_embedding,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=False,
                                 name='f_user')
        f_item = tf.layers.dense(f_item,
                                 units=dim_item_embedding,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=False,
                                 name='f_item')

        user_embedding = tf.nn.relu(f_user)
        item_embedding = tf.nn.relu(f_item)

        # === decoder ===
        weights_decoder = []
        with tf.variable_scope('decoder'):
            for i in range(num_basis):
                weights = tf.get_variable(name='decoder' + str(i),
                                          shape=[dim_user_embedding,
                                                 dim_item_embedding],
                                          dtype=tf.float64,
                                          trainable=True,
                                          regularizer=regularizer(regularizer_parameter),
                                          initializer=tf.glorot_normal_initializer()
                                          )
                weights_decoder.append(weights)

            weight_combination = tf.get_variable(name='weight_combination',
                                                 shape=[5, num_basis],
                                                 dtype=tf.float64,
                                                 trainable=True,
                                                 regularizer=None,
                                                 initializer=tf.glorot_normal_initializer()
                                                 )

        logits = []
        for row in range(classes):
            kernel = 0
            for k in range(num_basis):
                kernel += weight_combination[row, k] * weights_decoder[k]

            uQ = tf.matmul(user_embedding, kernel)
            uQv = tf.reduce_sum(tf.multiply(uQ, item_embedding), axis=1)
            logits.append(uQv)
        logits = tf.stack(logits, axis=1)

        # predicted labels
        predicted_classes = tf.argmax(logits, 1)

        # === performance measure ===
        self.loss = loss_function(labels=placeholders['labels'], logits=logits)
        self.accuracy = tf.contrib.metrics.accuracy(labels=placeholders['labels'], predictions=predicted_classes)
        self.mse = tf.losses.mean_squared_error(labels=placeholders['labels'], predictions=predicted_classes,
                                                reduction=tf.Reduction.SUM_OVER_BATCH_SIZE)
        # summary
        tf.summary.scalar('loss', self.loss)
        tf.summary.scalar('accuracy', self.accuracy)
        tf.summary.scalar('mse', self.mse)

        # training
        self.training_op = optimizer.minimize(self.loss, global_step=self.global_step)


class LogisticDecoder(Model):
    def __init__(self, placeholders, params):
        super().__init__(placeholders, params)
        self.model_name = 'LogisticsDecoder'

    def build(self, placeholders, params):
        # === pass model parameters ===
        user_features_columns = params.user_features_columns
        item_features_columns = params.item_features_columns

        dim_user_raw = params.dim_user_raw
        dim_item_raw = params.dim_item_raw
        dim_user_embedding = params.dim_user_embedding
        dim_item_embedding = params.dim_item_embedding

        classes = params.classes
        dropout = params.dropout
        regularizer = tf.contrib.layers.l2_regularizer
        regularizer_parameter = params.regularizer_parameter
        learning_rate = params.learning_rate
        loss_function = tf.losses.sparse_softmax_cross_entropy
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)

        # === input data ===
        user_features_all = tf.feature_column.input_layer(placeholders['u_features'],
                                                          user_features_columns)
        item_features_all = tf.feature_column.input_layer(placeholders['v_features'],
                                                          item_features_columns)
        user_features_all = tf.cast(user_features_all, tf.float64)
        item_features_all = tf.cast(item_features_all, tf.float64)

        # get batch
        user_features_batch = tf.sparse.matmul(placeholders['user_id'], user_features_all)
        item_features_batch = tf.sparse.matmul(placeholders['item_id'], item_features_all)

        # === dense layers at the first level ===
        f_user = tf.layers.dense(user_features_batch,
                                 units=dim_user_raw,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=True,
                                 name='user_features')
        f_item = tf.layers.dense(item_features_batch,
                                 units=dim_item_raw,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=True,
                                 name='item_features')

        # batch norm
        f_user = tf.cast(f_user, tf.float32)
        f_item = tf.cast(f_item, tf.float32)

        f_user = tf.contrib.layers.batch_norm(f_user,
                                              is_training=placeholders['training'],
                                              trainable=True)
        f_item = tf.contrib.layers.batch_norm(f_item,
                                              is_training=placeholders['training'],
                                              trainable=True)

        f_user = tf.cast(f_user, tf.float64)
        f_item = tf.cast(f_item, tf.float64)

        # activiation
        f_user = tf.nn.relu(f_user)
        f_item = tf.nn.relu(f_item)

        # dropout
        f_user = tf.layers.dropout(f_user, rate=dropout, training=placeholders['training'])
        f_item = tf.layers.dropout(f_item, rate=dropout, training=placeholders['training'])

        # === dense layers at the 2nd level ===
        f_user = tf.layers.dense(f_user,
                                 units=dim_user_embedding,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=False,
                                 name='f_user')
        f_item = tf.layers.dense(f_item,
                                 units=dim_item_embedding,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=False,
                                 name='f_item')

        user_embedding = tf.nn.relu(f_user)
        item_embedding = tf.nn.relu(f_item)

        # === decoder ===
        logits = tf.stack([user_embedding, item_embedding], axis=1)
        logits = tf.layers.dense(logits,
                                 units=classes,
                                 activation=None,
                                 kernel_initializer=tf.glorot_normal_initializer(),
                                 kernel_regularizer=regularizer(regularizer_parameter),
                                 use_bias=True,
                                 name='decoder')

        # predicted labels
        predicted_classes = tf.argmax(logits, 1)

        # === performance measure ===
        self.loss = loss_function(labels=placeholders['labels'], logits=logits)
        self.accuracy = tf.contrib.metrics.accuracy(labels=placeholders['labels'], predictions=predicted_classes)
        self.mse = tf.losses.mean_squared_error(labels=placeholders['labels'], predictions=predicted_classes,
                                                reduction=tf.Reduction.SUM_OVER_BATCH_SIZE)
        # summary
        tf.summary.scalar('loss', self.loss)
        tf.summary.scalar('accuracy', self.accuracy)
        tf.summary.scalar('mse', self.mse)

        # training
        self.training_op = optimizer.minimize(self.loss, global_step=self.global_step)


