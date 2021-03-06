import os
import sys
import numpy as np

import tensorflow as tf
from tensorflow.keras import Input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv2D, BatchNormalization, Activation, MaxPooling2D, Dropout, Conv2DTranspose, concatenate, ZeroPadding2D

from seg.utils import load_pretrain_model


def conv2d_block(input, n_filters, kernel_size=3, batchnorm=True):
    # first layer
    x = Conv2D(filters=n_filters,
               kernel_size=kernel_size,
               kernel_initializer='he_normal',
               padding='same')(input)
    if batchnorm:
        x = BatchNormalization()(x)
    x = Activation('relu')(x)

    # second layer
    x = Conv2D(filters=n_filters,
               kernel_size=kernel_size,
               kernel_initializer='he_normal',
               padding='same')(x)
    if batchnorm:
        x = BatchNormalization()(x)
    x = Activation('relu')(x)

    return x


def padding(x, y):
    x_shape = x.shape.as_list()
    y_shape = y.shape.as_list()

    if x.shape[1] > y_shape[1]:
        y = ZeroPadding2D(((1, 0), (0, 0)), data_format="channels_last")(y)
    if x.shape[1] < y_shape[1]:
        x = ZeroPadding2D(((1, 0), (0, 0)), data_format="channels_last")(x)
    if x.shape[2] > y_shape[2]:
        y = ZeroPadding2D(((0, 0), (1, 0)), data_format="channels_last")(y)
    if x.shape[2] < y_shape[2]:
        x = ZeroPadding2D(((0, 0), (1, 0)), data_format="channels_last")(x)

    return x, y


def unet(input_size=(216, 320, 1), n_filters=64, batchnorm=True, dropout_rate=0.1, freeze=False, freeze_at=0):
    inputs = Input(input_size, name="img")

    # contraction path
    c1 = conv2d_block(inputs, n_filters*1, kernel_size=3, batchnorm=batchnorm)
    p1 = MaxPooling2D((2, 2))(c1)
    p1 = Dropout(dropout_rate)(p1)

    c2 = conv2d_block(p1, n_filters * 2, kernel_size=3, batchnorm=batchnorm)
    p2 = MaxPooling2D((2, 2))(c2)
    p2 = Dropout(dropout_rate)(p2)

    c3 = conv2d_block(p2, n_filters * 4, kernel_size=3, batchnorm=batchnorm)
    p3 = MaxPooling2D((2, 2))(c3)
    p3 = Dropout(dropout_rate)(p3)

    c4 = conv2d_block(p3, n_filters * 8, kernel_size=3, batchnorm=batchnorm)
    p4 = MaxPooling2D((2, 2))(c4)
    p4 = Dropout(dropout_rate)(p4)

    c5 = conv2d_block(p4, n_filters * 16, kernel_size=3, batchnorm=batchnorm)

    # expansion path
    u6 = Conv2DTranspose(n_filters * 8, 3, strides=(2, 2), padding='same')(c5)
    u6, c4 = padding(u6, c4)
    u6 = concatenate([u6, c4])
    u6 = Dropout(dropout_rate)(u6)
    c6 = conv2d_block(u6, n_filters * 8, kernel_size=3, batchnorm=batchnorm)

    u7 = Conv2DTranspose(n_filters * 4, 3, strides=(2, 2), padding='same')(c6)
    u7, c3 = padding(u7, c3)
    u7 = concatenate([u7, c3])
    u7 = Dropout(dropout_rate)(u7)
    c7 = conv2d_block(u7, n_filters * 4, kernel_size=3, batchnorm=batchnorm)

    u8 = Conv2DTranspose(n_filters * 2, 3, strides=(2, 2), padding='same')(c7)
    u8, c2 = padding(u8, c2)
    u8 = concatenate([u8, c2])
    u8 = Dropout(dropout_rate)(u8)
    c8 = conv2d_block(u8, n_filters * 2, kernel_size=3, batchnorm=batchnorm)

    u9 = Conv2DTranspose(n_filters * 1, 3, strides=(2, 2), padding='same')(c8)
    u9, c1 = padding(u9, c1)
    u9 = concatenate([u9, c1])
    u9 = Dropout(dropout_rate)(u9)
    c9 = conv2d_block(u9, n_filters * 1, kernel_size=3, batchnorm=batchnorm)

    outputs = Conv2D(1, (1, 1), activation='sigmoid')(c9)
    model = Model(inputs=[inputs], outputs=[outputs], name="UNet")

    if freeze:
        fine_tune_at = freeze_at
        model_tmp = load_pretrain_model("../models/model_unet.hdf5")

        for layer, layer_tmp in zip(model.layers[:fine_tune_at], model_tmp.layers[:fine_tune_at]):
            layer.set_weights(layer_tmp.get_weights())
            layer.trainable = False

    model.summary()
    # tf.keras.utils.plot_model(model, show_shapes=True)

    return model


if __name__ == "__main__":
    model = unet()
    dot_img_file = '../images/unet.png'
    tf.keras.utils.plot_model(model, to_file=dot_img_file, show_shapes=True)
