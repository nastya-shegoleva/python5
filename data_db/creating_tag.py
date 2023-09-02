from data_db import db_session
from data_db.inf_game import InfGame
from data_db.standard_game import Standard_game


def add_inf_game(score):
    inf_game = InfGame()
    inf_game.score = score
    db_sess = db_session.create_session()
    db_sess.add(inf_game)
    db_sess.commit()
    db_sess.close()


def add_stand_game(score, level):
    standard_game = Standard_game()
    standard_game.score = score
    standard_game.level = level
    db_sess = db_session.create_session()
    db_sess.add(standard_game)
    db_sess.commit()
    db_sess.close()



