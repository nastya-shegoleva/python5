import datetime

import sqlalchemy

from data_db_snake.db_session_snake import SqlAlchemyBase


class Standard_game_snake(SqlAlchemyBase):
    __tablename__ = 'standard_game'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    create_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    score = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f'<Standard_game_snake> {self.id} | {self.level} | {self.score} | {self.create_date}'
