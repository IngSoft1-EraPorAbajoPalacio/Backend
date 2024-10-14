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
CARTAS_EN_MANO = 3

cartas_figuras = [fig.name for fig in Figura]
cartas_movimientos = [mov.name for mov in Movimiento]

def inicializacion_figuras_db(db:Session):
    if db.query(Figuras).count() == 0:
        cartas = []
        for i in range(2):
            for fig in Figura:
                cartas.append(Figuras(fig = fig))
        db.add_all(cartas)
        db.commit()
    
def inicializacion_movimientos_db(db:Session):
    if db.query(Movimientos).count() == 0:
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
    
    id_movimientos = list(range(1,CANTIDAD_CARTAS_MOV+1))
    
    partida = db.query(Partida).filter(Partida.id == id_partida).first()    
    jugadores = [jugador.jugador for jugador in partida.jugadores]
    cantidad_jugadores = len(jugadores)

    cartas_a_repartir = CANTIDAD_CARTAS_MOV // cantidad_jugadores 
    cartas_a_repartir = cartas_a_repartir * cantidad_jugadores
    
    id_movimientos = id_movimientos[:cartas_a_repartir]

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
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        figuras = db.query(CartasFigura).filter(CartasFigura.id_jugador == id_jugador, CartasFigura.en_mano == True).all()
        cartas = [{"id": fig.carta_fig, "figura": fig.figura.fig.value } for fig in figuras]    
        resultado.append({
            "idJugador": id_jugador,
            "nombreJugador": jugador.nickname,
            "cartas": cartas
        })
        
    return resultado

def obtener_cartas_movimientos(id_partida: int, db: Session):
    id_jugadores = obtener_id_jugadores(id_partida, db)
    resultado = []
    
    for id_jugador in id_jugadores:
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        movimientos = db.query(CartaMovimientos).filter(CartaMovimientos.id_jugador == id_jugador, CartaMovimientos.en_mano == True).all()
        cartas = [{"id": mov.carta_mov, "movimiento": mov.movimiento.mov.value } for mov in movimientos]    
        resultado.append({
            "idJugador": id_jugador,
            "nombreJugador": jugador.nickname,
            "cartas": cartas
        })
        
    return resultado
