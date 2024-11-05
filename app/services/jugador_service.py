from app.db.base import SessionLocal
from app.db.models import Jugador
from sqlalchemy.exc import *
from sqlalchemy.orm import Session
from app.db.models import *
from fastapi import HTTPException
from app.services.bd_service import db_service


def crear_jugador(nombre: str,db: Session):
    jugador_creado = Jugador(nickname=nombre)
    try :
        db.add(jugador_creado)
        db.commit()
        return jugador_creado
    except SQLAlchemyError as e :
        print(f"Ocurrió un error al crear el jugador : {e}")
                   
def obtener_jugadores(id_partida:int,db : Session):
    partida = db_service.obtener_partida(id_partida, db)
    if partida is None:
        raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")
    return [jugador.jugador for jugador in partida.jugadores]
     
def obtener_id_jugadores(id_partida:int,db : Session):
    partida = db_service.obtener_partida(id_partida, db)
    return [jugador.id_jugador for jugador in partida.jugadores]          

def obtener_cantidad_jugadores(id_partida: int, db: Session):
    partida = db_service.obtener_partida(id_partida, db)
    return len(partida.jugadores)

def pertenece( id_partida: int, id_jugador: int, db: Session) -> bool:
      id_jugadores = obtener_id_jugadores(id_partida, db)
      return id_jugador in id_jugadores