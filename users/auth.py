from datetime import datetime, timedelta
from users.permissions import oso
import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from users.models import User
from database import get_db
from config import settings

# Secret key, algorithm, and expiration time for JWT tokens
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer for extracting the token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def check_permission(user: User, action: str, resource):
    """
    Checks if a user has permission to perform an action on a resource using the Oso policy engine.

    Args:
        user (User): The user performing the action.
        action (str): The action the user is attempting to perform.
        resource: The resource the action is being performed on.

    Raises:
        HTTPException: If the user is not allowed to perform the action, a 403 Forbidden error is raised.
    """
    if not oso.is_allowed(user, action, resource):
        raise HTTPException(status_code=403, detail="Permission denied")


async def verify_password(plain_password, password):
    """
    Verifies if the provided plain password matches the hashed password.

    Args:
        plain_password (str): The plain password entered by the user.
        password (str): The hashed password stored in the database.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, password)


async def authenticate_user(db: AsyncSession, email: str, password: str):
    """
    Authenticates a user by verifying the email and password.

    Args:
        db (AsyncSession): The database session to execute the query.
        email (str): The email address of the user.
        password (str): The password provided by the user.

    Returns:
        User or None: The authenticated user if successful, or None if authentication fails.
    """
    # Execute the query asynchronously
    result = await db.execute(select(User).filter(User.email == email))

    # Retrieve the user asynchronously
    user = result.scalar_one_or_none()  # This will await the result

    # Verify the password asynchronously
    if not user or not await verify_password(password, user.password):
        return None

    return user


async def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Creates a JWT access token with the provided data and expiration time.

    Args:
        data (dict): The data to include in the JWT payload.
        expires_delta (timedelta, optional): The expiration time for the token. Defaults to None, which uses the default expiration time.

    Returns:
        str: The generated JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    to_encode["sub"] = str(to_encode["sub"])
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user from the database based on the provided JWT token.

    Args:
        db (AsyncSession): The database session to query the user.
        token (str): The JWT token provided in the request.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid or expired, or if the user cannot be found.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
