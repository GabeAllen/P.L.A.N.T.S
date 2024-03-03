import os
import re
import cv2
import time
import shutil
import zipfile
import urllib.request
import numpy as np
from PIL import Image
from os import listdir
from os.path import isfile, join
from random import randrange
import matplotlib.pyplot as plt
import keras
import tensorflow
from keras.models import load_model
from keras.preprocessing import image
from keras_preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D

training_data_directory = 'train'
test_data_directory = 'test'

# # Initiate data processing tools
# training_data_processor = ImageDataGenerator(
#     rescale = 1./255,
#     horizontal_flip = True,
#     zoom_range = 0.2,
#     rotation_range = 10,
#     shear_range = 0.2,
#     height_shift_range = 0.1,
#     width_shift_range = 0.1
# )

# test_data_processor = ImageDataGenerator(rescale = 1./255)

# # Load data into Python
# training_data = training_data_processor.flow_from_directory(
#     training_data_directory,
#     target_size = (256, 256),
#     batch_size = 32,
#     class_mode = 'categorical',
# )

# testing_data = test_data_processor.flow_from_directory(
#     test_data_directory,
#     target_size = (256 ,256),
#     batch_size = 32,
#     class_mode = 'categorical',
#     shuffle = False
# )

# print("Preprocessing Complete")

# # choose model parameters
# num_conv_layers = 2
# num_dense_layers = 1
# layer_size = 32
# num_training_epochs = 10
# MODEL_NAME = 'soil'
# # Initiate model variable
# model = Sequential()

# # begin adding properties to model variable
# # e.g. add a convolutional layer
# model.add(keras.Input(shape=(256,256,3)))
# model.add(Conv2D(layer_size, (3, 3), padding="same", activation="relu"))
# model.add(MaxPooling2D(pool_size=(2, 2)))

# # add additional convolutional layers based on num_conv_layers
# for _ in range(num_conv_layers-1):
#     model.add(Conv2D(layer_size, (3, 3), padding="same", activation="relu"))
#     model.add(MaxPooling2D(pool_size=(2, 2)))

# # reduce dimensionality
# model.add(Flatten())

# # add fully connected "dense" layers if specified
# for _ in range(num_dense_layers):
#     model.add(Dense(layer_size))
#     model.add(Activation('relu'))

# # add output layer
# model.add(Dense(4))
# model.add(Activation('softmax'))

# # compile the sequential model with all added properties
# model.compile(loss='categorical_crossentropy',
#                 optimizer='adam',
#                 metrics=['accuracy'],
#                 )

# # use the data already loaded previously to train/tune the model
# model.fit(training_data,
#             epochs=num_training_epochs,
#             validation_data = testing_data)

# # save the trained model
# model.save('soil_prediction_model.keras')

# print("Model trained and saved")


model_file = os.getcwd()+'/'+'soil_prediction_model.keras'
model = load_model(model_file)
print("loaded model")
def make_prediction(image_fp):
    
    im = cv2.imread(image_fp) # load image
    plt.imshow(im[:,:,[2,1,0]])
    img = image.load_img(image_fp, target_size = (256,256))
    img = image.img_to_array(img)

    image_array = img / 255. # scale the image
    img_batch = np.expand_dims(image_array, axis = 0)
    
    class_ = ["Alluvial soil", "Black Soil", "Clay soil","Red soil"] # possible output values
    #Change to my output values^


    predicted_value = class_[model.predict(img_batch).argmax()]
    #true_value = re.search(r'(Alluvial soil)|(Black Soil)|(Clay soil)|(Red soil)', image_fp)[0]
    #Change to my output values^

    # out = f"""Predicted Soil Type: {predicted_value}
    # True Soil Type: {true_value}
    # Correct?: {predicted_value == true_value}"""

    out = f"""Predicted Soil Type: {predicted_value}"""

    
    return out
#test_image_filepath = test_data_directory + r'\Clay soil\Clay_1.jpg'
#print(make_prediction(test_image_filepath))
