from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import DateTime, String, Integer

class Base(DeclarativeBase):
	pass

class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	telegram_id: Mapped[str] = mapped_column(Integer(), unique=True)
	ya_token: Mapped[Optional[str]] = mapped_column(String(), nullable=True)
 
	login_hash: Mapped[Optional[str]] = mapped_column(String())
	login_expires_in: Mapped[Optional[datetime]] = mapped_column(DateTime(), nullable=True)
