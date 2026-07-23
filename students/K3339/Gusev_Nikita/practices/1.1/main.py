from typing import List

from fastapi import FastAPI
from typing_extensions import TypedDict

from models import Transaction, Category, Tag

app = FastAPI()


@app.get("/")
def hello():
    return "Hello, finance app!"


# ---------- Временная БД ----------

temp_bd = [
    {
        "id": 1,
        "amount": 1500.0,
        "description": "Продукты в магазине",
        "category": {
            "id": 1,
            "title": "Еда",
            "type": "expense",
        },
        "tags": [
            {"id": 1, "name": "продукты"},
            {"id": 2, "name": "дом"},
        ],
    },
    {
        "id": 2,
        "amount": 50000.0,
        "description": "Зарплата за месяц",
        "category": {
            "id": 2,
            "title": "Зарплата",
            "type": "income",
        },
        "tags": [],
    },
    {
        "id": 3,
        "amount": 800.0,
        "description": "Такси до работы",
        "category": {
            "id": 3,
            "title": "Транспорт",
            "type": "expense",
        },
        "tags": [{"id": 3, "name": "работа"}],
    },
]


# ---------- CRUD для транзакций ----------

@app.get("/transactions_list")
def transactions_list() -> List[Transaction]:
    return temp_bd


@app.get("/transaction/{transaction_id}")
def transaction_get(transaction_id: int) -> List[Transaction]:
    return [t for t in temp_bd if t.get("id") == transaction_id]


@app.post("/transaction")
def transaction_create(
    transaction: Transaction,
) -> TypedDict("Response", {"status": int, "data": Transaction}):
    transaction_to_append = transaction.model_dump()
    temp_bd.append(transaction_to_append)
    return {"status": 200, "data": transaction}


@app.delete("/transaction/delete{transaction_id}")
def transaction_delete(transaction_id: int):
    for i, t in enumerate(temp_bd):
        if t.get("id") == transaction_id:
            temp_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/transaction{transaction_id}")
def transaction_update(transaction_id: int, transaction: Transaction) -> List[Transaction]:
    for t in temp_bd:
        if t.get("id") == transaction_id:
            transaction_to_append = transaction.model_dump()
            temp_bd.remove(t)
            temp_bd.append(transaction_to_append)
    return temp_bd


# ---------- CRUD для категорий (вложенный одиночный объект) ----------

categories_bd = [
    {"id": 1, "title": "Еда", "type": "expense"},
    {"id": 2, "title": "Зарплата", "type": "income"},
    {"id": 3, "title": "Транспорт", "type": "expense"},
]


@app.get("/categories_list")
def categories_list() -> List[Category]:
    return categories_bd


@app.get("/category/{category_id}")
def category_get(category_id: int) -> List[Category]:
    return [c for c in categories_bd if c.get("id") == category_id]


@app.post("/category")
def category_create(
    category: Category,
) -> TypedDict("Response", {"status": int, "data": Category}):
    category_to_append = category.model_dump()
    categories_bd.append(category_to_append)
    return {"status": 200, "data": category}


@app.delete("/category/delete{category_id}")
def category_delete(category_id: int):
    for i, c in enumerate(categories_bd):
        if c.get("id") == category_id:
            categories_bd.pop(i)
            break
    return {"status": 201, "message": "deleted"}


@app.put("/category{category_id}")
def category_update(category_id: int, category: Category) -> List[Category]:
    for c in categories_bd:
        if c.get("id") == category_id:
            category_to_append = category.model_dump()
            categories_bd.remove(c)
            categories_bd.append(category_to_append)
    return categories_bd