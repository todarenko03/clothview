from keras.models import load_model
from PIL import Image
import numpy as np
from io import BytesIO

breathability_model = load_model('breathability_model.h5')
answers = ['< 50', '50 - 100', '100 - 150', '150 >']


def predict_breathability_class(data):
    image = Image.open(BytesIO(data))
    image = image.convert('L')
    image_resized = image.resize((150, 150))
    image_array = np.array(image_resized)

    image_array = np.expand_dims(image_array, axis=0)

    result = breathability_model.predict(image_array)
     
    return answers[np.argmax(result)] 
