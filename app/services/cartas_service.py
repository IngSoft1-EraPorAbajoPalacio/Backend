from app.schema.partida_schema import *
from app.services.jugador_service import *
from sqlalchemy.exc import *
from app.services.partida_service import *
from sqlalchemy.orm import Session
from app.db.models import *
from app.schema.partida_schema import *
import random


CANTIDAD_CARTAS_FIG = 50
CANTIDAD_CARTAS_MOV = 49

cartas_figuras = [fig.name for fig in Figura]
cartas_movimientos = [mov.name for mov in Movimiento]


def inicializacion_figuras_db(db:Session):
    c = db.query(Figuras).count()
    if c == 0:
        cartas = []
        for i in range(2):
            for fig in Figura:
                cartas.append(Figuras(fig = fig))
        db.add_all(cartas)
        db.commit()

    
def inicializacion_movimientos_db(db:Session):
    c = db.query(Movimientos).count()
    if c == 0:
        movimientos = []
        for i in range(7):
            for mov in Movimiento:
                movimientos.append(Movimientos(mov=mov))
                
        db.add_all(movimientos)
        db.commit()    
          
            

def repartir_cartas_figuras(id_partida : int,db:Session):    
    
    id_figuras = list(range(1,CANTIDAD_CARTAS_FIG+1))
    random.shuffle(id_figuras)  
    
    partida = db.query(Partida).filter(Partida.id == id_partida).first()    
    jugadores = [jugador.jugador for jugador in partida.jugadores]
    cantidad_jugadores = len(jugadores)

    cartas_a_repartir = CANTIDAD_CARTAS_FIG // cantidad_jugadores 
    cartas_a_repartir = cartas_a_repartir * cantidad_jugadores

    id_figuras = id_figuras[:cartas_a_repartir]

    id_figuras = random.sample(id_figuras,len(id_figuras))
    
    cartas_entregadas = []
    for i in range(len(id_figuras)):
        jugador = jugadores[i % cantidad_jugadores]
        cartas_entregadas.append(CartasFigura(id_partida= id_partida , id_jugador= jugador.id, carta_fig=id_figuras[i]))

    db.add_all(cartas_entregadas)
    db.commit()
    
    
    
def repartir_cartas_movimientos(id_partida : int,db:Session):    
    
    id_movimientos = list(range(1,CANTIDAD_CARTAS_MOV+1))
    
    partida = db.query(Partida).filter(Partida.id == id_partida).first()    
    jugadores = [jugador.jugador for jugador in partida.jugadores]
    cantidad_jugadores = len(jugadores)

    cartas_a_repartir = CANTIDAD_CARTAS_MOV // cantidad_jugadores 
    cartas_a_repartir = cartas_a_repartir * cantidad_jugadores
    
    id_movimientos = id_movimientos[:cartas_a_repartir]

    id_movimientos = random.sample(id_movimientos,len(id_movimientos))

    cartas_entregadas = []
    for i in (range(len(id_movimientos))):
        jugador = jugadores[i % cantidad_jugadores]
        cartas_entregadas.append(CartaMovimientos(id_partida= id_partida,id_jugador=jugador.id, carta_mov = id_movimientos[i]))

    db.add_all(cartas_entregadas)
    db.commit()    
    


