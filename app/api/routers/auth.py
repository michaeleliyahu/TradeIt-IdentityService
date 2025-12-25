"""Authentication router for user registration and login."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.user import UserService
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.core.security import TokenUtil
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    **Registration Flow:**
    1. Validate email and username uniqueness
    2. Hash password securely using bcrypt
    3. Create user record in database
    4. Generate JWT access and refresh tokens
    5. Return tokens to client
    """
    try:
        service = UserService(session)
        user, tokens = await service.register_user(request)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and issue tokens.
    
    **Login Flow:**
    1. Find user by email in database
    2. Verify password against hashed password
    3. Check if user account is active
    4. Generate JWT access and refresh tokens
    5. Return tokens for authenticated requests
    """
    try:
        service = UserService(session)
        user, tokens = await service.login_user(request)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Fetch user details by user ID.
    
    **Note:** In production, add JWT verification middleware to ensure
    only authorized users can access user details.
    """
    service = UserService(session)
    user = await service.get_user_details(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user
