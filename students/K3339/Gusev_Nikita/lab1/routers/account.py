from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from database.connection import get_session
from models import Account, AccountDefault

router = APIRouter(prefix="/account", tags=["Account"])


@router.get("/list")
def accounts_list(session=Depends(get_session)) -> List[Account]:
    return session.exec(select(Account)).all()


@router.get("/{account_id}")
def account_get(account_id: int, session=Depends(get_session)) -> Account:
    return session.get(Account, account_id)


@router.post("")
def account_create(
    account: AccountDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Account}):
    account = Account.model_validate(account)
    session.add(account)
    session.commit()
    session.refresh(account)
    return {"status": 200, "data": account}


@router.delete("/delete{account_id}")
def account_delete(account_id: int, session=Depends(get_session)):
    account = session.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    session.delete(account)
    session.commit()
    return {"ok": True}
