import datetime

import sqlalchemy


from data_db.db_session import SqlAlchemyBase


class InfGame(SqlAlchemyBase):
    __tablename__ = 'inf_game'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f'<InfGame> {self.id} | {self.score} | {self.create_date}'
