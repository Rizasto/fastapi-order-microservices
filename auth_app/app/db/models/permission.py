from app.db.base import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Permission(Base):
    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
