from app.schema.juego_schema import *
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Jugador, Ficha
from sqlalchemy.exc import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *
from app.services.partida_service import *

class JuegoService:
    def validar_movimiento(self, movimiento: int, posicion_inicial: tuple, posicion_final: tuple):
        x1, y1 = posicion_inicial
        x2, y2 = posicion_final

        if movimiento == 1:
            # Mover dos pasos en diagonal
            return abs(x1 - x2) == 2 and abs(y1 - y2) == 2
        
        elif movimiento == 2:
            # Mover dos pasos horizontalmente o verticalmente
            return (abs(x1 - x2) == 2 and y1 == y2) or (abs(y1 - y2) == 2 and x1 == x2)
        
        elif movimiento == 3:
            # Mover un paso horizontalmente o verticalmente
            return (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2)
        
        elif movimiento == 4:
            # Mover un paso en diagonal
            return abs(x1 - x2) == 1 and abs(y1 - y2) == 1
        
        elif movimiento == 5:
            if(x2 > x1):
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            # Mover en forma de L hacia la izquierda
            return (x1 - x2 == 1 and y1 - y2 == 2) or (x1 - x2 == 2 and y1 - y2 == -1)

        elif movimiento == 6:
            if(x1 > x2):
                x1, x2 = x2, x1
                y1, y2 = y2, y1
            # Mover en forma de L hacia la derecha
            return (x1 - x2 == -1 and y1 - y2 == 2) or (x1 - x2 == -2 and y1 - y2 == -1)
        
        elif movimiento == 7:
            # Mover una ficha con cualquiera de las cuatro que estén en los extremos de su misma fila o columna.
            return (x1 == x2 and (y2 == 0 or y2 == 5)) or (y1 == y2 and (x2 == 0 or x2 == 5))

        else:
            return False

    async def jugar_movimiento(self, id_partida: int, id_jugador: int, movimiento: JugarMovimientoRequest, db: Session):
        partida = partida_service.obtener_partida(id_partida, db)
        if not partida.activa:
            raise HTTPException(status_code=404, detail="La partida no ha sido iniciada")
        
        if not partida_service.pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail="El jugador no pertenece a la partida")
        
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        if not jugador.jugando:
            raise HTTPException(status_code=404, detail="No es tu turno")

        if not db.query(CartaMovimientos).filter(CartaMovimientos.carta_mov == movimiento.idCarta).first().en_mano:
            raise HTTPException(status_code=404, detail="La carta no está en tu mano")

        tablero = partida.tablero
        carta_movimiento = db.query(Movimientos).filter(Movimientos.id == movimiento.idCarta).first().mov.value

        posicion_inicial = (movimiento.posiciones[0].x, movimiento.posiciones[0].y)
        posicion_final = (movimiento.posiciones[1].x, movimiento.posiciones[1].y)
        
        # Validar que las posiciones sean diferentes
        if posicion_inicial == posicion_final:
            raise HTTPException(status_code=400, detail="Las posiciones deben ser diferentes")

        # Validar que las posiciones estén dentro del tablero
        if not (0 <= posicion_inicial[0] < 6 and 0 <= posicion_inicial[1] < 6 and 0 <= posicion_final[0] < 6 and 0 <= posicion_final[1] < 6):
            raise HTTPException(status_code=400, detail="Posiciones fuera del tablero")
        
        # Validar el movimiento
        if not self.validar_movimiento(carta_movimiento, posicion_inicial, posicion_final):
            raise HTTPException(status_code=400, detail="Movimiento inválido")
        
        # Eliminar la carta de la mano del jugador
        db.query(CartaMovimientos).filter(CartaMovimientos.carta_mov == movimiento.idCarta).first().en_mano = False

        # Cambiar las posiciones de las fichas
        ficha_inicial = db.query(Ficha).filter_by(id_tablero=tablero.id, x=posicion_inicial[0], y=posicion_inicial[1]).first()
        ficha_final = db.query(Ficha).filter_by(id_tablero=tablero.id, x=posicion_final[0], y=posicion_final[1]).first()

        ficha_inicial.x, ficha_final.x = ficha_final.x, ficha_inicial.x
        ficha_inicial.y, ficha_final.y = ficha_final.y, ficha_inicial.y
        ficha_inicial.color, ficha_final.color = ficha_final.color, ficha_inicial.color
        
        db.commit()
        
        response = {"type": "MovimientoParcial", 
                    "carta": {"id": movimiento.idCarta, "movimiento": carta_movimiento}, 
                    "fichas": [{"x": ficha_final.x, "y": ficha_final.y, "color": ficha_final.color.name}, {"x": ficha_inicial.x, "y": ficha_inicial.y, "color": ficha_inicial.color.name}]}
        return response

juego_service = JuegoService()
