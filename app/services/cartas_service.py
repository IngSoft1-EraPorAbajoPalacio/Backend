from sqlalchemy import select, distinct
from app.schema.partida_schema import *
from app.services.jugador_service import *
from sqlalchemy.exc import *
from app.services.partida_service import *
from sqlalchemy.orm import Session
from app.db.models import *
from app.schema.partida_schema import *
import random
from sqlalchemy import true
from sqlalchemy import func
from app.services.bd_service import db_service

CANTIDAD_CARTAS_FIG = 50
CANTIDAD_CARTAS_MOV = 49
CARTAS_EN_MANO = 3

ID_FIGURAS = list(range(1, CANTIDAD_CARTAS_FIG+1))
ID_MOVIMIENTOS = list(range(1,CANTIDAD_CARTAS_MOV+1))

cartas_figuras = [fig.name for fig in Figura]
cartas_movimientos = [mov.name for mov in Movimiento]

def inicializacion_figuras_db(db:Session):
    if db_service.cantidad_figuras(db) == 0:             
        figuras = [
            Figuras(fig=fig)
            for _ in range(2)
            for fig in Figura
        ]
        db.add_all(figuras)
        db.commit()
    
def inicializacion_movimientos_db(db:Session):
    if db_service.cantidad_movimientos(db) == 0:
        movimientos = [
            Movimientos(mov=mov)
            for _ in range(7)
            for mov in Movimiento
        ]                
        db.add_all(movimientos)
        db.commit()            
          
def repartir_cartas_figuras(id_partida : int,db:Session):    
    
    random.shuffle(ID_FIGURAS)  
    
    partida = db_service.obtener_partida(id_partida, db)    
    jugadores = [jugador.jugador for jugador in partida.jugadores]
    cantidad_jugadores = len(jugadores)

    cartas_a_repartir = CANTIDAD_CARTAS_FIG // cantidad_jugadores 
    cartas_a_repartir = cartas_a_repartir * cantidad_jugadores

    id_figuras = ID_FIGURAS[:cartas_a_repartir]

    id_figuras = random.sample(id_figuras,len(id_figuras))
    
    cartas_entregadas = []
    iteracion_cartas_en_mano = CARTAS_EN_MANO * cantidad_jugadores
    j = 1
    for i in range(len(id_figuras)):
        jugador = jugadores[i % cantidad_jugadores]
        cartaFigura = CartasFigura(id_partida= id_partida , id_jugador= jugador.id, carta_fig=id_figuras[i],en_mano=False)
        if (j <= iteracion_cartas_en_mano):
            cartaFigura.en_mano = True
            j+=1
        cartas_entregadas.append(cartaFigura)    

    db.add_all(cartas_entregadas)
    db.commit()
     
def repartir_cartas_movimientos(id_partida : int,db:Session):    
        
    partida = db_service.obtener_partida(id_partida, db)   
    jugadores = [jugador.jugador for jugador in partida.jugadores]
    cantidad_jugadores = len(jugadores)

    cartas_a_repartir = CANTIDAD_CARTAS_MOV // cantidad_jugadores 
    cartas_a_repartir = cartas_a_repartir * cantidad_jugadores
    
    id_movimientos = ID_MOVIMIENTOS[:cartas_a_repartir]

    id_movimientos = random.sample(id_movimientos,len(id_movimientos))

    cartas_entregadas = []
    j = 1
    iteracion_cartas_en_mano = CARTAS_EN_MANO * cantidad_jugadores
    for i in (range(len(id_movimientos))):
        jugador = jugadores[i % cantidad_jugadores]
        cartaMovimiento = CartaMovimientos(id_partida= id_partida,id_jugador=jugador.id, carta_mov = id_movimientos[i], en_mano=False)
        if (j <= iteracion_cartas_en_mano):
            cartaMovimiento.en_mano = True
            j+=1
        cartas_entregadas.append(cartaMovimiento)
            
    db.add_all(cartas_entregadas)
    db.commit()    
    
