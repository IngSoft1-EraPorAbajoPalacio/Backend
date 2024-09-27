from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import NoResultFound
from db.models import Partida,Jugador_Partida, Jugador
from typing import List
from sqlalchemy.exc import *
from sqlalchemy.orm import Session
from schema.partida_schema import *
from fastapi.exceptions import HTTPException
from .ficha_service import *
from .cartas_service import repartir_cartas_figuras


def obtener_partida(id:int, db:Session):
    print(f"el id de la partida es : {id}")
    resultado = db.query(Partida).filter(Partida.id == id).first()
    print(f"el resultado es {resultado}")
    return resultado

def obtener_id(id : int , db : Session):
    return db.query(Jugador).filter(Jugador.id == id).first()


def obtener_partidas_db(db:Session):
    partidas = db.query(Partida).all()
    if not partidas:
        raise HTTPException(status_code=404, detail="No existe niguna partida")
    return partidas


def obtener_partida_particular(id:int, db:Session) :
    partida = db.query(Partida).filter(Partida.id == id).first()
    if partida is None:
        raise HTTPException(status_code=404, detail=f"No existe partida con id : {id}")
    return partida


def create_partida(partida : PartidaCreate, db:Session) :
    
    id_owner = obtener_id(partida.id_owner,db)
    
    if id_owner is None:
        raise Exception(f"No existe jugador con id : {partida.id_owner}") 
    
    
    partida_creada = Partida(nombre=partida.nombre_partida,
                             min=partida.min,
                             max=partida.max,
                             activa=partida.activa,
                             id_owner = partida.id_owner)
    try :
        db.add(partida_creada)
        db.commit()
        db.refresh(partida_creada)
    except SQLAlchemyError as e :
        print(str(e))
        
    #falta unir el owner a la partida
    
    nuevo_jugador_partida = Jugador_Partida(
                            id_jugador= partida.id_owner,
                            id_partida= partida_creada.id)    
        
    db.add(nuevo_jugador_partida)
    db.commit()
    
    return PartidaResponse(id= partida_creada.id, nombre= partida_creada.nombre, min=partida.min, max = partida.max)
        
        
        
        
def eliminar_partida_db(id: int, db:Session) :
        partida = db.query(Partida).filter(Partida.id == id).first()
        if partida is None:
            raise ValueError(f"No existe partida con id {id}")    
        db.delete(partida)
        db.commit()
        return PartidaResponse(id=partida.id, nombre=partida.nombre)

        
        
def unirse_partida(partidainput : UnirsePartidaRequest , db : Session):
    
    #verifico que la partida exista
    partida_obtenida = db.query(Partida).filter(Partida.id == partidainput.id_partida).first()
    if partida_obtenida is None:
        raise HTTPException(status_code=404,detail=f"No existe partida con id {partidainput.id_partida}")
    
    #verifico que el jugador no se encuentre en la partida
    esta_registrado = db.query(Jugador_Partida).filter(Jugador_Partida.id_jugador == partidainput.id_jugador,
                                                       Jugador_Partida.id_partida == partidainput.id_partida).first()
    if (esta_registrado):
        raise HTTPException(status_code=410,detail= f"El usuario ya está registrado en la partida con id {partidainput.id_partida}")

    #verifico que la cantidad de jugadores es entre 3 y 4
    partida = db.query(Partida).filter(Partida.id == partidainput.id_partida).first()
    cantidad_jugadores = len(partida.jugadores)
    print(cantidad_jugadores)
    
    if (cantidad_jugadores >= partida.max) :
        raise HTTPException(status_code=404, detail=f"Partida con id {partidainput.id_partida} llena")

    agregar_jugador = Jugador_Partida(id_jugador = partidainput.id_jugador,
                                     id_partida = partidainput.id_partida)
    
    db.add(agregar_jugador)
    db.commit()
    
    return UnirsePartidaResponse(id_jugador=partidainput.id_jugador,id_partida=partidainput.id_partida)   
       
       
       
def iniciar_partida(iniciarPartida : IniciarPartida , db : Session):
    
    #fijarme si quien inicia la partida es el owner
    
    is_owner = db.query(Partida).filter(Partida.id_owner == iniciarPartida.id_jugador).first()
    
    if (is_owner is None):
        raise HTTPException(status_code=404, detail="Solo puede iniciar la partida el owner")
    
    #me fijo que no esté iniciado
    
    partida = obtener_partida_particular(iniciarPartida.id_partida,db)

    if(partida.activa == True):
        raise HTTPException(status_code=404, detail=f"La partida con id {iniciarPartida.id_partida} ya esta iniciada")
    
    #inicializacio de tablero
    crear_tablero(iniciarPartida.id_partida,db)
    
    repartir_fichas(iniciarPartida.id_partida, db)
    
    partida_activa = obtener_partida_particular(iniciarPartida.id_partida,db)
    partida_activa.activa = True
    db.commit()
    
    #reparto de cartas
    #NO ANDArepartir_cartas_figuras(iniciarPartida,db)    
    
    return InicarPartidaResponse(id_jugador=iniciarPartida.id_jugador  ,id_partida=iniciarPartida.id_partida)
    
    
    
    
    
def get_partidas():
    return None


def change_turno():
    return None 

