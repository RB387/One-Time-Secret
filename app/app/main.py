from fastapi import FastAPI, HTTPException
import uuid
from .dbmanager import DataBaseManager
from .encryption import Crypto
from .config import *


app = FastAPI()

manager = DataBaseManager(DB_PATH, LIFE_TIME_HOURS)
crypto = Crypto(SECRET_KEY)


def generate_id() -> str:
    '''Generates uniq id

    UUIDs have 122 bits of entropy
    so the chance of two random UUIDs colliding is about 10^-37
    Chance of getting a collision is 1 in 50 billion if you generate 2^46 UUIDs

    But for uniq guarantee in this function used loop
    that generates new UUID if collision happened

    Examples:
        >>>print(generate_id())
        UUID('cefeb69f-9d43-4ab2-96ca-cb6a77ee1ede')

    :return: uniq UUID
    '''
    id = uuid.uuid4()
    while manager.does_exist(id):
        id = uuid.uuid4()
    return id


@app.get('/generate')
async def generate(secret: str='', password: str='') -> str:
    '''Secret generator

    Creates new one time secret that can be accessed by id
    Text message and password encrypts with AES and codes with base64
    Deletes secret after first visit

    If secret and/or password is empty, returns 400 error

    Examples:
       >>>response = client.get('/generate/?secret=TEXT-MESSAGE&password=PASS')
       >>>print(response.json())
       {'secret-key': f60a0191-ce68-44dd-b741-04543b97cdef}

       >>>no_response = client.get('/generate/?secret=TEXT-MESSAGE')
       >>>print(no_response.status_code)
       400

    :param secret: text message of secret
    :param password: password for the secret
    :return: JSON with id of generated secret
            that can be accessed by key 'secret-key'
            {'secret-key': id}
    '''
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
    '''View secret by secret-key

    Secret deletes after first visit

    If such secret doesn't exit, returns 404 error

    Examples:
        >>>secret_key = '/secrets/f60a0191-ce68-44dd-b741-04543b97cdef/'
        >>>response = client.get(secret_key)
        >>>print(response.json())
        {'secret': 'TEXT-MESSAGE'}

        >>>no_response = client.get(secret_key)
        >>>print(no_response.status_code)
        404

    :param secret_key: key to access
    :return: JSON with text message of secret
            that can be accessed by key 'secret'
            {'secret' message}
    '''
    if not manager.does_exist(secret_key):
        error = 'Not found. This secret was deleted or never existed'
        raise HTTPException(status_code=404, detail=error)
    secret = manager.select(secret_key)
    manager.delete(secret_key)
    return {'secret': crypto.decrypt(secret)}
