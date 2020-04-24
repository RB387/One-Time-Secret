from fastapi import FastAPI, HTTPException
import config
from .dbmanager import DataBaseManager
from .encryption import Crypto
import uuid

app = FastAPI()

manager = DataBaseManager(config.DB_PATH)
crypto = Crypto(config.SECRET_KEY)


def generate_id() -> str:
    id = uuid.uuid4()
    while manager.does_exist(id):
        id = uuid.uuid4()
    return id


@app.get('/generate')
async def generate(secret: str='', password: str='') -> str:
    if not (secret and password):
        error = 'Bad request. No secret and/or password argument in request.'
        raise HTTPException(status_code=400, detail=error)
    id = generate_id()
    secret = crypto.encrypt(secret)
    password = crypto.encrypt(password)
    manager.insert(id, secret.decode(), password.decode())
    return {'secret-key': id}


@app.get('/secrets/{secret_key}')
async def secrets(secret_key):
    if not manager.does_exist(secret_key):
        error = 'Not found. This secret was deleted or never existed'
        raise HTTPException(status_code=404, detail=error)
    secret = manager.select(secret_key)
    manager.delete(secret_key)
    return {'secret': crypto.decrypt(secret)}
