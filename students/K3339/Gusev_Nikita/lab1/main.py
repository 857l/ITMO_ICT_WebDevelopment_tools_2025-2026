from fastapi import FastAPI

from database.connection import init_db
from routers import category, tag, user, account, budget, transaction, auth

app = FastAPI(title="Personal Finance Service")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def hello():
    return "Hello, finance app!"


app.include_router(auth.router)
app.include_router(category.router)
app.include_router(tag.router)
app.include_router(user.router)
app.include_router(account.router)
app.include_router(budget.router)
app.include_router(transaction.router)
