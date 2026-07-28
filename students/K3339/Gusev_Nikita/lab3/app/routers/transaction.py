from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from database.connection import get_session
from models import (
    Transaction,
    TransactionDefault,
    TransactionWithCategory,
    TransactionWithTags,
    Tag,
    TransactionTagLink,
)

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.get("/list")
def transactions_list(session=Depends(get_session)) -> List[Transaction]:
    return session.exec(select(Transaction)).all()


@router.get("/{transaction_id}", response_model=TransactionWithCategory)
def transaction_get(transaction_id: int, session=Depends(get_session)) -> Transaction:
    return session.get(Transaction, transaction_id)


@router.get("/{transaction_id}/with_tags", response_model=TransactionWithTags)
def transaction_get_with_tags(transaction_id: int, session=Depends(get_session)) -> Transaction:
    return session.get(Transaction, transaction_id)


@router.post("")
def transaction_create(
    transaction: TransactionDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Transaction}):
    transaction = Transaction.model_validate(transaction)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return {"status": 200, "data": transaction}


@router.patch("/{transaction_id}")
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


@router.delete("/delete{transaction_id}")
def transaction_delete(transaction_id: int, session=Depends(get_session)):
    transaction = session.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    session.delete(transaction)
    session.commit()
    return {"ok": True}


# ---------- Привязка тега к транзакции (many-to-many с доп. полем note) ----------

@router.post("/{transaction_id}/tag/{tag_id}")
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
