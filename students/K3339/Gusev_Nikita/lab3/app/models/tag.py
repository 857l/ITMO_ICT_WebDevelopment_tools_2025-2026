from typing import List

from sqlmodel import SQLModel, Field, Relationship

from models.links import TransactionTagLink


class TagDefault(SQLModel):
    name: str


class Tag(TagDefault, table=True):
    id: int = Field(default=None, primary_key=True)

    transactions: List["Transaction"] = Relationship(
        back_populates="tags", link_model=TransactionTagLink
    )
