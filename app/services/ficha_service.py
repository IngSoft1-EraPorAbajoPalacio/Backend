from sqlalchemy.exc import *
import random
from sqlalchemy.orm import Session
from app.db.models import *
from app.schema.juego_schema import Posicion

TAMANO_TABLERO = 6

def crear_tablero(id_partida: int, db: Session):       
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        if not partida:
            return []
        id_jugadores = [jugador.id_jugador for jugador in partida.jugadores]        
        tablero_nuevo = Tablero(id_partida = id_partida,
                                color_prohibido=random.choice(list(Color)),
                                turno = random.choice(id_jugadores) 
        )
        db.add(tablero_nuevo)
        db.commit()
        
        
def repartir_fichas(id_partida: int, db: Session):
    posiciones = []
    colores = {"Rojo": 0, "Verde": 0, "Azul": 0, "Amarillo": 0}
    max_colores = 9
    for x in range(TAMANO_TABLERO):
        for y in range(TAMANO_TABLERO):
            colores_disponibles = [color for color, count in colores.items() if count < max_colores]
            chosen_color = random.choice(colores_disponibles)
            colores[chosen_color] += 1
            posiciones.append(Ficha(x=x, y=y, color=chosen_color, id_tablero=id_partida))

    db.add_all(posiciones)
    db.commit()
    
       
def obtener_fichas(id_partida: int, db:Session) :
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        fichas = partida.tablero.fichas
        lista_fichas =  [{"x": ficha.x, "y": ficha.y, "color": ficha.color.name } for ficha in fichas]
        return lista_fichas   


def obtener_ficha(id_partida: int, x: int, y: int, db: Session):
    
    ficha = (
            db.query(Ficha).
            filter(
                Ficha.id_tablero == id_partida,
                Ficha.x == x,
                Ficha.y == y)
            .first()
        )
    return ficha
                
                
def switchear_fichas_tablero(movimiento_parcial: MovimientosParciales , db: Session):
        
        ficha1 = obtener_ficha(
            movimiento_parcial.id_partida, 
            movimiento_parcial.x1, 
            movimiento_parcial.y1, 
            db
        )
        
        ficha2 = obtener_ficha(
            movimiento_parcial.id_partida,
            movimiento_parcial.x2,
            movimiento_parcial.y2,
            db
        )
        
        color_ficha1 = ficha1.color
        ficha1.color = ficha2.color
        ficha2.color = color_ficha1
        
        db.delete(movimiento_parcial)
        db.commit()
        
        posiciones = [
            Posicion(
                x= ficha1.x,
                y= ficha1.y
            ),
            Posicion(
                x= ficha2.x,
                y= ficha2.y
            )
        ]              
        return posiciones 


def obtener_id_movimientos_en_mano(id_partida: int, id_jugador: int, db: Session):
    movimientos_en_mano = db.query(CartaMovimientos).filter(
        CartaMovimientos.id_partida == id_partida,
        CartaMovimientos.id_jugador == id_jugador,
        CartaMovimientos.en_mano == True
    ).all()
    
    id_movimientos = [mov.carta_mov for mov in movimientos_en_mano]

    return id_movimientos


def obtener_movimientos_en_mano(id_partida: int, id_jugador: int, db: Session):
    movimientos_en_mano = db.query(CartaMovimientos).filter(
        CartaMovimientos.id_partida == id_partida,
        CartaMovimientos.id_jugador == id_jugador,
        CartaMovimientos.en_mano == True
    ).all()
    
    movimientos = [fila.movimiento.mov.value for fila in movimientos_en_mano]
    
    return movimientos
    
def obtener_movimiento(idCarta: int, db: Session):
    movimiento = db.query(Movimientos).filter(Movimientos.id == idCarta).first()
    return movimiento.mov.value