from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from users.models import User
from users.schemas import UserCreate, UserRegister, UserUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def register_user(db: AsyncSession, user: UserRegister):
    """
    Register a new user in the database. If the email already exists, returns None.

    Args:
    - db: The database session dependency.
    - user: User registration data including email and password.

    Returns:
    - The created user if the email is not already registered.
    - None if the email is already registered.
    """
    existing_user = await db.execute(select(User).filter(User.email == user.email))
    if existing_user.scalar_one_or_none():
        return None  # Email already exists

    password = pwd_context.hash(user.password)
    db_user = User(email=user.email, password=password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def create_user(db: AsyncSession, user: UserCreate):
    """
    Create a new user in the database.

    Args:
    - db: The database session dependency.
    - user: User creation data including first name, last name, email, and password.

    Returns:
    - The created user.
    """
    password = pwd_context.hash(user.password)
    db_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name, password=password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: int):
    """
    Retrieve a user from the database by their user ID.

    Args:
    - db: The database session dependency.
    - user_id: The ID of the user to be retrieved.

    Returns:
    - The user if found.
    - None if no user is found with the given ID.
    """
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user_id: int, updated_user: UserUpdate):
    """
    Update an existing user's details in the database.

    Args:
    - db: The database session dependency.
    - user_id: The ID of the user to be updated.
    - updated_user: The new user data (first name, last name, and email).

    Returns:
    - The updated user if found and updated.
    - None if the user was not found.
    """
    user = await get_user(db, user_id)
    if user:
        user.first_name = updated_user.first_name
        user.last_name = updated_user.last_name
        user.email = updated_user.email
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int):
    """
    Delete a user from the database by their user ID.

    Args:
    - db: The database session dependency.
    - user_id: The ID of the user to be deleted.

    Returns:
    - The deleted user if found and removed.
    - None if no user was found to delete.
    """
    user = await get_user(db, user_id)
    if user:
        await db.delete(user)
        await db.commit()
    return user
