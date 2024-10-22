from app.db.base import SessionLocal
from app.db.models import Jugador
from sqlalchemy.exc import *
from sqlalchemy.orm import Session
from app.db.models import *
from fastapi import HTTPException

def crear_jugador(nombre: str,db: Session):
    jugador_creado = Jugador(nickname=nombre)
    try :
        db.add(jugador_creado)
        db.commit()
        return jugador_creado
    except SQLAlchemyError as e :
        print(f"Ocurrió un error al crear el jugador : {e}")
                   
def obtener_jugadores(id_partida:int,db : Session):
    partida = db.query(Partida).filter(Partida.id == id_partida).first()
    if partida is None:
        raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")
    return [jugador.jugador for jugador in partida.jugadores]
         
def obtener_id_jugadores(id_partida:int,db : Session):
    partida = db.query(Partida).filter(Partida.id == id_partida).first()
    return [jugador.id_jugador for jugador in partida.jugadores]          


def obtener_cantidad_jugadores(id_partida: int, db: Session):
    partida = db.query(Partida).filter(Partida.id == id_partida).first()
    return len(partida.jugadores)

