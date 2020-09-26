from enum import Enum


class ResponseError(Enum):
    NOT_FOUND = 'Not found. This secret was deleted or never existed'
    NO_ARGS = 'Bad request. No secret and/or password argument in request.'
    WRONG_PASSWORD = 'Wrong password'
