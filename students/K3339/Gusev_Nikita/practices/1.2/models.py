from enum import Enum
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class CategoryType(Enum):
    income = "income"
    expense = "expense"


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None, foreign_key="transaction.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
    # доп. поле ассоциативной сущности (не просто ссылки на связанные таблицы)
    note: Optional[str] = ""


class CategoryDefault(SQLModel):
    title: str
    type: CategoryType


class Category(CategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="category")



class TagDefault(SQLModel):
    name: str


class Tag(TagDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(
        back_populates="tags", link_model=TransactionTagLink
    )


class TransactionDefault(SQLModel):
    amount: float
    description: str
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Transaction(TransactionDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    category: Optional[Category] = Relationship(back_populates="transactions")
    tags: List[Tag] = Relationship(
        back_populates="transactions", link_model=TransactionTagLink
    )


class TransactionWithCategory(TransactionDefault):
    category: Optional[CategoryDefault] = None



class TransactionWithTags(TransactionDefault):
    tags: List[TagDefault] = []