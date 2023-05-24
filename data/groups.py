import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class Group(SqlAlchemyBase):
    __tablename__ = 'Groups'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    group_admin = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("Users.id"))
    group_name = sqlalchemy.Column(sqlalchemy.String, unique=True,
                                   nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)


class GroupMember(SqlAlchemyBase):
    __tablename__ = 'GroupMember'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    members_group = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("Groups.id"))
    member = sqlalchemy.Column(sqlalchemy.Integer,
                                    sqlalchemy.ForeignKey("Users.id"))


class Ticket(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Tickets'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    members_group = sqlalchemy.Column(sqlalchemy.Integer,
                                      sqlalchemy.ForeignKey("Groups.id"))
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
