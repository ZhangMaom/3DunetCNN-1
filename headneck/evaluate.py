import numpy as np
import nibabel as nib
import os
import argparse
import glob
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import morphology
import scipy.io


def get_background_mask(data):
    return data == 0


def get_organ_mask(data):
    return data == 1


def dice_coefficient(truth, prediction):
    return 2 * np.sum(truth * prediction)/(np.sum(truth) + np.sum(prediction))


def main(args):
    header = ("Background", "Organ")
    masking_functions = (get_background_mask, get_organ_mask)
    rows = list()

    prediction_path = "./headneck/prediction/"+args.organ.lower()+"/"

    for case_folder in glob.glob(prediction_path+"*/"):
        truth_file = os.path.join(case_folder, "truth.nii.gz")
        truth_image = nib.load(truth_file)
        truth = truth_image.get_data()
        prediction_file = os.path.join(case_folder, "prediction.nii.gz")
        prediction_image = nib.load(prediction_file)
        prediction = prediction_image.get_data()
        rows.append([dice_coefficient(func(truth), func(prediction)) for func in masking_functions])

    df = pd.DataFrame.from_records(rows, columns=header)
    df.to_csv(prediction_path+"headneck_scores.csv")


    scores = dict()
    for index, score in enumerate(df.columns):
        values = df.values.T[index]
        scores[score] = values[np.isnan(values) == False]

    plt.boxplot(list(scores.values()), labels=list(scores.keys()))
    plt.ylabel("Dice Coefficient")
    plt.savefig(prediction_path+"validation_scores_boxplot.png")
    plt.close()

    training_df = pd.read_csv("./headneck/isensee2017/training.log")

    # fix logging epochs
    training_df['epoch'] = range(len(training_df.index))
    training_df = training_df.set_index('epoch')


    plt.plot(training_df['loss'].values, label='training loss')
    plt.plot(training_df['val_loss'].values, label='validation loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.xlim((0, len(training_df.index)))
    plt.legend(loc='upper right')
    plt.savefig(prediction_path+'loss_graph.png')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("organ", help="enter segmented organ")
    args = parser.parse_args()
    main(args)
