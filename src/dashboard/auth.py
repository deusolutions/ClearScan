from functools import wraps
from flask import request, Response
import os

# Dummy user credentials for HTTP Basic Auth
USERNAME = os.getenv('DASHBOARD_USERNAME', 'admin')
PASSWORD = os.getenv('DASHBOARD_PASSWORD', 'password')

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated