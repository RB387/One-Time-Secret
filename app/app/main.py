from fastapi import FastAPI, HTTPException
import uuid
from .dbmanager import DataBaseManager
from .encryption import Crypto
from .config import *
from .response_errors import ResponseError


app = FastAPI()

manager = DataBaseManager(DB_PATH, LIFE_TIME_HOURS)
crypto = Crypto(SECRET_KEY)


def generate_id() -> uuid.UUID:
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
    secret_id = uuid.uuid4()

    while manager.does_exist(secret_id):
        secret_id = uuid.uuid4()

    return secret_id


@app.get('/generate')
async def generate(secret: str='', password: str='') -> dict:
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
        raise HTTPException(status_code=400, detail=ResponseError.NO_ARGS.value)

    secret_id = generate_id()
    secret = crypto.encrypt(secret)
    password = crypto.encrypt(password)

    manager.insert(secret_id, secret.decode(), password.decode())

    return {'secret-key': secret_id}


@app.get('/secrets/{secret_key}')
async def secrets(secret_key: str, password: str='') -> dict:
    '''View secret by secret-key and password

    Secret deletes after first visit

    If such secret doesn't exit, returns 404 error
    If password is incorrect, returns 401 error
    If no password in args, returns 400 error

    Examples:
        >>>secret_key = '/secrets/f60a0191-ce68-44dd-b741-04543b97cdef/'
        >>>response = client.get(secret_key)
        >>>print(response.status_code)
        400

        >>>secret_key = '/secrets/f60a0191-ce68-44dd-b741-04543b97cdef?password=wrong'
        >>>response = client.get(secret_key)
        >>>print(response.status_code)
        401

        >>>secret_key = '/secrets/f60a0191-ce68-44dd-b741-04543b97cdef?password=PASS'
        >>>response = client.get(secret_key)
        >>>print(response.json())
        {'secret': 'TEXT-MESSAGE'}

        >>>no_response = client.get(secret_key)
        >>>print(no_response.status_code)
        404

    :param secret_key: key to access
    :param password: password for secret
    :return: JSON with text message of secret
            that can be accessed by key 'secret' if password is correct
            {'secret' message}
    '''
    if not manager.does_exist(secret_key):
        raise HTTPException(status_code=404, detail=ResponseError.NOT_FOUND.value)

    if not password:
        raise HTTPException(status_code=400, detail=ResponseError.NO_ARGS.value)

    secret, password_true = manager.select(secret_key)
    password_true = crypto.decrypt(password_true)

    if password == password_true:
        manager.delete(secret_key)
        return {'secret': crypto.decrypt(secret)}

    raise HTTPException(status_code=401, detail=ResponseError.WRONG_PASSWORD.value)
