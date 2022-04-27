import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase


class City(SqlAlchemyBase, UserMixin):
    __tablename__ = 'Cities'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    city = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return self.city


