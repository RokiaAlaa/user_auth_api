import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model

User = get_user_model()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def _create_token(user_id: int, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.utcnow() + expires_delta
    payload = {'sub': str(user_id), 'exp': expire, 'type': token_type}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(user_id: int) -> str:
    return _create_token(user_id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), token_type='access')

def create_refresh_token(user_id: int) -> str:
    return _create_token(user_id, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), token_type='refresh')


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError('Invalid or expired token')
    
class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = decode_token(token)
        except ValueError:
            return None
        else:
            if payload['type'] != 'access':
                return None
            
        user_id = int(payload['sub'])

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
        
        return user

jwt_auth = JWTAuth()

class AdminJWTAuth(JWTAuth):
    def authenticate(self, request, token):
        user = super().authenticate(request, token)

        if not user or not user.is_superuser:
            return None

        return user
        
admin_jwt_auth = AdminJWTAuth()