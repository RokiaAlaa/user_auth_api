from ninja import Router
from django.contrib.auth import get_user_model
from .schemas import RegisterSchema, LoginSchema, UserOutSchema, TokenSchema, UserUpdateSchema, RefreshSchema
from .auth import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from ninja.errors import HttpError
from .auth import jwt_auth, admin_jwt_auth
from typing import List

User = get_user_model()
router = Router()

@router.post('/register', response=UserOutSchema)
def register(request, data: RegisterSchema):
    
    exist = User.objects.filter(username=data.username).exists()
    if exist:
        raise HttpError(400, 'username already exists')
    
    exist = User.objects.filter(email=data.email).exists()
    if exist:
        raise HttpError(400, 'email already exists')
    
    hashed_password = hash_password(data.password)
    
    user = User.objects.create(username=data.username, email=data.email, password=hashed_password)
    # user = User.objects.create_user(username=data.username, email=data.email, password=data.password)

    return user

@router.post('/login', response=TokenSchema)
def login(request, data: LoginSchema):
    
    try:
        user = User.objects.get(username=data.username)
    except User.DoesNotExist:
        raise HttpError(401, 'Invalid credentails')
    
    verified = verify_password(data.password, user.password)
    if not verified:
        raise HttpError(401, 'Invalid credentials')
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {'refresh_token': refresh_token, 'access_token':access_token}

@router.get('/me', response=UserOutSchema, auth=jwt_auth)
def get_me(request):
    return request.auth

@router.get('/users/', response=List[UserOutSchema], auth=admin_jwt_auth)
def list_users(request):
    return User.objects.all()

@router.put('/users/{user_id}', response=UserOutSchema, auth=admin_jwt_auth)
def update_user(request, user_id: int, data: UserUpdateSchema):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, 'user not found')
    
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(user, field, value)

    user.save()
    return user
    
@router.delete('/users/{user_id}', auth=admin_jwt_auth)
def delete_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, 'user not found')

    user.delete()

    # return 204
    return {'success': True}

@router.post('/refresh', response=TokenSchema)
def refresh_token(request, data: RefreshSchema):
    try:
        payload = decode_token(data.refresh_token)
    except ValueError:
        raise HttpError(401, 'Invalid refresh token')
    
    if payload['type'] != 'refresh':
        raise HttpError(401, 'Invalid token type')
    
    user_id = int(payload['sub'])

    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)

    return {'access_token':access_token, 'refresh_token':refresh_token}