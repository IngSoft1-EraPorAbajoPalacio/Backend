from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Jugador, Ficha
from sqlalchemy.exc import *
from app.schema.juego_schema import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *
from app.services.partida_service import *

class JuegoService:
    def validar_movimiento(self, movimiento: int, posicion_1: tuple, posicion_2: tuple):
        x1, y1 = posicion_1
        x2, y2 = posicion_2

        if movimiento == idMovimiento.mov_diagonal_doble:
            # Mover dos pasos en diagonal
            return abs(x1 - x2) == 2 and abs(y1 - y2) == 2
        
        elif movimiento == idMovimiento.mov_lineal_doble:
            # Mover dos pasos horizontalmente o verticalmente
            return (abs(x1 - x2) == 2 and y1 == y2) or (abs(y1 - y2) == 2 and x1 == x2)
        
        elif movimiento == idMovimiento.mov_lineal_simple:
            # Mover un paso horizontalmente o verticalmente
            return (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2)
        
        elif movimiento == idMovimiento.mov_diagonal_simple:
            # Mover un paso en diagonal
            return abs(x1 - x2) == 1 and abs(y1 - y2) == 1
        
        elif movimiento == idMovimiento.mov_L_izq:
            # Mover en forma de L hacia la izquierda
            return (
                (x2 - x1 == 1  and y2 - y1 == -2) or 
                (x2 - x1 == -1 and y2 - y1 == 2)  or 
                (y2 - y1 == 1  and x2 - x1 == 2)  or 
                (y2 - y1 == -1 and x2 - x1 == -2)
            )

        elif movimiento == idMovimiento.mov_L_der:
            # Mover en forma de L hacia la derecha
            return (
                (x2 - x1 == 1  and y2 - y1 == 2)  or 
                (x2 - x1 == -1 and y2 - y1 == -2) or 
                (y2 - y1 == 1  and x2 - x1 == -2) or 
                (y2 - y1 == -1 and x2 - x1 == 2)
            )
        
        elif movimiento == idMovimiento.mov_lineal_lateral:
            # Mover una ficha con cualquiera de las cuatro que estén en los extremos de su misma fila o columna.
            return (
                (x1 == x2 and (y2 == 0 or y2 == 5 or y1 == 0 or y1 == 5)) or 
                (y1 == y2 and (x2 == 0 or x2 == 5 or x1 == 0 or x1 == 5))
            )

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

        if not db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == id_partida, 
                                                 CartaMovimientos.carta_mov == movimiento.idCarta).first().en_mano:
            raise HTTPException(status_code=404, detail=f"La carta {movimiento.idCarta} no está en tu mano")

        tablero = partida.tablero
        carta_movimiento = db.query(Movimientos).filter(Movimientos.id == movimiento.idCarta).first().mov.value

        posicion_1 = (movimiento.posiciones[0].x, movimiento.posiciones[0].y)
        posicion_2 = (movimiento.posiciones[1].x, movimiento.posiciones[1].y)
        
        # Validar que las posiciones sean diferentes
        if posicion_1 == posicion_2:
            raise HTTPException(status_code=400, detail="Las posiciones deben ser diferentes")

        # Validar que las posiciones estén dentro del tablero
        if not (0 <= posicion_1[0] < 6 and 0 <= posicion_1[1] < 6 and 0 <= posicion_2[0] < 6 and 0 <= posicion_2[1] < 6):
            raise HTTPException(status_code=400, detail="Posiciones fuera del tablero")
        
        # Validar el movimiento
        if not self.validar_movimiento(carta_movimiento, posicion_1, posicion_2):
            raise HTTPException(status_code=400, detail="Movimiento inválido")
        
        # Eliminar la carta de la mano del jugador
        db.query(CartaMovimientos).filter(
            CartaMovimientos.id_partida == id_partida,
            CartaMovimientos.id_jugador == id_jugador,
            CartaMovimientos.carta_mov == movimiento.idCarta
        ).first().en_mano = False

        # Cambiar las posiciones de las fichas
        ficha1 = db.query(Ficha).filter(
                Ficha.id_tablero == tablero.id, 
                Ficha.x == posicion_1[0],
                Ficha.y == posicion_1[1]
        ).first()

        ficha2 = db.query(Ficha).filter(
                Ficha.id_tablero == tablero.id, 
                Ficha.x == posicion_2[0],
                Ficha.y == posicion_2[1]
        ).first()

        ficha1.color, ficha2.color = ficha2.color, ficha1.color
        
        db.commit()
        
        response = {"type": "MovimientoParcial", 
                    "carta": {"id": movimiento.idCarta, "movimiento": carta_movimiento}, 
                    "fichas": [{"x": ficha2.x, "y": ficha2.y, "color": ficha2.color.name}, 
                               {"x": ficha1.x, "y": ficha1.y, "color": ficha1.color.name}]
                    }
        return response

juego_service = JuegoService()
