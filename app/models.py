from datetime import datetime, timezone
from typing import List, Optional
import sqlalchemy as sa
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import database, login_manager
from flask import current_app


class Permissions:
    READ = 1  # you can read the public notes
    WRITE = 2  # you can write you own notes
    COMMENT = 4  # you can comment on notes made by others
    MODERATE = 8  # you can moderate comments and block notes made by others
    ADMIN = 16  # administration access


class Role(database.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=64), index=True, unique=True)
    default: Mapped[bool] = mapped_column(default=False, index=True)
    permissions: Mapped[int] = mapped_column(default=0)
    users: Mapped[List["User"]] = relationship(back_populates="role")

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permissions(self):
        self.permissions = 0

    @staticmethod
    def set_roles():
        roles = {
            "User": [Permissions.READ, Permissions.WRITE, Permissions.COMMENT],
            "Moderator": [Permissions.READ, Permissions.WRITE, Permissions.COMMENT,
                          Permissions.MODERATE],
            "Admin": [Permissions.READ, Permissions.WRITE, Permissions.COMMENT,
                      Permissions.MODERATE, Permissions.ADMIN]
        }
        default_role = "User"
        for role_from_dict in roles:
            query = sa.select(Role).where(Role.name == role_from_dict)
            role = database.session.scalar(query)
            if role is None:
                role = Role(name=role_from_dict)
            role.reset_permissions()
            for permission in roles[role_from_dict]:
                role.add_permission(permission)
            role.default = (role.name == default_role)
            database.session.add(role)
        database.session.commit()


class User(UserMixin, database.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=64), index=True, unique=True)
    email: Mapped[str] = mapped_column(String(length=128), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(length=256))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), index=True)
    role: Mapped["Role"] = relationship(back_populates="users")
    notes: Mapped[List["Note"]] = relationship(back_populates="author")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email in current_app.config["ADMINS"]:
                query = sa.select(Role).where(Role.name == "Admin")
                self.role = database.session.scalar(query)
            if self.role is None:
                query = sa.select(Role).where(Role.default == 1)
                self.role = database.session.scalar(query)

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', role='{self.role.name}')"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id):
    return database.session.get(User, int(id))


class Note(database.Model):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        index=True,
        default=lambda: datetime.now(timezone.utc)
    )
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    author: Mapped["User"] = relationship(back_populates="notes")

    def __repr__(self):
        return f"{self.__class__.__name__}(author='{self.author}', timestamp={self.timestamp.isoformat()}"