def obtener_cartas_figuras(id_partida: int, db: Session):
    id_jugadores = obtener_id_jugadores(id_partida, db)
    resultado = []
    
    for id_jugador in id_jugadores:
        jugador = db_service.obtener_jugador(id_jugador, db)
        figuras = db_service.obtener_figuras_en_mano(id_partida, id_jugador, db)
        cartas = [{"id": fig.carta_fig, "figura": fig.figura.fig.value } for fig in figuras]    
        resultado.append({
            "idJugador": id_jugador,
            "nombreJugador": jugador.nickname,
            "cartas": cartas
        })
        
    return resultado

def obtener_figuras_en_juego(id_partida: int, db: Session) -> List[int]:
    """retorna lista de tipos (sin repeticion ) de figura en juego (cartas de figura visibles)"""
    id_jugadores = obtener_id_jugadores(id_partida, db)
    tipos_figura = []
    
    for id_jugador in id_jugadores:
        figuras = db_service.obtener_figuras_en_mano(id_partida, id_jugador, db)
        cartas = [fig.figura.fig.value for fig in figuras if fig.figura]    
        tipos_figura.extend(cartas)
        
    return list(set(tipos_figura))

def obtener_cartas_movimientos(id_partida: int, db: Session):
    id_jugadores = obtener_id_jugadores(id_partida, db)
    resultado = []
    
    for id_jugador in id_jugadores:
        jugador = db_service.obtener_jugador(id_jugador, db)
        movimientos = db_service.obtener_movimientos_en_mano(id_partida, id_jugador, db)
        cartas = [{"id": mov.carta_mov, "movimiento": mov.movimiento.mov.value } for mov in movimientos]    
        resultado.append({
            "idJugador": id_jugador,
            "nombreJugador": jugador.nickname,
            "cartas": cartas
        })  
    return resultado
   

def asignar_cartas_figuras(idPartida: int, idJugador: int, reponer: int, db: Session):
       
    resultado = []  
    
    if reponer == 0:
        return resultado
    
    cartas_fig = db.query(CartasFigura).filter(
        CartasFigura.id_partida == idPartida,
        CartasFigura.id_jugador == idJugador,
        CartasFigura.en_mano == False).limit(reponer).all()     
    
    for fig in cartas_fig:
        fig.en_mano = True
        resultado.append(
            {
                "id": fig.carta_fig,
                "figura": fig.figura.fig.value
            }
        )
    
    db.commit()

    return resultado

    
def reposicion_cartas_figuras(idPartida: int, idJugador: int, db:Session):
    
    resultado = []   
            
    cartas_fig = db_service.obtener_figuras_en_mano(idPartida , idJugador, db)
    
    for mov in cartas_fig :
        resultado.append({
            "id": mov.carta_fig,
            "figura": mov.figura.fig.value
        })
        
    en_mano = len(cartas_fig)
    reponer = max(0, CARTAS_EN_MANO - en_mano)
    
    repuestas = asignar_cartas_figuras(idPartida, idJugador, reponer, db )  
    
    resultado = resultado + repuestas
    
    return resultado

def asignar_cartas_movimientos(idPartida: int, idJugador: int , reponer: int, db: Session): 
    
    resultado = []
    
    if reponer == 0:
        return resultado   
    
    cartas_mov = db.query(CartaMovimientos).filter(
        CartaMovimientos.id_partida == idPartida,
        CartaMovimientos.id_jugador == idJugador,
        CartaMovimientos.en_mano == False
    ).order_by(func.random()).limit(reponer).all()
    
    
    for mov in cartas_mov:
        resultado.append(
            {
                "id": mov.carta_mov,
                "movimiento": mov.movimiento.mov.value
            }
        )
   
    db.commit()
    
    return resultado


def reposicion_cartas_movimientos(idPartida: int, idJugador: int, db: Session):
        
    resultado = []    
        
    cartas_mov = db_service.obtener_movimientos_en_mano(idPartida, idJugador, db)
    
    for mov in cartas_mov:
        resultado.append({
            "id": mov.movimiento.id,
            "movimiento": mov.movimiento.mov.value         
        })
    
    en_mano = len(cartas_mov)
    
    reponer = max(0, CARTAS_EN_MANO - en_mano)
        
    repuestas =  asignar_cartas_movimientos(idPartida, idJugador, reponer, db)
    
    return resultado + repuestas       