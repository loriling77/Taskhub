from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    Identity,
    func,
)
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(
        Integer,
        Identity(always=True),
        primary_key=True
    )

    username:Mapped[str] = mapped_column(
        String[50],
        unique=True,
        nullable=False
    )

    email:Mapped[str] = mapped_column(
        String[255],
        unique=True,
        nullable=False
    )

    password_hash:Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    created_at:Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        server_default=func.now(),
        nullable=False
    )
