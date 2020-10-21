import os
import numpy as np
import pandas as pd

from utils import *
from config import *
from data import DataLoader
from ellipse_fitting import ellipse_fit


def generate_submission(predicted_path):
    centers_x = list()
    centers_y = list()
    axes_a = list()
    axes_b = list()
    angles = list()

    pre_images = read_predict_2_numpy(predicted_path)

    df = pd.read_csv("../data/test_set_pixel_size.csv")

    for mask, (i, row) in zip(pre_images, df.iterrows()):
        (xx, yy), (MA, ma), angle = ellipse_fit(mask)

        assert 540 / mask.shape[0] == 800 / mask.shape[1]

        factor = row["pixel size(mm)"] * 540 / mask.shape[0]

        center_x_mm = factor * yy
        center_y_mm = factor * xx
        semi_axes_a_mm = factor * ma / 2
        semi_axes_b_mm = factor * MA / 2
        angle_rad = (-angle * np.pi / 180) % np.pi

        centers_x.append(center_x_mm)
        centers_y.append(center_y_mm)
        axes_a.append(semi_axes_a_mm)
        axes_b.append(semi_axes_b_mm)
        angles.append(angle_rad)

    df = df.drop(columns="pixel size(mm)")
    df["center_x_mm"] = centers_x
    df["center_y_mm"] = centers_y
    df["semi_axes_a_mm"] = axes_a
    df["semi_axes_b_mm"] = axes_b
    df["angle_rad"] = angles

    df.to_csv(
        "../submission/{}.csv".format(predicted_path.split("/")[-1]), index=False)


if __name__ == "__main__":
    generate_submission()
