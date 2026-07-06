import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

@pytest.fixture
def db():
    """Provide a test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def auth_token():
    """Provide a valid JWT token for testing."""
    from app.security import create_access_token
    return create_access_token(data={"sub": "test-user-id"})
