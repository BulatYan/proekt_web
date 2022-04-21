import sqlalchemy
from .db_session import SqlAlchemyBase


class Description(SqlAlchemyBase):
    __tablename__ = 'Description'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    member_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("Users.id"))
    author_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("Users.id"))
    har01 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har02 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har03 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har04 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har05 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har06 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har07 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har08 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har09 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har10 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har11 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har12 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    har13 = sqlalchemy.Column(sqlalchemy.Boolean, default=False)