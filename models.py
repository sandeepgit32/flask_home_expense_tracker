from typing import List
from db import db


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    last_login_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, password, name, surname):
        self.username = username
        self.password = password
        self.name = name
        self.surname = surname

    @classmethod
    def find_by_usename(cls, username: str) -> "TransactionModel":
        return cls.query.filter_by(username=username).first()


class TransactionModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    transaction_day = db.Column(db.Integer, nullable=False)
    transaction_month = db.Column(db.Integer, nullable=False)
    transaction_year = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False) # 'positive'/'negative'
    storing_datetime = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(20), nullable=True)
    value = db.Column(db.Float(precision=2), nullable=False)

    @classmethod
    def find_by_id(cls, id: int) -> "TransactionModel":
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_year_month_type(cls, transaction_type:str, transaction_year: int, transaction_month: int, user: str) -> List["TransactionModel"]:
        return cls.query.filter_by(transaction_type=transaction_type)\
            .filter_by(transaction_month=transaction_month)\
            .filter_by(transaction_year=transaction_year)\
            .filter_by(user=user)\
            .order_by(cls.transaction_year.desc(), cls.transaction_month.desc(), \
                cls.transaction_day.desc(), cls.storing_datetime.desc())

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()