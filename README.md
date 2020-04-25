# One-Time-Secret

API service for one time secrets

## Example:
```
>>>response = client.get('/generate/?secret=TEXT-MESSAGE&password=PASS')
>>>print(response.json())
{'secret-key': f60a0191-ce68-44dd-b741-04543b97cdef}
```
```
>>>secret_key = '/secrets/f60a0191-ce68-44dd-b741-04543b97cdef/'
>>>response = client.get(secret_key)
>>>print(response.json())
{'secret': 'TEXT-MESSAGE'}

>>>no_response = client.get(secret_key)
>>>print(no_response.status_code)
404
```

## Install
```
docker-compose up
```
Runs on '0.0.0.0:8000' by default
