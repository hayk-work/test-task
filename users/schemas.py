from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """
    Pydantic model for user registration data.

    This model validates the data required to register a new user, including:
    - email: The email address of the user.
    - password: The password for the user.
    """
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """
    Pydantic model for user creation data.

    This model validates the data required to create a new user, including:
    - email: The email address of the user.
    - first_name: The user's first name.
    - last_name: The user's last name.
    - password: The password for the user.
    """
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserUpdate(BaseModel):
    """
    Pydantic model for updating existing user data.

    This model validates the data required to update a user's profile, including:
    - email: The updated email address of the user.
    - first_name: The updated first name of the user.
    - last_name: The updated last name of the user.
    """
    email: EmailStr
    first_name: str
    last_name: str


class UserResponse(BaseModel):
    """
    Pydantic model for the response when retrieving user data.

    This model defines the structure of the user data returned in API responses, including:
    - id: The user's unique identifier.
    - email: The email address of the user.
    - first_name: The user's first name.
    - last_name: The user's last name.

    The `Config` class specifies that this model can be created from ORM attributes.
    """
    id: int
    email: EmailStr
    first_name: str
    last_name: str

    class Config:
        from_attributes = True
