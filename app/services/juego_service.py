from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Jugador, Ficha
from sqlalchemy.exc import *
from app.schema.juego_schema import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *
from app.services.partida_service import *
from app.services.encontrar_fig import *
from sqlalchemy import desc

class JuegoService:

    def obtener_datos_partida(self, id_partida: int, id_jugador: int, db: Session):
        
        partida = partida_service.obtener_partida(id_partida, db)
        cartas_movimientos = obtener_cartas_movimientos_jugador(id_jugador, db)
        cartas_figuras = obtener_cartas_figuras(id_partida, db)
        fichas = fichas_service.obtener_fichas(id_partida, db)
        orden = obtener_id_jugadores(id_partida, db)
        cantidad_movimientos_parciales = (
            db.query(MovimientosParciales)
            .filter(
                MovimientosParciales.id_partida == id_partida,
                MovimientosParciales.id_jugador == id_jugador
            )
        ).count()
        
        response = {
            "type": "InicioConexion",
            "fichas": fichas,
            "orden": orden,
            "turnoActual": partida.tablero.turno,
            "colorProhibido": "Amarillo", # Hay que cambiar cuando se implemente el color prohibido
            "tiempo": 160, # Hay que cambiar cuando se implemente el temporizador
            "cartasMovimiento": cartas_movimientos,
            "cartasFigura": cartas_figuras,
            "cartasBloqueadas": [], # Hay que cambiar cuando se implemente el bloqueo de cartas
            "cantMovimientosParciales": cantidad_movimientos_parciales
        }
                
        return response

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
                (x2 - x1 == 1 and y2 - y1 == 2) or
                (x2 - x1 == -1 and y2 - y1 == -2) or
                (y2 - y1 == 1 and x2 - x1 == -2) or
                (y2 - y1 == -1 and x2 - x1 == 2)
            )
        
        elif movimiento == idMovimiento.mov_L_der:
            # Mover en forma de L hacia la derecha
            return (
                (x2 - x1 == 1 and y2 - y1 == -2) or
                (x2 - x1 == -1 and y2 - y1 == 2) or
                (y2 - y1 == 1 and x2 - x1 == 2) or
                (y2 - y1 == -1 and x2 - x1 == -2)
            )

        elif movimiento == idMovimiento.mov_lineal_lateral:
            # Mover una ficha con cualquiera de las cuatro que estén en los extremos de su misma fila o columna.
            return (
                (x1 == x2 and (y2 == 0 or y2 == 5 or y1 == 0 or y1 == 5)) or 
                (y1 == y2 and (x2 == 0 or x2 == 5 or x1 == 0 or x1 == 5))
            )

        else:
            return False

    def completar_figura(self, id_partida: int, id_jugador: int, figura: DeclararFiguraRequest, tipo: str, db: Session):
        if tipo == "descartar":
            # Eliminar la carta de la mano del jugador
            db.query(CartasFigura).filter(
                CartasFigura.id_partida == id_partida,
                CartasFigura.id_jugador == id_jugador,
                CartasFigura.carta_fig == figura.idCarta
            ).delete()

            # Cartas en mano
            cartas_en_mano = db.query(CartasFigura).filter(
                CartasFigura.id_partida == id_partida,
                CartasFigura.id_jugador == id_jugador,
                CartasFigura.en_mano == True
            ).all()
            cartas = []
            for carta in cartas_en_mano:
                cartas.append({
                    "id": carta.carta_fig,
                    "figura": carta.figura.fig.value
                })

            # Desbloquear la carta si es necesario    
            carta_bloqueada = db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == id_jugador,
                                             CartasFigura.en_mano == True,
                                             CartasFigura.bloqueada == True).first()
            esta_bloqueado = carta_bloqueada.bloqueada if carta_bloqueada else False
            cartas_en_mano = db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                                           CartasFigura.id_jugador == id_jugador,
                                                           CartasFigura.en_mano == True).count()
            if esta_bloqueado and cartas_en_mano == 1:
                carta_bloqueada.bloqueada = False
                return {
                    "completarFigura": "desbloquearFigura",
                    "cartasFig": cartas,
                    "idCarta": figura.idCarta,
                    "idJugador": id_jugador
                }
            else:
                return {
                    "completarFigura": "descartarFigura",
                    "cartasFig": cartas
                }
        elif tipo == "bloquear":
            # Bloquear la carta
            db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida, 
                                          CartasFigura.id_jugador == id_jugador,
                                          CartasFigura.carta_fig == figura.idCarta).first().bloqueada = True
            db.commit()
            return {
                "completarFigura": "bloquearFigura",
                "idCarta": figura.idCarta,
                "idJugador": id_jugador
            }
        
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
                Ficha.id_tablero == tablero.id_partida, 
                Ficha.x == posicion_1[0],
                Ficha.y == posicion_1[1]
        ).first()

        ficha2 = db.query(Ficha).filter(
                Ficha.id_tablero == tablero.id_partida, 
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
                
        fila_nueva = MovimientosParciales(
            id_partida = id_partida, id_jugador = id_jugador,
            movimiento = movimiento.idCarta,
            x1 = ficha1.x,
            y1 = ficha1.y,
            x2 = ficha2.x,
            y2= ficha2.y
        )
        
        db.add(fila_nueva)
        db.commit()
             
        return response
    
    async def declarar_figura(self, id_partida: int, id_jugador: int, figura: DeclararFiguraRequest, db: Session):
        partida = partida_service.obtener_partida(id_partida, db)
        if not partida.activa:
            raise HTTPException(status_code=404, detail="La partida no ha sido iniciada")
        
        if not partida_service.pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail="El jugador no pertenece a la partida")
    
        if not db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.carta_fig == figura.idCarta,
                                             CartasFigura.en_mano == True).first():
            raise HTTPException(status_code=431, detail=f"La carta {figura.idCarta} no está en tu mano")

        carta_figura = db.query(Figuras).filter(Figuras.id == figura.idCarta).first().fig.value
        
        # Validar la figura
        carta_figura = db.query(Figuras).filter(Figuras.id == figura.idCarta).first().fig.value
        if not carta_figura == figura.tipo_figura:
            raise HTTPException(status_code=432, detail="Figura inválida")

        # Eliminar movimientos parciales 
        movimintos_parciales = db.query(MovimientosParciales).filter(MovimientosParciales.id_jugador == id_jugador,
                                                                     MovimientosParciales.id_partida == id_partida).all()
        
        for mov in movimintos_parciales:
            cm = db.query(CartaMovimientos).filter(CartaMovimientos.id_jugador == id_jugador,
                                                   CartaMovimientos.id_partida == id_partida,
                                                   CartaMovimientos.carta_mov == mov.movimiento).first()
            cm.en_mano = False
        
        if movimintos_parciales is not None:
            for mov in movimintos_parciales:
                db.delete(mov)
                
        carta_figura = db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                                     CartasFigura.id_jugador == id_jugador,
                                                     CartasFigura.carta_fig == figura.idCarta).first()
        esta_en_mano = carta_figura.en_mano if carta_figura else False
        
        if esta_en_mano:
            # Descartar una figura propia
            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == id_jugador,
                                             CartasFigura.carta_fig == figura.idCarta).first().bloqueada:
                raise HTTPException(status_code=433, detail="No puedes descartar una figura bloqueada")
            
            # Descartar la carta y desbloquear si es necesario
            response = self.completar_figura(id_partida, id_jugador, figura, "descartar", db)
            db.commit()
            return response
        else:   
            # Bloquear una figura
            id_jugador = db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida, 
                                                       CartasFigura.carta_fig == figura.idCarta).first().id_jugador
            
            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == id_jugador,
                                             CartasFigura.carta_fig == figura.idCarta).first().bloqueada:
                raise HTTPException(status_code=434, detail="Figura ya bloqueada")
            
            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == id_jugador).count() == 1:
                raise HTTPException(status_code=435, detail="No puedes bloquear un jugador con una sola carta de figura")

            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == id_jugador,
                                             CartasFigura.bloqueada == True).count() == 1:
                raise HTTPException(status_code=436, detail="No puedes bloquear 2 cartas de un mismo jugador")
            
            # Bloquear la carta
            response = self.completar_figura(id_partida, id_jugador, figura, "bloquear", db)
            db.commit()
            return response
    
    
    def deshacer_movimiento(self, idPartida: int, idJugador: int, db: Session):
        
        ultimo_movimiento_parcial = (
            db.query(MovimientosParciales).filter(
                MovimientosParciales.id_partida == idPartida,
                MovimientosParciales.id_jugador == idJugador).order_by(desc(MovimientosParciales.id)).first()
        )

        if ultimo_movimiento_parcial is None:
            raise HTTPException(status_code=404, detail=f"El jugador con id {idJugador} no realizo ningun movimiento ")
                
        movimiento = obtener_movimiento(ultimo_movimiento_parcial.movimiento, db)
        
        carta_movimiento = db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == idPartida,
                                                             CartaMovimientos.id_jugador == idJugador,
                                                             CartaMovimientos.carta_mov == ultimo_movimiento_parcial.movimiento).first()
        
        carta_movimiento.en_mano = True
        posiciones_actualizadas = switchear_fichas_tablero(ultimo_movimiento_parcial, db)
        
        resultado = {
            "idCarta": ultimo_movimiento_parcial.movimiento,
            "movimiento": movimiento,
            "posiciones": posiciones_actualizadas
        }
                
        return resultado
    
    def deshacer_movimientos(self,idPartida: int, idJugador: int, db:Session):
        
        cartas =[]
        posiciones =[]
        
        movimientos = (
            db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == idPartida,
                                              CartaMovimientos.id_jugador == idJugador,
                                              CartaMovimientos.en_mano == True).all()
        )
        
        movimientos_en_mano = len(movimientos)
        movimientos_parciales = (
            db.query(MovimientosParciales).filter(MovimientosParciales.id_partida == idPartida,
                                                  MovimientosParciales.id_jugador == idJugador).all()
        )
                
        cantidad_mov_parciales = len(movimientos_parciales)
        cantidad_mov_deshechos = len(movimientos_parciales)
        
        while (cantidad_mov_parciales > 0) :
            movimiento_desecho = self.deshacer_movimiento(idPartida, idJugador, db)

            cartas.append({
                "id": movimiento_desecho['idCarta'],
                "movimiento": movimiento_desecho['movimiento']
            })

            posiciones.append(movimiento_desecho['posiciones'])
            cantidad_mov_parciales-=1
        
        resultado = {
            "cartas": cartas,
            "cantMovimientosDesechos": cantidad_mov_deshechos,
            "posiciones": posiciones
        }

        movimientos_a_devolver = max(0, 3 - movimientos_en_mano)
        
        asignacion = asignar_cartas_movimientos(idPartida, idJugador, movimientos_a_devolver, db)
        
        while len(resultado['cartas']) != movimientos_a_devolver:
            movimiento = db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == idPartida,
                                                           CartaMovimientos.id_jugador == idJugador,
                                                           CartaMovimientos.carta_mov == asignacion[0]['id']).first()
            movimiento.en_mano = True
            db.commit()
            
            resultado["cartas"].append(asignacion[0])
            asignacion.pop(0)
            
            
        print(f"al final retorno : {resultado}")    
        return  resultado   

juego_service = JuegoService()