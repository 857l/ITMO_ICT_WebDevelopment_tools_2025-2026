from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import select
from typing_extensions import TypedDict

from database.connection import get_session
from models import Tag, TagDefault

router = APIRouter(prefix="/tag", tags=["Tag"])


@router.get("/list")
def tags_list(session=Depends(get_session)) -> List[Tag]:
    return session.exec(select(Tag)).all()


@router.post("")
def tag_create(
    tag: TagDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Tag}):
    tag = Tag.model_validate(tag)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return {"status": 200, "data": tag}
