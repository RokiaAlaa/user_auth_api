from ninja import Router
from django.contrib.auth import get_user_model
from .schemas import RegisterSchema, LoginSchema, UserOutSchema, TokenSchema
from .auth import hash_password, verify_password, create_access_token, create_refresh_token
from ninja.errors import HttpError
from .auth import jwt_auth

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
