from sqlalchemy import ForeignKey, String, ARRAY, text, Text, JSON, BigInteger, Integer, Boolean, Numeric, DateTime, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from datetime import datetime
from database.database import Base
from sqlalchemy import ForeignKey

class Product(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    price_no_spp: Mapped[int] = mapped_column(Integer, nullable=True)
    price_spp: Mapped[int] = mapped_column(Integer, nullable=True)
    percent_spp: Mapped[float] = mapped_column(Float, nullable=True)