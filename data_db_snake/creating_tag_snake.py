from data_db_snake import db_session_snake
from data_db_snake.inf_game_snake import InfGame_snake
from data_db_snake.standart_game_snake import Standard_game_snake



def add_inf_game(score):
    inf_game = InfGame_snake()
    inf_game.score = score
    db_sess = db_session_snake.create_session()
    db_sess.add(inf_game)
    db_sess.commit()
    db_sess.close()


def add_stand_game(score, level):
    standard_game = Standard_game_snake()
    standard_game.score = score
    standard_game.level = level
    db_sess = db_session_snake.create_session()
    db_sess.add(standard_game)
    db_sess.commit()
    db_sess.close()



