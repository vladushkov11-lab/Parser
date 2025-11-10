from datetime import datetime
from sqlalchemy import Integer, func, ARRAY, String, JSON, create_engine
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, create_session, sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import class_mapper

DATABASE_URL = "mysql+asyncmy://parser:12345678@localhost/app_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    update_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

uniq_str_an = Annotated[str, mapped_column(unique=True)]
array_or_none_an = Annotated[list[str] | None, mapped_column(JSON())]

def to_dict(self) -> dict:
    columns = class_mapper(self.__class__).columns
    return {column.key: getattr(self, column.key) for column in columns}