from datetime import datetime
from sqlalchemy import Integer, func, ARRAY, String, JSON
from typing import Annotated
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://parser:12345678@localhost/app_db"
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True 
)

# Создаём синхронную сессию
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def connection(method):
    def wrapper(*args, **kwargs):
        session = SessionLocal()
        try:
            return method(*args, session=session, **kwargs)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    return wrapper
