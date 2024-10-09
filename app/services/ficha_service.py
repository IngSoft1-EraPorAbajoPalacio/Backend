from sqlalchemy.exc import *
import random
from sqlalchemy.orm import Session
from app.db.models import *

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
       
                
            
