import os
class config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave-secreta-de-prueba"
