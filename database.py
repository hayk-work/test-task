from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings


# Create an asynchronous SQLAlchemy engine for database connections
engine = create_async_engine(settings.DATABASE_URL, echo=True, future=True)

# Define a session factory for asynchronous database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db():
    """
    Dependency function to get the database session.

    This function provides a session for interacting with the database. It ensures that the session
    is properly opened and closed, and it's used as a dependency in FastAPI routes to access the database.

    Yields:
        AsyncSession: The database session that is used to interact with the database.
    """
    async with SessionLocal() as session:
        yield session
