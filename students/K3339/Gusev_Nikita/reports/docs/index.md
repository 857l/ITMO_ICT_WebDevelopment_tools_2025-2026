# Лабораторная работа 1. Сервис для управления личными финансами на FastAPI

**Студент:** Гусев Никита
**Группа:** K3339
**Тема:** Разработка сервиса для управления личными финансами

## Описание

Реализовано серверное приложение на FastAPI для учёта личных доходов и расходов. Приложение позволяет:

- Регистрироваться и авторизовываться по JWT
- Заводить несколько счетов (наличные, карты и т.д.)
- Категоризировать транзакции (доход/расход)
- Помечать транзакции тегами
- Планировать бюджет по категориям на период

## Ссылки на практики
https://github.com/857l/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/Lab1/students/K3339/Gusev_Nikita/practices/1.1
- [Практика 1.1 — Базовое приложение на FastAPI](https://github.com/857l/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/Lab1/students/K3339/Gusev_Nikita/practices/1.1)
- [Практика 1.2 — SQLModel + PostgreSQL](https://github.com/857l/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/Lab1/students/K3339/Gusev_Nikita/practices/1.2)
- [Практика 1.3 — Alembic + .env + .gitignore](https://github.com/857l/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/Lab1/students/K3339/Gusev_Nikita/practices/1.3)
- [Финальный код лабораторной (lab1)](https://github.com/857l/ITMO_ICT_WebDevelopment_tools_2025-2026/tree/Lab1/students/K3339/Gusev_Nikita/lab1)

---

## Модель данных

Реализовано **7 таблиц**:

| Таблица | Описание |
|---|---|
| `User` | Пользователи системы |
| `Account` | Счета пользователя (наличные, карты и т.д.) |
| `Category` | Категории доходов/расходов |
| `Transaction` | Транзакции (доходы/расходы) |
| `Budget` | Плановый бюджет по категории на период |
| `Tag` | Метки для транзакций |
| `TransactionTagLink` | Связь many-to-many между Transaction и Tag (с доп. полем `note`) |

### Связи

- **One-to-many:** User → Account (у пользователя несколько счетов)
- **One-to-many:** User → Budget (у пользователя несколько бюджетов)
- **One-to-many:** Account → Transaction (у счёта много транзакций)
- **One-to-many:** Category → Transaction (у категории много транзакций)
- **One-to-many:** Category → Budget (у категории может быть бюджет)
- **Many-to-many:** Transaction ↔ Tag (через `TransactionTagLink`)

### Ассоциативная сущность

`TransactionTagLink` содержит дополнительное поле `note` — комментарий к тому, почему тег присвоен именно этой транзакции.

---

## Модели (SQLModel)

### User

```python
class UserDefault(SQLModel):
    email: str
    name: str


class User(UserDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    accounts: List["Account"] = Relationship(back_populates="user")
    budgets: List["Budget"] = Relationship(back_populates="user")
```

### Account

```python
class AccountDefault(SQLModel):
    name: str
    balance: float = 0.0
    currency: str = "RUB"
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")


class Account(AccountDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: Optional["User"] = Relationship(back_populates="accounts")
    transactions: List["Transaction"] = Relationship(back_populates="account")
```

### Category

```python
class CategoryType(Enum):
    income = "income"
    expense = "expense"


class CategoryDefault(SQLModel):
    title: str
    type: CategoryType


class Category(CategoryDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(back_populates="category")
    budgets: List["Budget"] = Relationship(back_populates="category")
```

### Tag

```python
class TagDefault(SQLModel):
    name: str


class Tag(TagDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    transactions: List["Transaction"] = Relationship(
        back_populates="tags", link_model=TransactionTagLink
    )
```

### TransactionTagLink (ассоциативная таблица)

```python
class TransactionTagLink(SQLModel, table=True):
    transaction_id: Optional[int] = Field(
        default=None, foreign_key="transaction.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tag.id", primary_key=True
    )
    note: Optional[str] = ""
```

### Transaction

```python
class TransactionDefault(SQLModel):
    amount: float
    description: str
    date: date_type = Field(default_factory=lambda: datetime.utcnow().date())
    account_id: Optional[int] = Field(default=None, foreign_key="account.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Transaction(TransactionDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    account: Optional["Account"] = Relationship(back_populates="transactions")
    category: Optional["Category"] = Relationship(back_populates="transactions")
    tags: List["Tag"] = Relationship(
        back_populates="transactions", link_model=TransactionTagLink
    )


# Модели для вложенного отображения в ответах API
class TransactionWithCategory(TransactionDefault):
    category: Optional[CategoryDefault] = None


class TransactionWithTags(TransactionDefault):
    tags: List[TagDefault] = []
```

### Budget

```python
class BudgetDefault(SQLModel):
    limit_amount: float
    period_start: date_type
    period_end: date_type
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")


class Budget(BudgetDefault, table=True):
    id: int = Field(default=None, primary_key=True)
    user: Optional["User"] = Relationship(back_populates="budgets")
    category: Optional["Category"] = Relationship(back_populates="budgets")
```

---

## Подключение к БД

`database/connection.py`:

```python
from sqlmodel import SQLModel, Session, create_engine
from core.config import DB_URL

engine = create_engine(DB_URL, echo=True)


def init_db():
    import models  # noqa
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

Переменные окружения (`.env`, не попадает в git благодаря `.gitignore`):

```
DB_ADMIN=postgresql://postgres:ПАРОЛЬ@localhost/lab1_finance_db
JWT_SECRET=super_secret_key_change_me_12345
```

---

## Эндпоинты API

### Auth (авторизация)

| Метод | Путь | Описание |
|---|---|---|
| POST | `/auth/register` | Регистрация нового пользователя |
| POST | `/auth/login` | Авторизация (получение JWT-токена) |
| GET | `/auth/me` | Информация о текущем пользователе (по токену) |
| PATCH | `/auth/me` | Обновление своего имени/пароля |

### Users

| Метод | Путь | Описание |
|---|---|---|
| GET | `/user/list` | Список пользователей |
| GET | `/user/{user_id}` | Пользователь по id |
| POST | `/user` | Создание пользователя (служебный CRUD) |
| DELETE | `/user/delete{user_id}` | Удаление пользователя |

### Accounts (счета)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/account/list` | Список счетов |
| GET | `/account/{account_id}` | Счёт по id |
| POST | `/account` | Создание счёта |
| DELETE | `/account/delete{account_id}` | Удаление счёта |

### Categories (категории)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/category/list` | Список категорий |
| GET | `/category/{category_id}` | Категория по id |
| POST | `/category` | Создание категории |
| DELETE | `/category/delete{category_id}` | Удаление категории |

### Tags (теги)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/tag/list` | Список тегов |
| POST | `/tag` | Создание тега |

### Budgets (бюджеты)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/budget/list` | Список бюджетов |
| GET | `/budget/{budget_id}` | Бюджет по id |
| POST | `/budget` | Создание бюджета |
| DELETE | `/budget/delete{budget_id}` | Удаление бюджета |

### Transactions (транзакции)

| Метод | Путь | Описание |
|---|---|---|
| GET | `/transaction/list` | Список транзакций |
| GET | `/transaction/{transaction_id}` | Транзакция с вложенной категорией |
| GET | `/transaction/{transaction_id}/with_tags` | Транзакция с вложенным списком тегов |
| POST | `/transaction` | Создание транзакции |
| PATCH | `/transaction/{transaction_id}` | Обновление транзакции |
| DELETE | `/transaction/delete{transaction_id}` | Удаление транзакции |
| POST | `/transaction/{transaction_id}/tag/{tag_id}` | Привязка тега к транзакции (many-to-many, с доп. полем `note`) |

---

## Аутентификация

JWT-аутентификация и хэширование паролей реализованы **полностью вручную**, без сторонних библиотек-обёрток (`passlib`, `python-jose`, `pyjwt` не используются) — только базовые модули стандартной библиотеки Python: `hashlib`, `hmac`, `secrets`, `base64`, `json`.

### Хэширование пароля (PBKDF2-HMAC-SHA256)

```python
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return f"{salt}${hashed}"


def verify_password(password: str, stored: str) -> bool:
    salt, hashed = stored.split("$")
    check = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 100_000
    ).hex()
    return hmac.compare_digest(check, hashed)
```

### Генерация и проверка JWT (вручную, по спецификации JWT)

```python
def create_access_token(user_id: int) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "exp": int(time.time()) + JWT_EXPIRE_MINUTES * 60,
        "iat": int(time.time()),
    }
    header_b64 = _b64url_encode(json.dumps(header).encode())
    payload_b64 = _b64url_encode(json.dumps(payload).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_access_token(token: str) -> Optional[dict]:
    header_b64, payload_b64, signature_b64 = token.split(".")
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_signature_b64 = _b64url_encode(
        hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    )
    if not hmac.compare_digest(expected_signature_b64, signature_b64):
        return None  # подпись не совпадает
    payload = json.loads(_b64url_decode(payload_b64))
    if payload.get("exp", 0) < time.time():
        return None  # токен просрочен
    return payload
```

### Dependency для защищённых эндпоинтов

```python
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = session.get(User, int(payload.get("sub")))
    if user is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user
```

---

## Миграции (Alembic)

Alembic настроен с автогенерацией миграций. URL базы данных передаётся из `.env` через `core/config.py`:

```python
# migrations/env.py
from core.config import DB_URL
from models import *  # noqa

config.set_main_option("sqlalchemy.url", DB_URL)
target_metadata = SQLModel.metadata
```

Команды:

```bash
# Создание миграции
alembic revision --autogenerate -m "init"

# Применение миграций
alembic upgrade head
```

За время разработки были применены миграции:
1. `init` — создание всех 7 таблиц
2. `add password to user` — добавление поля `hashed_password` для JWT-авторизации

---

## Структура проекта

```
lab1/
├── .env                     # Переменные окружения (не в git)
├── .gitignore
├── alembic.ini              # Конфигурация Alembic
├── requirements.txt
├── main.py                  # Сборка FastAPI-приложения и роутеров
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── core/
│   ├── config.py            # Настройки из .env
│   ├── security.py          # Хэширование паролей, JWT (вручную)
│   └── dependencies.py      # get_current_user
├── database/
│   └── connection.py        # Подключение к БД, get_session
├── models/
│   ├── __init__.py          # Сборка метадаты для Alembic
│   ├── user.py
│   ├── account.py
│   ├── category.py
│   ├── tag.py
│   ├── budget.py
│   ├── transaction.py
│   └── links.py             # TransactionTagLink (ассоциативная)
└── routers/
    ├── auth.py               # /auth/register, /auth/login, /auth/me
    ├── user.py
    ├── account.py
    ├── category.py
    ├── tag.py
    ├── budget.py
    └── transaction.py
```

---

## Запуск

```bash
# 1. Создать БД в PostgreSQL (например, через pgAdmin)
#    CREATE DATABASE lab1_finance_db;

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Применить миграции
alembic upgrade head

# 4. Запустить сервер
uvicorn main:app --reload
```

Документация API доступна по адресу: `http://127.0.0.1:8000/docs`
