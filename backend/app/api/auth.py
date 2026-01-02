"""Authentication API endpoints."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

from app.models.user import Token, User, UserCreate, UserInDB, RefreshTokenRequest
from app.core.security import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_current_active_user
)
from app.core.config import settings
from app.db.mongodb import MongoDB

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login.
    Get an access token for future requests.
    """
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.jwt_refresh_token_expire_days)
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=refresh_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    Returns a new access token if the refresh token is valid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode and validate refresh token
        payload = jwt.decode(
            refresh_request.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Verify it's a refresh token
        if username is None or token_type != "refresh":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Verify user still exists and is active
    db = MongoDB.get_db()
    users_collection = db.users
    user_data = await users_collection.find_one({"username": username})
    
    if user_data is None:
        raise credentials_exception
    
    user = UserInDB(**user_data)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    Note: In production, you may want to restrict this endpoint.
    """
    db = MongoDB.get_db()
    users_collection = db.users
    
    # Check if username already exists
    existing_user = await users_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists (if provided)
    if user_data.email:
        existing_email = await users_collection.find_one({"email": user_data.email})
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    user_in_db = UserInDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    
    user_dict = user_in_db.model_dump(exclude={"hashed_password"})
    user_dict["hashed_password"] = user_in_db.hashed_password
    
    await users_collection.insert_one(user_dict)
    
    return User(**user_dict)


@router.get("/me", response_model=User)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information."""
    return User(**current_user.model_dump())
