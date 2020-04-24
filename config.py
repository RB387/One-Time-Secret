from os import getcwd, path

DB_PATH = path.join(getcwd(), 'db.db')
SECRET_KEY = 'topsecretkey' #key length must be less than 24 characters and more than 12
