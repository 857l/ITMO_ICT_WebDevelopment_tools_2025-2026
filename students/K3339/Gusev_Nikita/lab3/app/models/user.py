from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class UserDefault(SQLModel):
    """Публичные поля пользователя — без пароля."""
    email: str
    name: str


class User(UserDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    accounts: List["Account"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")


class UserRegister(SQLModel):
    """Схема для регистрации — принимает сырой пароль."""
    email: str
    name: str
    password: str


class UserLogin(SQLModel):
    email: str
    password: str


class UserUpdate(SQLModel):
    """Схема для обновления собственных данных пользователем."""
    name: Optional[str] = None
    password: Optional[str] = None
