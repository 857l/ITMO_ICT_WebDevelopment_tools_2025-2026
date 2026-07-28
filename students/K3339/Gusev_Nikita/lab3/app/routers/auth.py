from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing_extensions import TypedDict

from database.connection import get_session
from core.security import hash_password, verify_password, create_access_token
from core.dependencies import get_current_user
from models import User, UserRegister, UserLogin, UserDefault, UserUpdate

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(
    data: UserRegister, session: Session = Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": UserDefault}):
    existing = session.exec(select(User).where(User.email == data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        name=data.name,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": 200, "data": user}


@router.post("/login")
def login(
    data: UserLogin, session: Session = Depends(get_session)
) -> TypedDict("Response", {"access_token": str, "token_type": str}):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)) -> UserDefault:
    return current_user


@router.patch("/me")
def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserDefault:
    if data.name is not None:
        current_user.name = data.name
    if data.password is not None:
        current_user.hashed_password = hash_password(data.password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
