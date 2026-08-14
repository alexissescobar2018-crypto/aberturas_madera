import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-aberturas'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///aberturas.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False