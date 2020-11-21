# -*- coding: utf-8 -*-
"""common_implementations.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1huVmjSC6pmQZbQjo4daANH7biOqCF7rZ
"""
from sklearn.datasets import load_files
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix

from keras.utils import np_utils
from keras.preprocessing import image
from keras.utils.vis_utils import plot_model
from keras.callbacks import ModelCheckpoint
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D
from keras.layers import Dropout, Flatten, Dense
from keras.models import Sequential

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
from google.colab import drive
from keras.preprocessing.image import ImageDataGenerator
from math import ceil


def drive_atuh_for_dataset_download():
    # Authenticate and create the PyDrive client.
    # This only needs to be done once per notebook.
    auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive_auth = GoogleDrive(gauth)
    file_id = '1ins8Y329AMJdkPbi_5AIoJotYsAlq0Fw'  # URL id.
    downloaded = drive_auth.CreateFile({'id': file_id})
    downloaded.GetContentFile('driver.zip')
    file_id = '1OaEIIqD3sHmhaoTuEWu0hNidCU_atGZR'  # URL id.
    downloaded = drive_auth.CreateFile({'id': file_id})
    downloaded.GetContentFile('mini_test.zip')
    file_id = '1lU_FfEqLONGAOUmAAZm4mGoqmCVY4T7a'  # URL id.
    downloaded = drive_auth.CreateFile({'id': file_id})
    downloaded.GetContentFile('driver_imgs_list.csv')
    file_id = '1l7E6XI_bokxD2XCdZueJXYsBbrFQPD_J'  # URL id.
    downloaded = drive_auth.CreateFile({'id': file_id})
    downloaded.GetContentFile('common_implementations.py')


def mount_drive():
    drive.mount('/content/gdrive')


# define function to load datasets
def load_dataset(path):
    data = load_files(path)
    files = np.array(data['filenames'])
    targets = np_utils.to_categorical(np.array(data['target']), 10)
    return files, targets


def print_image_data(train_files, valid_files):
    # print statistics about the dataset
    print('There are %s total images.\n' % len(np.hstack([train_files, valid_files])))
    print('There are %d training images.' % len(train_files))
    print('There are %d total training categories.' % len(names))
    print('There are %d validation images.' % len(valid_files))


def data_exploration():
    ##Data Exploration
    df = pd.read_csv("/content/driver_imgs_list.csv", header='infer')
    print(df['classname'].head(3))
    print(df.iloc[:, 1].describe())
    print("\n Image Counts")
    print(df['classname'].value_counts(sort=False))
    return df


# Commented out IPython magic to ensure Python compatibility.
def data_visualization(df):
    # Visualization
    # Pretty display for notebooks
    #   %matplotlib inline

    nf = df['classname'].value_counts(sort=False)
    labels = df['classname'].value_counts(sort=False).index.tolist()
    y = np.array(nf)
    width = 1 / 1.5
    N = len(y)
    x = range(N)

    fig = plt.figure(figsize=(20, 15))
    ay = fig.add_subplot(211)

    plt.xticks(x, labels, size=15)
    plt.yticks(size=15)

    ay.bar(x, y, width, color="blue")

    plt.title('Bar Chart', size=25)
    plt.xlabel('classname', size=15)
    plt.ylabel('Count', size=15)

    plt.show()


def path_to_tensor(img_path):
    img = image.load_img(img_path, target_size=(64, 64))
    x = image.img_to_array(img)
    # convert 3D tensor to 4D tensor with shape (1, 64, 64, 3) and return 4D tensor
    return np.expand_dims(x, axis=0)


def paths_to_tensor(img_paths):
    list_of_tensors = [path_to_tensor(img_path) for img_path in tqdm(img_paths)]
    return np.vstack(list_of_tensors)


def print_accuracy_plots(fit_output):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))
    ax1.plot(fit_output.history['loss'], color='b', label="Training loss")
    ax1.plot(fit_output.history['val_loss'], color='r', label="validation loss")
    ax1.set_xticks(np.arange(1, 25, 1))
    ax1.set_yticks(np.arange(0, 1, 0.1))

    ax2.plot(fit_output.history['accuracy'], color='b', label="Training accuracy")
    ax2.plot(fit_output.history['val_accuracy'], color='r', label="Validation accuracy")
    ax2.set_xticks(np.arange(1, 25, 1))

    legend = plt.legend(loc='best', shadow=True)
    plt.tight_layout()
    plt.show()


