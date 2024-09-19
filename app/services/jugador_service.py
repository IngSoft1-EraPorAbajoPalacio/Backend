from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from db.models import Partida, engine
from typing import List

# Crea una sesión
Session = sessionmaker(bind=engine)

class JugadorBD:

    def obtener_cartas_movimientos():
        return None

    def obtener_cartas_figura():
        return None

    def  get_tablero():
        return None

    
