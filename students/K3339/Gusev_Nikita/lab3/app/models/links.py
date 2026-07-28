from typing import Optional

from sqlmodel import SQLModel, Field


class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None, foreign_key="transaction.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
    # доп. поле ассоциативной сущности
    note: Optional[str] = ""
