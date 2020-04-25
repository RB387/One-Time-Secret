import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #path to current folder

LIFE_TIME_HOURS = 168 #life time of secrets. After this time they can't be accessed. 7 days by default
DB_PATH = os.path.join(BASE_DIR, 'db.db') #path to database
SECRET_KEY = 'topsecretkey' #key to encrypt and decrypt data. length must be less than 24 characters and more than 12
