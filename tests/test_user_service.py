"""Unit tests for user service."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.services.user import UserService
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.models.user import User


@pytest.fixture
async def test_db_session():
    """Create in-memory SQLite test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_user(test_db_session: AsyncSession):
    """Test successful user registration."""
    service = UserService(test_db_session)
    request = UserRegisterRequest(
        email="test@example.com",
        username="testuser",
        password="SecurePass123",
    )
    
    user, tokens = await service.register_user(request)
    
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.token_type == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(test_db_session: AsyncSession):
    """Test registration fails with duplicate email."""
    service = UserService(test_db_session)
    request1 = UserRegisterRequest(
        email="test@example.com",
        username="user1",
        password="SecurePass123",
    )
    request2 = UserRegisterRequest(
        email="test@example.com",
        username="user2",
        password="SecurePass123",
    )
    
    await service.register_user(request1)
    
    with pytest.raises(ValueError, match="already registered"):
        await service.register_user(request2)


@pytest.mark.asyncio
async def test_login_user(test_db_session: AsyncSession):
    """Test successful user login."""
    service = UserService(test_db_session)
    
    # Register first
    register_request = UserRegisterRequest(
        email="test@example.com",
        username="testuser",
        password="SecurePass123",
    )
    await service.register_user(register_request)
    
    # Login
    login_request = UserLoginRequest(
        email="test@example.com",
        password="SecurePass123",
    )
    user, tokens = await service.login_user(login_request)
    
    assert user.email == "test@example.com"
    assert tokens.access_token


@pytest.mark.asyncio
async def test_login_invalid_password(test_db_session: AsyncSession):
    """Test login fails with wrong password."""
    service = UserService(test_db_session)
    
    # Register first
    register_request = UserRegisterRequest(
        email="test@example.com",
        username="testuser",
        password="SecurePass123",
    )
    await service.register_user(register_request)
    
    # Try login with wrong password
    login_request = UserLoginRequest(
        email="test@example.com",
        password="WrongPassword",
    )
    
    with pytest.raises(ValueError, match="Invalid email or password"):
        await service.login_user(login_request)
