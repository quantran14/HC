import os
import sys
import glob
import datetime
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras.models import load_model

import losses


def time_to_timestr():
    timestr = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    return timestr


custom_objects = {"jaccard_loss": losses.jaccard_loss,
                  "jaccard_index": losses.jaccard_index,
                  "dice_loss": losses.dice_loss,
                  "dice_coeff": losses.dice_coeff}


def load_model(file_path):
    model = tf.keras.models.load_model(file_path, custom_objects=custom_objects)

    return model