def print_confusion_matrix(confusion_matrix, class_names, figsize=(10, 7), fontsize=14):
    df_cm = pd.DataFrame(
        confusion_matrix, index=class_names, columns=class_names,
    )
    fig = plt.figure(figsize=figsize)
    try:
        heatmap = sns.heatmap(df_cm, annot=True, fmt="d")
    except ValueError:
        raise ValueError("Confusion matrix values must be integers.")
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=45, ha='right', fontsize=fontsize)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def print_heatmap(n_labels, n_predictions, class_names):
    labels = n_labels  # sess.run(tf.argmax(n_labels, 1))
    predictions = n_predictions  # sess.run(tf.argmax(n_predictions, 1))

    #     confusion_matrix = sess.run(tf.contrib.metrics.confusion_matrix(labels, predictions))
    matrix = confusion_matrix(labels.argmax(axis=1), predictions.argmax(axis=1))
    row_sum = np.sum(matrix, axis=1)
    w, h = matrix.shape

    c_m = np.zeros((w, h))

    for i in range(h):
        c_m[i] = matrix[i] * 100 / row_sum[i]

    c = c_m.astype(dtype=np.uint8)
    heatmap = print_confusion_matrix(c, class_names, figsize=(18, 10), fontsize=20)


def print_metrics(ypred, valid_targets):
    # manipulates data
    ypred_class = np.argmax(ypred, axis=1)
    ytest = np.argmax(valid_targets, axis=1)

    accuracy = accuracy_score(ytest, ypred_class)
    print('Accuracy: %f' % accuracy)
    # precision tp / (tp + fp)
    precision = precision_score(ytest, ypred_class, average='weighted')
    print('Precision: %f' % precision)
    # recall: tp / (tp + fn)
    recall = recall_score(ytest, ypred_class, average='weighted')
    print('Recall: %f' % recall)
    # f1: 2 tp / (2 tp + fp + fn)
    f1 = f1_score(ytest, ypred_class, average='weighted')
    print('F1 score: %f' % f1)


def image_datagenerator(batch_size=40, target_size=(64, 64), train_path='/content/train/',
                        validation_path='/content/validation/',
                        test_path='/content/mini_test'):
    image_datagen = ImageDataGenerator(
        rotation_range=10,  # range (0-180) within which to randomly rotate pictures
        # width_shift_range=0.2, # as fraction of width, range within to which randomly translate pictures
        # height_shift_range=0.2, # same as above, but with height
        rescale=1. / 255,
        # RBG coefficient values 0-255 are too hight to process. instead, represent them as values 0-1
        # shear_range=0.2, # random shearing transformations
        zoom_range=0.1,  # randomly zooming inside pictures
        horizontal_flip=False,
        fill_mode='nearest')  # strategy for filling in newly created pixels, which can appear after a rotation or a width/height shift
    train_generator = image_datagen.flow_from_directory(
        train_path,  # this is the target directory
        target_size=target_size,  # all images will be resized to 150x150
        batch_size=batch_size,
        shuffle=False,
        class_mode='categorical')  # since we use binary_crossentropy loss, we need binary labels

    # this is a similar generator, for validation data
    val_generator = image_datagen.flow_from_directory(
        validation_path,
        target_size=target_size,
        batch_size=batch_size,
        shuffle=False,
        class_mode='categorical')

    # this is a similar generator, for validation data
    test_generator = image_datagen.flow_from_directory(
        test_path,
        target_size=target_size,
        batch_size=batch_size,
        shuffle=False,
        class_mode='categorical')

    return train_generator, val_generator, test_generator


def split_train_val():
    import os
    from sklearn.model_selection import train_test_split

    NUM_CLASSES = 10
    data_path = '/content/imgs/train/'

    for i in range(NUM_CLASSES):

        curr_dir_path = data_path + 'c' + str(i) + '/'

        xtrain = labels = os.listdir(curr_dir_path)

        x, x_test, y, y_test = train_test_split(xtrain, labels, test_size=0.2, train_size=0.8)
        x_train, x_val, y_train, y_val = train_test_split(x, y, test_size=0.25, train_size=0.75)

        for x in x_train:

            if (not os.path.exists('train/' + 'c' + str(i) + '/')):
                os.makedirs('train/' + 'c' + str(i) + '/')

            os.rename(data_path + 'c' + str(i) + '/' + x, 'train/' + 'c' + str(i) + '/' + x)

        for x in x_test:

            if (not os.path.exists('test/' + 'c' + str(i) + '/')):
                os.makedirs('test/' + 'c' + str(i) + '/')

            os.rename(data_path + 'c' + str(i) + '/' + x, 'test/' + 'c' + str(i) + '/' + x)

        for x in x_val:

            if (not os.path.exists('validation/' + 'c' + str(i) + '/')):
                os.makedirs('validation/' + 'c' + str(i) + '/')

            os.rename(data_path + 'c' + str(i) + '/' + x, 'validation/' + 'c' + str(i) + '/' + x)


def return_validator_labels(val_generator,batch_size):
    number_of_examples = len(val_generator.filenames)
    number_of_generator_calls = ceil(number_of_examples / (1.0 * batch_size))
    # 1.0 above is to skip integer division
    test_labels = []
    for i in range(0, int(number_of_generator_calls)):
        test_labels.extend(np.array(val_generator[i][1]).tolist())
    validation_label = np.asarray(test_labels)
    return validation_label