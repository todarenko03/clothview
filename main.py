import os
import uvicorn
import firebase_admin
import pyrebase
import json
from dotenv import load_dotenv

from fastapi import FastAPI, Request, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import credentials, auth
from celery_worker import predict_breathability, predict_textile_classification, predict_drape_rigidity

app = FastAPI()

load_dotenv()

d = {
  "type": os.getenv("TYPE"),
  "project_id": os.getenv("PROJECT_ID"),
  "private_key_id": os.getenv("PRIVATE_KEY_ID"),
  "private_key":os.getenv("PRIVATE_KEY"),
  "client_email": os.getenv("client_email"),
  "client_id": os.getenv("client_id"),
  "auth_uri": os.getenv("auth_uri"),
  "token_uri": os.getenv("token_uri"),
  "auth_provider_x509_cert_url": os.getenv("auth_provider_x509_cert_url"),
  "client_x509_cert_url": os.getenv("client_x509_cert_url"),
  "universe_domain": os.getenv("universe_domain")
}

cred = credentials.Certificate(d)
firebase = firebase_admin.initialize_app(cred)
pb = pyrebase.initialize_app(json.load(open('firebase_config.json')))
allow_all = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_all,
    allow_credentials=True,
    allow_methods=allow_all,
    allow_headers=allow_all,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.post("/signup", include_in_schema=False)
async def signup(request: Request):
    req = await request.json()
    if 'email' not in req or 'password' not in req:
        return HTTPException(status_code=400, detail={'message': 'Error! Missing Email or Password'})
    email = req['email']
    password = req['password']
    if email is None or password is None:
        return HTTPException(status_code=400, detail={'message': 'Error! Missing Email or Password'})
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return JSONResponse(content={'message': f'Successfully created user {user.uid}'}, status_code=200)
    except:
        return HTTPException(status_code=400, detail={'message': 'Error Creating User'})


@app.post("/login", include_in_schema=False)
async def login(request: Request):
    req_json = await request.json()
    email = req_json['email']
    password = req_json['password']
    try:
        user = pb.auth().sign_in_with_email_and_password(email, password)
        token = user['idToken']
        return JSONResponse(content={'token': token}, status_code=200)
    except:
        return HTTPException(detail={'message': 'There was an error logging in'}, status_code=400)

async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        return auth.verify_id_token(token)
    except:
        raise HTTPException(status_code=401, detail='Invalid token')


@app.get("/predict-breathability")
async def predict_breathability_method(user_data: str = Depends(verify_token), img: UploadFile = File(...)):
    opened_img = await img.read()
    
    breathability_result = predict_breathability.delay(opened_img).get()

    body = {
        'breathability':  breathability_result
    }

    return JSONResponse(content=body, status_code=200)


@app.get("/predict-textile-classification")
async def predict_textile_classification_method(user_data: str = Depends(verify_token), img: UploadFile = File(...)):
    opened_img = await img.read()
    
    textile_classification_result = predict_textile_classification.delay(opened_img).get()

    body = {
        'textile_classification': textile_classification_result
    }

    return JSONResponse(content=body, status_code=200)


@app.get("/predict-drape-rigidity")
async def predict_drape_rigidity_method(user_data: str = Depends(verify_token),
                               Height:float = 0,
                               Density: int = 0,
                               Consist: int = 0,
                               Thread: int = 0,
                               is_fabric: int = 0,
                               is_knitwear: int = 1):
    
    prediction = predict_drape_rigidity.delay([Height, Density, Consist, 
                                 Thread, is_fabric, is_knitwear]).get()

    body = {
        'drape': prediction[0],
        'rigidity': prediction[1]
    }

    return JSONResponse(content=body, status_code=200)


if __name__ == "__main__":
    uvicorn.run("main:app")
