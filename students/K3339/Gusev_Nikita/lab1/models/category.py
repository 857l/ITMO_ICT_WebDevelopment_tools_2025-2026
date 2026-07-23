from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class CategoryType(Enum):
    income = "income"
    expense = "expense"


class CategoryDefault(SQLModel):
    title: str
    type: CategoryType


class Category(CategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")
