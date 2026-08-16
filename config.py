import os
Class config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave-secreta-de-prueba"
