from sqlalchemy import Column, Integer, String, Boolean
from database import Base
from sqlalchemy.orm import relationship
from documents.models import Document


class User(Base):
    """
    User model that represents a user in the application.

    This model defines the structure of the "users" table in the database, with fields for
    the user's personal information, authentication, and roles. The table contains the following columns:

    - id: The unique identifier for the user (Primary Key).
    - email: The email address of the user (unique and indexed).
    - first_name: The first name of the user (nullable).
    - last_name: The last name of the user (nullable).
    - password: The hashed password of the user (cannot be null).
    - is_admin: A flag indicating if the user is an admin (default is False).

    Attributes:
    id (int): The unique ID of the user.
    email (str): The email of the user.
    first_name (str): The first name of the user.
    last_name (str): The last name of the user.
    password (str): The password of the user.
    is_admin (bool): Flag to indicate if the user has admin privileges.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True, default='')
    last_name = Column(String, nullable=True, default='')
    password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

    documents = relationship("Document", back_populates="uploaded_by")
