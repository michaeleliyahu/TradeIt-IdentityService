"""User service containing business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.usreRepository import UserRepository
from app.core.security import PasswordUtil, TokenUtil
from app.schemas.user import UserRegisterRequest, UserLoginRequest, TokenResponse
from app.models.user import User
from typing import Optional, Tuple
import uuid


class UserService:
    """Service for user-related business logic."""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session."""
        self.repository = UserRepository(session)

    async def register_user(self, request: UserRegisterRequest) -> Tuple[User, TokenResponse]:
        """
        Register a new user and return user + tokens.
        
        Flow:
        1. Check if email/username exists
        2. Hash password
        3. Create user in database
        4. Generate access & refresh tokens
        5. Return user and tokens
        """
        # Check if user already exists
        if await self.repository.user_exists_by_email(request.email):
            raise ValueError(f"Email {request.email} already registered")
        
        if await self.repository.user_exists_by_username(request.username):
            raise ValueError(f"Username {request.username} already taken")

        # Hash password
        hashed_password = PasswordUtil.hash_password(request.password)

        # Create user in database
        user = await self.repository.create_user(
            email=request.email,
            username=request.username,
            hashed_password=hashed_password,
        )

        # Generate tokens
        tokens = self._generate_tokens(user.id)

        return user, tokens

    async def login_user(self, request: UserLoginRequest) -> Tuple[User, TokenResponse]:
        """
        Authenticate user and return tokens.
        
        Flow:
        1. Find user by email
        2. Verify password
        3. Generate access & refresh tokens
        4. Return user and tokens
        """
        # Find user by email
        user = await self.repository.get_user_by_email(request.email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not PasswordUtil.verify_password(request.password, user.hashed_password):
            raise ValueError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is inactive")

        # Generate tokens
        tokens = self._generate_tokens(user.id)

        return user, tokens

    async def get_user_details(self, user_id: int) -> Optional[User]:
        """Retrieve user details by ID."""
        return await self.repository.get_user_by_id(user_id)

    def _generate_tokens(self, user_id: int) -> TokenResponse:
        """Generate access and refresh tokens."""
        access_token = TokenUtil.create_access_token(str(user_id))
        refresh_token = TokenUtil.create_refresh_token(str(user_id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=15 * 60,  # 15 minutes in seconds
        )