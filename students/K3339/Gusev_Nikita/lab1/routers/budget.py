from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing_extensions import TypedDict

from database.connection import get_session
from models import Budget, BudgetDefault

router = APIRouter(prefix="/budget", tags=["Budget"])


@router.get("/list")
def budgets_list(session=Depends(get_session)) -> List[Budget]:
    return session.exec(select(Budget)).all()


@router.get("/{budget_id}")
def budget_get(budget_id: int, session=Depends(get_session)) -> Budget:
    return session.get(Budget, budget_id)


@router.post("")
def budget_create(
    budget: BudgetDefault, session=Depends(get_session)
) -> TypedDict("Response", {"status": int, "data": Budget}):
    budget = Budget.model_validate(budget)
    session.add(budget)
    session.commit()
    session.refresh(budget)
    return {"status": 200, "data": budget}


@router.delete("/delete{budget_id}")
def budget_delete(budget_id: int, session=Depends(get_session)):
    budget = session.get(Budget, budget_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    session.delete(budget)
    session.commit()
    return {"ok": True}
