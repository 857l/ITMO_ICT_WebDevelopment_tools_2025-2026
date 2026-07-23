from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from database.connection import get_session
from models import User, UserDefault

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/list")
def users_list(session=Depends(get_session)) -> List[User]:
    return session.exec(select(User)).all()


@router.get("/{user_id}")
def user_get(user_id: int, session=Depends(get_session)) -> User:
    return session.get(User, user_id)


@router.post("")
def user_create(
    user: UserDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": User}):
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}


@router.delete("/delete{user_id}")
def user_delete(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
