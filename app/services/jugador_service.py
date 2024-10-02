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


    
"""    
def obtener_jugadores_db(db:Session):
    try : 
        jugadores = db.query(Jugador).all()
        return [JugadorOut(id=jugador.id, nickname=jugador.nickname) for jugador in jugadores]            
    except Exception as e:
        print(f'Ocurrió una excepción {e}')


def obtener_jugador_particular(id:int, db : Session):
    jugador = db.query(Jugador).filter(Jugador.id == id).first()
    if jugador is None:
        return {f"No existe jugador con id {id}"}
    return jugador


def eliminar_jugador_db(id: int, db:Session) :
    try :
        jugador = db.query(Jugador).filter(Jugador.id == id).first()
        db.delete(jugador)
        db.commit()
        return JugadorOut(id=jugador.id, nickname=jugador.nickname)
    except Exception as e:
        print(f"Ocurrió una excepción {e}")


def obtener_cartas_movimientos():
    return None
def obtener_cartas_figura():
    return None
def  get_tablero():
    return None



"""
"""
def agregar_jugador(self,nickname : str) -> JugadorOut :
    session = SessionLocal()
    jugador_creado = Jugador(nickname=nickname)
    try:
        session.add(jugador_creado)
        session.commit()
            return JugadorOut(id= jugador_creado.id, nickname=jugador_creado.nickname)
        except SQLAlchemyError as e :
            print(str(e))
        finally:
            session.close()            
         
    def obtener_partidas_de_jugador(self,id) :
        session = SessionLocal()
        jugador = self.obtener_jugador_particular(id)
        for jugador_partida in jugador.relacion_JugadorPartida:
            print(jugador_partida)        



"""