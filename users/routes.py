from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db

from users.auth import authenticate_user, create_access_token, get_current_user, check_permission
from users import crud, schemas
from users.schemas import UserResponse
from users.models import User

router = APIRouter()


@router.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserRegister, db: AsyncSession = Depends(get_db)):
    """
    Register a new user. If the email is already registered, returns an error.

    Args:
    - user: User registration data including email, password, etc.
    - db: The database session dependency.

    Returns:
    - The created user data in the response model.
    """
    new_user = await crud.register_user(db, user)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return new_user


@router.post("/token")
async def login(db: AsyncSession = Depends(get_db), email: str = Form(...), password: str = Form(...)):
    """
    Authenticate a user and generate a JWT token for them.

    Args:
    - db: The database session dependency.
    - email: The user's email address.
    - password: The user's password.

    Returns:
    - A dictionary containing the access token and its type.

    Raises:
    - HTTPException: If the email or password is incorrect.
    """
    user = await authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = await create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.put("/set-admin/{user_id}")
async def set_admin(user_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Assign admin role to a user. Only an admin user can perform this action.

    Args:
    - user_id: The ID of the user to be assigned admin role.
    - db: The database session dependency.
    - current_user: The user making the request, retrieved from the token.

    Returns:
    - A success message if the operation is successful.

    Raises:
    - HTTPException: If the user is not found or the current user does not have permission.
    """
    await check_permission(current_user, "manage_roles", None)
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = True
    await db.commit()
    await db.refresh(user)
    return {"message": f"User {user_id} is now an admin"}


@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.

    Args:
    - current_user: The user making the request, retrieved from the token.

    Returns:
    - The current user's profile data.

    Raises:
    - HTTPException: If the user does not have permission to view the profile.
    """
    await check_permission(current_user, "view_profile", current_user)
    return current_user


@router.get("/get_users", response_model=List[schemas.UserResponse])
async def get_users(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get a list of all users. Only an admin can view all users.

    Args:
    - db: The database session dependency.
    - current_user: The user making the request, retrieved from the token.

    Returns:
    - A list of all users.

    Raises:
    - HTTPException: If the current user does not have permission to view all users.
    """
    await check_permission(current_user, "view_all_users", None)
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.post("/create", response_model=schemas.UserResponse)
async def create_user(
        user: schemas.UserCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Create a new user. Only authorized users can create new users.

    Args:
    - user: User creation data including email, password, etc.
    - db: The database session dependency.
    - current_user: The user making the request, retrieved from the token.

    Returns:
    - The created user's data.

    Raises:
    - HTTPException: If the user does not have permission to create a new user.
    """
    await check_permission(current_user, "create_user", user)
    db_user = await crud.create_user(db, user)
    return db_user


@router.put("/update", response_model=schemas.UserResponse)
async def update_user(
        user: schemas.UserUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    Update the profile of the currently authenticated user.

    Args:
    - user: The updated user data.
    - db: The database session dependency.
    - current_user: The user making the request, retrieved from the token.

    Returns:
    - The updated user's data.

    Raises:
    - HTTPException: If the user does not have permission to update the profile or if the user is not found.
    """
    await check_permission(current_user, "update_profile", current_user)
    user = await crud.update_user(db, current_user.id, user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/delete")
async def delete_user(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Delete the currently authenticated user's account.

    Args:
    - db: The database session dependency.
    - current_user: The user making the request, retrieved from the token.

    Returns:
    - A success message indicating that the user was deleted.

    Raises:
    - HTTPException: If the user does not exist or does not have permission to delete the account.
    """
    user = await db.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await check_permission(current_user, "delete_user", user)
    await db.delete(user)
    await db.commit()
    return {"message": f"User {current_user.id} deleted"}
