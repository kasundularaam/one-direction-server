import numpy as np
from tensorflow.keras.preprocessing import image
import tensorflow as tf


class_names = ['forward', 'left', 'no_arrow', 'right']


model = tf.keras.models.load_model('one_direction_model.h5')


def predict_arrow(image_path):
    img = image.load_img(image_path, target_size=(64, 64))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0

    prediction = model.predict(img_array)
    predicted_class = class_names[np.argmax(prediction)]
    return predicted_class
