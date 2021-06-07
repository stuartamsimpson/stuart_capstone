import json, os
from flask import request, _request_ctx_stack, abort, session
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN')
ALGORITHMS = os.environ.get('ALGORITHMS')
API_AUDIENCE = os.environ.get('AUTH0_AUDIENCE')

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth_header = request.headers.get('Authorization', None)
    if not auth_header:
        raise AuthError({
            'success': False,
            'message': 'authorization_header_missing',
            'error': 401
        }, 401)

    bearer_token_array = auth_header.split()
    if bearer_token_array[0].lower() != 'bearer' or len(bearer_token_array) == 1 or len(bearer_token_array) > 2:
        raise AuthError({
            'success': False,
            'message': 'invalid_header',
            'error': 401
        }, 401)

    token = bearer_token_array[1]
    return token

# def check_permissions(permission, payload):
#     if "permissions" in payload:
#         if permission in payload['permissions']:
#             return True
#     raise AuthError({
#         'success': False,
#         'message': 'Permission not found in JWT',
#         'error': 401
#     }, 401)

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
                'success': False,
                'message': 'Permission header missing',
                'error': 400
            }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
                'success': False,
                'message': 'Permission not found in JWT',
                'error': 401
            }, 401)
    return True

def verify_decode_jwt(token):
    jsonurl = urlopen(f'http://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'success': False,
            'message': 'Authorization malformed',
            'error': 401,
        }, 401)
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'success': False,
                'message': 'Token expired',
                'error': 401,
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'success': False,
                'message': 'Incorrect claims. Please, check the audience and issuer',
                'error': 401,
            }, 401)
        except Exception:
            raise AuthError({
                'success': False,
                'message': 'Unable to parse authentication token',
                'error': 400,
            }, 400)
    raise AuthError({
        'success': False,
        'message': 'Unable to find the appropriate key',
        'error': 400,
    }, 400)

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            #print('requires_auth',flush=True)
            token = None
            if session and session['token']:
                token = session['token']
            else:
                token = get_token_auth_header()
            if token is None:
                abort(400)
            payload = verify_decode_jwt(token)
            #print('Payload is: {}'.format(payload),flush=True)
            #print(f'testing for permission: {permission}',flush=True)
            if check_permissions(permission, payload):
                print('Permission is in permissions!',flush=True)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator