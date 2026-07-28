from __future__ import annotations
import os
from typing import Optional

from sqlmodel import SQLModel, Field, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL", "postgresql://postgres:postgres@localhost:5432/lab_db")
if DB_URL and DB_URL.startswith("postgresql://"):
    DB_URL = DB_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DB_URL)


class ScrapedPage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field()
    title: str = Field()
    approach: str = Field(default="async")  # 'threading' | 'multiprocessing' | 'async'


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    return Session(engine)
