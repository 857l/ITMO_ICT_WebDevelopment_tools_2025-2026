from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class AccountDefault(SQLModel):
    name: str
    balance: float = 0.0
    currency: str = "RUB"
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Account(AccountDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    user: Optional["User"] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")
