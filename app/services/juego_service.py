from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import *
from app.schema.juego_schema import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *
from app.services.partida_service import *
from app.services.encontrar_fig import *
from app.services.bd_service import *
from app.db.models import Color


class JuegoService:
    
    def obtener_datos_partida(self, id_partida: int, id_jugador: int, db: Session):
                
        partida = db_service.obtener_partida(id_partida, db)
        cartas_movimientos = obtener_cartas_movimientos_jugador(id_partida, id_jugador, db)
        cartas_figuras = obtener_cartas_figuras(id_partida, db)
        cartas_bloqueadas = obtener_cartas_figuras_bloqueadas(id_partida, db)
        fichas = fichas_service.obtener_fichas(id_partida, db)
        orden = obtener_id_jugadores(id_partida, db)
        cantidad_movimientos_parciales = db_service.obtener_movimientos_parciales(id_partida, id_jugador, db)
        cantidad_movimientos_parciales = db_service.obtener_cantidad_movimientos_parciales(id_partida, id_jugador, db)
        color_prohibido = db_service.obtener_color_prohibido(id_partida, db)
        tiempo = db_service.obtener_tiempo_actual(id_partida, db)
        
        response = {
            "type": "InicioConexion",
            "fichas": fichas,
            "orden": orden,
            "turnoActual": partida.tablero.turno,
            "colorProhibido": color_prohibido,
            "tiempo": tiempo ,
            "cartasMovimiento": cartas_movimientos,
            "cartasFigura": cartas_figuras,
            "cartasBloqueadas": cartas_bloqueadas,
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

    def completar_figura(self, id_partida: int, jugador_a_bloquear: int, id_jugador: int, figura: DeclararFiguraRequest, tipo: str, db: Session):
        nombre_jugador = db_service.obtener_nombre_jugador(id_jugador, db)
        accion = ""
        idCarta = None
        idJugador = None
        color_prohibido = None
        gano = False
        cartas = []

        # Eliminar movimientos parciales
        movimientos_parciales = db_service.obtener_movimientos_parciales(id_partida, id_jugador, db)
        for mov in movimientos_parciales:
            db_service.eliminar_carta_movimiento(id_partida, id_jugador, mov.movimiento, db)

        db_service.eliminar_movimientos_parciales(id_partida, id_jugador, db)    
        
        #Cambio el color prohibido
        color = Color(figura.color)
        db_service.cambiar_color_prohibido(id_partida, color, db)
        color_prohibido = db_service.obtener_color_prohibido(id_partida, db)
        if tipo == "descartar":
            # Eliminar la carta de la mano del jugador
            db_service.eliminar_carta_figura(id_partida, id_jugador, figura.idCarta, db)
            
            # Verificar si el jugador ganó
            gano = db_service.cantidad_cartas_figuras(id_partida, id_jugador, db) == 0  

            # Cartas en mano
            cartas_en_mano = db_service.obtener_figuras_en_mano(id_partida, id_jugador, db)
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
                carta_a_desbloquear = db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                                                    CartasFigura.id_jugador == id_jugador,
                                                                    CartasFigura.en_mano == True).first()
                carta_bloqueada.bloqueada = False
                db.commit()

                accion = "desbloquearFigura"
                idCarta = carta_a_desbloquear.carta_fig
                idJugador = id_jugador
            else:
                accion = "descartarFigura"

        elif tipo == "bloquear":
            # Bloquear la carta
            db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida, 
                                          CartasFigura.id_jugador == jugador_a_bloquear,
                                          CartasFigura.carta_fig == figura.idCarta).first().bloqueada = True
            db.commit()
            accion = "bloquearFigura"
            idCarta = figura.idCarta
            idJugador = jugador_a_bloquear

        return {
            "completarFigura": accion,
            "idCarta": idCarta,
            "idJugador": idJugador,
            "colorProhibido": color_prohibido,
            "ganar": gano,
            "cartasFig": cartas,
            "nombre": nombre_jugador
        }
        
    async def jugar_movimiento(self, id_partida: int, id_jugador: int, movimiento: JugarMovimientoRequest, db: Session):
        partida = db_service.obtener_partida(id_partida, db)
        if not partida.activa:
            raise HTTPException(status_code=404, detail="La partida no ha sido iniciada")
        
        if not pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail="El jugador no pertenece a la partida")
        
        jugador = db_service.obtener_jugador(id_jugador, db)
        if not jugador.jugando:
            raise HTTPException(status_code=404, detail="No es tu turno")

        if not db_service.obtener_movimiento_en_mano(id_partida, movimiento.idCarta, db):
            raise HTTPException(status_code=404, detail=f"La carta {movimiento.idCarta} no está en tu mano")

        tablero = partida.tablero
        movimiento_bd = db_service.obtener_movimiento_bd(movimiento.idCarta, db)
        carta_movimiento = movimiento_bd.mov.value
        
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
        db_service.eliminar_carta_movimiento(id_partida, id_jugador, movimiento.idCarta, db)

        # Cambiar las posiciones de las fichas
        ficha1 = db_service.obtener_ficha(tablero.id_partida, posicion_1[0], posicion_1[1], db)
  
        ficha2 = db_service.obtener_ficha(tablero.id_partida, posicion_2[0], posicion_2[1], db)

        db_service.swapear_color_fichas(ficha1, ficha2, db)                
        
        response = {"type": "MovimientoParcial", 
                    "carta": {"id": movimiento.idCarta, "movimiento": carta_movimiento}, 
                    "fichas": [{"x": ficha2.x, "y": ficha2.y, "color": ficha2.color.name}, 
                               {"x": ficha1.x, "y": ficha1.y, "color": ficha1.color.name}]
                    }
                
        db_service.crear_movimiento_parcial(id_partida, id_jugador, movimiento.idCarta,
                                            ficha1.x, ficha1.y, ficha2.x, ficha2.y, db)
             
        return response
    
    async def declarar_figura(self, id_partida: int, id_jugador: int, figura: DeclararFiguraRequest, db: Session):
        partida = db_service.obtener_partida(id_partida, db)
        if not partida.activa:
            raise HTTPException(status_code=404, detail="La partida no ha sido iniciada")
        
        if not pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail="El jugador no pertenece a la partida")
    
        if not db_service.obtener_todas_figuras_en_mano(id_partida, db):
            raise HTTPException(status_code=431, detail=f"La carta {figura.idCarta} no está en ninguna mano")

        # Validar la figura
        figura_db = db_service.obtener_figura(figura.idCarta, db)
        carta_figura = figura_db.fig.value
        if not carta_figura == figura.tipo_figura:
            raise HTTPException(status_code=432, detail="Figura inválida")
        
        esta_en_mano = db_service.obtener_figura_en_mano(id_partida, id_jugador, figura.idCarta, db)
        if esta_en_mano:
            # Descartar una figura propia
            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == id_jugador,
                                             CartasFigura.carta_fig == figura.idCarta).first().bloqueada:
                raise HTTPException(status_code=433, detail="No puedes descartar una figura bloqueada")
            
            # Descartar la carta y desbloquear si es necesario
            response = self.completar_figura(id_partida, None, id_jugador, figura, "descartar", db)
            db.commit()
            return response
        else:   
            # Bloquear una figura
            jugador_a_bloquear = db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida, 
                                                       CartasFigura.carta_fig == figura.idCarta).first().id_jugador
            
            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == jugador_a_bloquear,
                                             CartasFigura.carta_fig == figura.idCarta).first().bloqueada:
                raise HTTPException(status_code=434, detail="Figura ya bloqueada")
            
            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == jugador_a_bloquear).count() == 1:
                raise HTTPException(status_code=435, detail="No puedes bloquear un jugador con una sola carta de figura")

            if db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                             CartasFigura.id_jugador == jugador_a_bloquear,
                                             CartasFigura.bloqueada == True).count() == 1:
                raise HTTPException(status_code=436, detail="No puedes bloquear 2 cartas de un mismo jugador")
            
            # Bloquear la carta
            response = self.completar_figura(id_partida, jugador_a_bloquear, id_jugador, figura, "bloquear", db)
            db.commit()
            return response

    def deshacer_movimiento(self, idPartida: int, idJugador: int, db: Session):
        
        ultimo_movimiento_parcial = db_service.obtener_ultimo_movimiento_parcial(idPartida, idJugador, db)

        if ultimo_movimiento_parcial is None:
            raise HTTPException(status_code=404, detail=f"El jugador con id {idJugador} no realizo ningun movimiento ")
                
        movimiento = obtener_movimiento(ultimo_movimiento_parcial.movimiento, db)
        
        carta_movimiento = db_service.obtener_movimiento(idPartida, idJugador, ultimo_movimiento_parcial.movimiento, db)
        
        db_service.setear_carta_movimiento(carta_movimiento, db)
              
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
        
        movimientos = db_service.obtener_movimientos_en_mano(idPartida, idJugador, db)
        
        movimientos_en_mano = len(movimientos)

        movimientos_parciales = db_service.obtener_movimientos_parciales(idPartida, idJugador, db)
        
        
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
        
        
        movimientos_a_devolver = max(0, 3 - movimientos_en_mano)
        
        asignacion = asignar_cartas_movimientos(idPartida, idJugador, movimientos_a_devolver, db)
        
    
        while len(cartas) != movimientos_a_devolver:            
            movimiento = db_service.obtener_movimiento(idPartida, idJugador, asignacion[0]['id'], db)
            db_service.setear_carta_movimiento(movimiento, db)
                        
            cartas.append(asignacion[0])
            asignacion.pop(0)
        
        
        resultado = {
            "cartas": cartas,
            "cantMovimientosDesechos": cantidad_mov_deshechos,
            "posiciones": posiciones
        }    
    
        return  resultado     

juego_service = JuegoService()