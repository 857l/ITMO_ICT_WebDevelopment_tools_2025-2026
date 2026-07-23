from datetime import datetime, date as date_type
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from models.links import TransactionTagLink
from models.category import CategoryDefault
from models.tag import TagDefault


class TransactionDefault(SQLModel):
    amount: float
    description: str
    date: date_type = Field(default_factory=lambda: datetime.utcnow().date())
    account_id: Optional[int] = Field(default=None, foreign_key="account.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Transaction(TransactionDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    account: Optional["Account"] = Relationship(back_populates="transactions")
    category: Optional["Category"] = Relationship(back_populates="transactions")
    tags: List["Tag"] = Relationship(
        back_populates="transactions", link_model=TransactionTagLink
    )


# ---------- Модели для вложенного отображения в ответах API ----------

class TransactionWithCategory(TransactionDefault):
    category: Optional[CategoryDefault] = None


class TransactionWithTags(TransactionDefault):
    tags: List[TagDefault] = []
