from sqlmodel import SQLModel, Session, create_engine

from core.config import DB_URL

engine = create_engine(DB_URL, echo=True)


def init_db():
    # Импорт моделей должен произойти до создания таблиц,
    # чтобы SQLModel.metadata знал обо всех сущностях проекта
    import models  # noqa
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
