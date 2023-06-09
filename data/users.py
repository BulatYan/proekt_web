import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    group = sqlalchemy.Column(sqlalchemy.Integer,
                              sqlalchemy.ForeignKey("Groups.id"))
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Task(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'Tasks'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("Users.id"))
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                  sqlalchemy.ForeignKey("Users.id"))
    group_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey("Groups.id"))
    short_task = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    detail_task = sqlalchemy.Column(sqlalchemy.String, unique=False)
    completed = sqlalchemy.Column(sqlalchemy.Boolean)
