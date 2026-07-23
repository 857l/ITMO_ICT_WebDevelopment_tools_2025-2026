from datetime import date as date_type
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class BudgetDefault(SQLModel):
    limit_amount: float
    period_start: date_type
    period_end: date_type
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Budget(BudgetDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    user: Optional["User"] = Relationship(back_populates="budgets")
    category: Optional["Category"] = Relationship(back_populates="budgets")
