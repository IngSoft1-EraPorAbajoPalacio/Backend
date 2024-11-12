from app.schema.partida_schema import *
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *
from app.services.bd_service import *

class PartidaService:
    
    async def crear_partida(self, partida: CrearPartida, db: Session):
                
        try:
            owner = db_service.crear_jugador(partida.nombre_host, db)
            partida_creada = db_service.crear_partida(
                partida.nombre_partida,
                partida.cant_min_jugadores,
                partida.cant_max_jugadores,
                owner.id,
                partida.contrasena,
                db
            )

            db_service.crear_jugador_partida(owner.id, partida_creada.id, db)
    
        except SQLAlchemyError as e:
            db.rollback() 
            print(e)
               
        return CrearPartidaResponse(
            id_partida=str(partida_creada.id),
            nombre_partida=partida_creada.nombre,
            id_jugador=str(owner.id)
        )             
                            
    async def unirse_partida(self, id_partida: str, nombre_jugador: str, contrasena: str, db: Session) -> UnirsePartidaResponse:
        
        partida = db_service.obtener_partida(int(id_partida), db)
                
        if not partida:
            raise HTTPException(status_code=404, detail=f"No existe partida con id {id_partida}")
        
        if len(partida.jugadores) >= partida.max:
            raise HTTPException(status_code=404, detail="La partida está llena")
        
        if (db_service.partida_iniciada(int(id_partida), db)):
            raise HTTPException(status_code=404, detail=f"No se puede unir a una partida en progreso")
        
        if (db_service.obtener_contraseña(id_partida, db) !=  contrasena):
            raise HTTPException(status_code=401, detail=f"La contraseña es incorrecta")

        jugador_a_unirse = crear_jugador(nombre_jugador, db)

        try:
            db_service.crear_jugador_partida(jugador_a_unirse.id, id_partida, db)      
            
        except SQLAlchemyError as e:
            db.rollback()
            print(f"Error al unirse a la partida: {e}")
            
        return UnirsePartidaResponse(
            idJugador=str(jugador_a_unirse.id),
            unidos=[
                JugadorListado(id=str(jugador.jugador.id), nombre=jugador.jugador.nickname)
                for jugador in partida.jugadores
            ]
        )


    async def iniciar_partida(self, id_partida: int, id_jugador: int, db: Session):
        if not pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail=f"El jugador {id_jugador} no pertenece a la partida")

        if not db_service.obtener_partida_owner(id_jugador, db):
            raise HTTPException(status_code=404, detail="Solo el owner puede iniciar la partida")

        if obtener_cantidad_jugadores(id_partida, db) == 1:
            raise HTTPException(status_code=404, detail="No puedes iniciar la partida con menos de 2 jugadores")

        if db_service.partida_iniciada(id_partida, db):
            raise HTTPException(status_code=404, detail=f"La partida {id_partida} ya está iniciada")

        db_service.crear_tablero(id_partida, db)
        repartir_fichas(id_partida, db)
        
        inicializacion_figuras_db(db)
        inicializacion_movimientos_db(db)
        
        repartir_cartas_movimientos(id_partida, db)
        repartir_cartas_figuras(id_partida, db)

        db_service.setear_partida_activa(id_partida, db)
        db_service.setear_jugadores_jugando(id_partida, db)  
        
        cartas_movimientos = obtener_cartas_movimientos(id_partida, db)
        cartas_figuras = obtener_cartas_figuras(id_partida, db)
        fichas = fichas_service.obtener_fichas(id_partida, db)
        orden = obtener_id_jugadores(id_partida, db)
        
        response = {
            "type": "IniciarPartida",
            "fichas": fichas, 
            "orden": orden,
            "cartasMovimiento": cartas_movimientos,  
            "cartasFigura": cartas_figuras   
        } 
        
        return response
    
    
    def pasar_turno(self, id_partida: int, id_jugador: int, db: Session):  
        partida = db_service.obtener_partida(id_partida,db) 
        
        if partida is None:
            print("la partida no existe")
            
        jugador = db_service.obtener_jugador(id_jugador, db)
        
        if jugador is None :
            print(f"el jugador con id {id_jugador} no pertenece a la partida")
                
        tablero = partida.tablero
        turno_actual = id_jugador

        id_jugadores = obtener_id_jugadores(id_partida, db)
        cantidad_jugadores = len(id_jugadores)
        
        turno_nuevo = (id_jugadores.index(turno_actual) + 1) % cantidad_jugadores
        tablero.turno = id_jugadores[turno_nuevo]

        return tablero.turno       


    async def abandonar_partida(self, id_partida: int, id_jugador: int, db: Session):
    
        try:
            partida = db_service.obtener_partida(id_partida, db)
            if not partida:
                raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")

            jugador = db_service.obtener_jugador(id_jugador, db)
            if not jugador:
                raise HTTPException(status_code=404, detail=f"No existe ningún jugador con id {id_jugador}")

            jugador_partida = db.query(Jugador_Partida).filter(Jugador_Partida.id_partida == id_partida).all()

            cantidad_jugadores = obtener_cantidad_jugadores(id_partida, db)

            if partida.activa:
                if cantidad_jugadores == 2:
                    
                    jugadores = obtener_jugadores(id_partida, db)
                    
                    if (jugador_partida):
                        for jp in jugador_partida:
                            db.delete(jp)
                    db.commit()        
                    
                    tablero = db_service.obtener_tablero(id_partida, db)
                    if tablero is None:
                        raise HTTPException(status_code=404, detail=f"abandonar No existe tablero asociado a id : {id_partida}")

                    db.query(Ficha).filter(Ficha.id_tablero == tablero.id_partida).delete()

                    # Eliminar los tableros  y las cartas asociadas a la partida
                    db.query(Tablero).filter(Tablero.id_partida == id_partida).delete()
                    db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida).delete()
                    db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == id_partida).delete()

                    for jugador in jugadores:
                        db.delete(jugador)
                    
                    db.delete(partida)
                    
                else:
                    db.query(Jugador_Partida).filter(Jugador_Partida.id_jugador == id_jugador,
                                                     Jugador_Partida.id_partida == id_partida).delete()
                    
                    tablero = db.query(Tablero).filter(Tablero.id_partida == id_partida).first()

                    if tablero is None:
                        raise HTTPException(status_code=404, detail=f"abandonar No existe tablero asociado a id : {id_partida}")

                    db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida,
                                                  CartasFigura.id_jugador == id_jugador).delete()
                    db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == id_partida,
                                                      CartaMovimientos.id_jugador == id_jugador).delete()
                    db.delete(jugador)

            else:
                if cantidad_jugadores > 1 and id_jugador != partida.id_owner:
                    
                    db.query(Jugador_Partida).filter(
                        Jugador_Partida.id_jugador == id_jugador,
                        Jugador_Partida.id_partida == id_partida
                    ).delete()
                    
                    db.delete(jugador)
                else:
                    await self.eliminar_partida(id_partida, db)  # Elimina si el owner abandona antes de comenzar
            db.commit()

        except SQLAlchemyError as e:
            db.rollback()
            print(f"Database error: {str(e)}")
            raise HTTPException(status_code=500, detail="Database error occurred")
        except HTTPException as he:
            print(f"HTTP error: {str(he)}")
            raise he
        except Exception as e:
            db.rollback()
            print(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")


    async def eliminar_partida(self, id_partida: int, db: Session):
        try:
            partida = db_service.obtener_partida(id_partida, db)
            if not partida:
                raise HTTPException(status_code=404, detail="Partida no encontrada")
                        
            # Eliminar los jugadores asociados a la Partida
            db.query(Jugador_Partida).filter(Jugador_Partida.id_partida == id_partida).delete()
                
            #elimino la tabla jugadores
            jugadores = obtener_jugadores(id_partida, db)
            for jugador in jugadores:
                db.delete(jugador)            
                
            # Finalmente, eliminar la partida
            db.delete(partida)

            # Confirmar los cambios en la base de datos
            db.commit()

        except Exception as e:
            db.rollback()  # Deshacer los cambios en caso de error
            raise HTTPException(status_code=500, detail=f"Error eliminando la partida: {str(e)}")
        
partida_service = PartidaService()