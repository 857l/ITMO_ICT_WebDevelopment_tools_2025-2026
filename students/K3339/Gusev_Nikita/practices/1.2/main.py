from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from connection import init_db, get_session
from models import (
    Transaction, TransactionDefault, TransactionWithCategory, TransactionWithTags,
    Category, CategoryDefault,
    Tag, TagDefault,
    TransactionTagLink,
)

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def hello():
    return "Hello, finance app!"


# ---------- CRUD: Transaction ----------

@app.get("/transactions_list")
def transactions_list(session=Depends(get_session)) -> List[Transaction]:
    return session.exec(select(Transaction)).all()


@app.get("/transaction/{transaction_id}", response_model=TransactionWithCategory)
def transaction_get(transaction_id: int, session=Depends(get_session)) -> Transaction:
    return session.get(Transaction, transaction_id)


@app.post("/transaction")
def transaction_create(
    transaction: TransactionDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Transaction}):
    transaction = Transaction.model_validate(transaction)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return {"status": 200, "data": transaction}


@app.patch("/transaction{transaction_id}")
def transaction_update(
    transaction_id: int, transaction: TransactionDefault, session=Depends(get_session)
) -> TransactionDefault:
    db_transaction = session.get(Transaction, transaction_id)
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    transaction_data = transaction.model_dump(exclude_unset=True)
    for key, value in transaction_data.items():
        setattr(db_transaction, key, value)
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@app.delete("/transaction/delete{transaction_id}")
def transaction_delete(transaction_id: int, session=Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}


# ---------- CRUD: Category (one-to-many с Transaction) ----------

@app.get("/categories_list")
def categories_list(session=Depends(get_session)) -> List[Category]:
    return session.exec(select(Category)).all()


@app.get("/category/{category_id}")
def category_get(category_id: int, session=Depends(get_session)) -> Category:
    return session.get(Category, category_id)


@app.post("/category")
def category_create(
    category: CategoryDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Category}):
    category = Category.model_validate(category)
    session.add(category)
    session.commit()
    session.refresh(category)
    return {"status": 200, "data": category}


@app.delete("/category/delete{category_id}")
def category_delete(category_id: int, session=Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}


# ---------- CRUD: Tag (many-to-many с Transaction) ----------

@app.get("/tags_list")
def tags_list(session=Depends(get_session)) -> List[Tag]:
    return session.exec(select(Tag)).all()


@app.post("/tag")
def tag_create(
    tag: TagDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Tag}):
    tag = Tag.model_validate(tag)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return {"status": 200, "data": tag}


# ---------- Привязка тега к транзакции (many-to-many с доп. полем note) ----------

@app.post("/transaction/{transaction_id}/tag/{tag_id}")
def add_tag_to_transaction(
    transaction_id: int, tag_id: int, note: str = "", session=Depends(get_session)
):
    transaction = session.get(Transaction, transaction_id)
    tag = session.get(Tag, tag_id)
    if not transaction or not tag:
        raise HTTPException(status_code=404, detail="Transaction or Tag not found")
    link = TransactionTagLink(transaction_id=transaction_id, tag_id=tag_id, note=note)
    session.add(link)
    session.commit()
    return {"ok": True}


# ---------- Получение транзакции со вложенным списком тегов (many-to-many) ----------

@app.get("/transaction/{transaction_id}/with_tags", response_model=TransactionWithTags)
def transaction_get_with_tags(transaction_id: int, session=Depends(get_session)) -> Transaction:
    return session.get(Transaction, transaction_id)