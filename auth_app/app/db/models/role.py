from app.db.base import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permission"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permission.id"), nullable=False)
