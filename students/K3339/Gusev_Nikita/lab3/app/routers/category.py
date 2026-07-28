from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from database.connection import get_session
from models import Category, CategoryDefault

router = APIRouter(prefix="/category", tags=["Category"])


@router.get("/list")
def categories_list(session=Depends(get_session)) -> List[Category]:
    return session.exec(select(Category)).all()


@router.get("/{category_id}")
def category_get(category_id: int, session=Depends(get_session)) -> Category:
    return session.get(Category, category_id)


@router.post("")
def category_create(
    category: CategoryDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Category}):
    category = Category.model_validate(category)
    session.add(category)
    session.commit()
    session.refresh(category)
    return {"status": 200, "data": category}


@router.delete("/delete{category_id}")
def category_delete(category_id: int, session=Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"ok": True}
