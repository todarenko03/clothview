import cv2
import numpy as np
from keras.models import load_model
from PIL import Image
from io import BytesIO

textile_clf = load_model('textile_classification_model.h5')

def predict_textile_class(data):
    image = np.array(Image.open(BytesIO(data)))
    pic = cv2.resize(image, (128,128))

    pic_test = np.array(pic, dtype=np.float32) / 255.0
    pic_test = pic_test.reshape(1, 128,128,3)
    
    pred = textile_clf.predict(pic_test, verbose=0)[0]
    
    result = 'ткань' if pred[0] > pred[1] else 'трикотаж'
    
    return result
