import pickle
import numpy as np

with open('drape_xgb.pickle', 'rb') as f:
    drape_model = pickle.load(f)
    
with open('rigidity_xgb.pickle', 'rb') as f:
    rigidity_model = pickle.load(f)
    
def predict_drape_rigidity_value(params):
    params = np.array(params).reshape(1, -1)
    
    return (
            str(drape_model.predict(params)[0]),
            str(rigidity_model.predict(params)[0])
            )
