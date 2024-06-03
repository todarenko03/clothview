from celery import Celery
from breathability import predict_breathability_class
from textile_classification import predict_textile_class
from drape import predict_drape_value

celery_app = Celery('celery_worker', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@celery_app.task(name="predict")
def predict(img):
    breathability_result = predict_breathability_class(img)
    textile_classification_result = predict_textile_class(img)
    
    return breathability_result, textile_classification_result

@celery_app.task(name="predict_breathability")
def predict_breathability(img):
    breathability_result = predict_breathability_class(img)
    
    return breathability_result

@celery_app.task(name="predict_textile_classification")
def predict_textile_classification(img):
    textile_classification_result = predict_textile_class(img)
    
    return textile_classification_result

@celery_app.task(name="predict_drape")
def predict_drape(params):
    drape_result = predict_drape_value(params)
    
    return drape_result