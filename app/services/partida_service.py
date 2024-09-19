from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from db.models import Partida, engine
from typing import List

# Crea una sesión
Session = sessionmaker(bind=engine)

class PartidaBD:

    def create_partida():
        return None

    def iniciar_partida():
        return None

    def get_partidas():
        return None

    def add_player_to_partida():
        return None
    
    def change_turno():
        return None 
