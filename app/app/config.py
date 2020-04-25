import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db.db')
SECRET_KEY = 'topsecretkey' #key length must be less than 24 characters and more than 12
