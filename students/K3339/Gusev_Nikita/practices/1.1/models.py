from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class CategoryType(Enum):
    income = "income"
    expense = "expense"


class Category(BaseModel):
    id: int
    title: str
    type: CategoryType


class Tag(BaseModel):
    id: int
    name: str


class Transaction(BaseModel):
    id: int
    amount: float
    description: str
    category: Category
    tags: Optional[List[Tag]] = []