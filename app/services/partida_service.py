from app.schema.partida_schema import *
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.models import Partida, Jugador_Partida
from sqlalchemy.exc import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *

class PartidaService:
    
    def _init_(self):
        self.partidas_lobby = []
        self.partidas_iniciadas = []
        
    def obtener_partidas(self, db: Session):
        partidas = db.query(Partida).filter(Partida.activa == False).all()
        if not partidas:
            return []
        return partidas 
    
    def obtener_partida(self, id_partida: int, db: Session):        
        print(id_partida)
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        if partida is None:
            raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}, error 1")
        return partida
               
    def obtener_jugadores(self, id_partida: int, db: Session):
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        if partida is None:
            raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")
        return [jugador.jugador for jugador in partida.jugadores]
        
    def esta_iniciada(self, id_partida: int, db: Session) -> bool:
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        return partida.activa  
    
    def pertenece(self, id_partida: int, id_jugador: int, db: Session) -> bool:
        return id_jugador in obtener_id_jugadores(id_partida, db)
    
    async def crear_partida(self, partida: CrearPartida, db: Session):
        if(partida.cant_max_jugadores < 2):
            raise HTTPException(status_code=404, detail="La cantidad máxima de jugadores debe ser mayor o igual a 2")
        if(partida.cant_min_jugadores < 2):
            raise HTTPException(status_code=404, detail="La cantidad mínima de jugadores debe ser mayor o igual a 2")
        if(partida.cant_max_jugadores < partida.cant_min_jugadores):
            raise HTTPException(status_code=404, detail="La cantidad máxima de jugadores debe ser mayor o igual a la cantidad mínima de jugadores")
        
        owner = crear_jugador(partida.nombre_host, db)
        
        partida_creada = Partida(
            nombre=partida.nombre_partida,
            min=partida.cant_min_jugadores,
            max=partida.cant_max_jugadores,
            id_owner=owner.id
        )
        db.add(partida_creada)
        db.commit()
        
        try:
            jugador_partida = Jugador_Partida(
                id_jugador=owner.id,
                id_partida=partida_creada.id
            )
                                
            db.add(jugador_partida)
            db.commit()
        except SQLAlchemyError as e:
            db.rollback() 
            print(e)
               
        return CrearPartidaResponse(
            id_partida=str(partida_creada.id),
            nombre_partida=partida_creada.nombre,
            id_jugador=str(owner.id)
        )                
                    
    async def unirse_partida(self, id_partida: str, nombre_jugador: str, db: Session) -> UnirsePartidaResponse:
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        
        if not partida:
            raise HTTPException(status_code=404, detail=f"No existe partida con id {id_partida}")
        
        if len(partida.jugadores) >= partida.max:
            raise HTTPException(status_code=404, detail="La partida está llena")
        
        if(self.esta_iniciada(id_partida, db)):
            raise HTTPException(status_code=404, detail=f"No se puede unir a una partida en progreso")

        jugador_a_unirse = crear_jugador(nombre=nombre_jugador, db=db)
        agregar_jugador = Jugador_Partida(
            id_jugador=jugador_a_unirse.id,
            id_partida=id_partida
        )
        try:
            db.add(agregar_jugador)
            db.commit()
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
        if not self.pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail=f"El jugador {id_jugador} no pertenece a la partida")

        if not db.query(Partida).filter(Partida.id_owner == id_jugador).first():
            raise HTTPException(status_code=404, detail="Solo el owner puede iniciar la partida")

        if obtener_cantidad_jugadores(id_partida, db) == 1:
            raise HTTPException(status_code=404, detail="No puedes iniciar la partida con menos de 2 jugadores")

        partida = self.obtener_partida(id_partida, db)

        if partida.activa:
            raise HTTPException(status_code=404, detail=f"La partida {id_partida} ya está iniciada")

        crear_tablero(id_partida, db)
        repartir_fichas(id_partida, db)
        
        inicializacion_figuras_db(db)
        inicializacion_movimientos_db(db)
        
        repartir_cartas_movimientos(id_partida, db)
        repartir_cartas_figuras(id_partida, db)

        partida.activa = True
        db.commit()
        
        jugadores = obtener_jugadores(id_partida, db)
        for jugador in jugadores:
            jugador.jugando = True
            
        db.commit()        
        
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
    
    def pasar_turno(self, id_partida: int, id_jugador, db: Session):  
        partida = self.obtener_partida(id_partida,db)  
        tablero = partida.tablero
        turno_actual = id_jugador

        id_jugadores = [jugador.id_jugador for jugador in partida.jugadores]
        cantidad_jugadores = len(id_jugadores)
        
        turno_nuevo = (id_jugadores.index(turno_actual) + 1) % cantidad_jugadores
        tablero.turno = id_jugadores[turno_nuevo]

        db.commit()
        
        return tablero.turno       

    async def abandonar_partida(self,id_partida:int,id_jugador:int,db:Session):
    
        try:
            partida = self.obtener_partida(id_partida, db)
            if not partida:
                raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")

            jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
            if not jugador:
                raise HTTPException(status_code=404, detail=f"No existe ningún jugador con id {id_jugador}")

            jugador_partida = db.query(Jugador_Partida).filter_by(id_partida=id_partida, id_jugador=id_jugador).first()
            if not jugador_partida:
                raise HTTPException(status_code=404, detail=f"El jugador {id_jugador} no está en la partida {id_partida}")

            cantidad_jugadores = obtener_cantidad_jugadores(id_partida, db)

            if partida.activa:
                if cantidad_jugadores == 2:
                    await self.eliminar_partida(id_partida, db)
                else:
                    db.delete(jugador_partida)
                    db.commit()
            else:
                if cantidad_jugadores > 1 and id_jugador != partida.id_owner:
                    db.delete(jugador_partida)
                else:
                    await self.eliminar_partida(id_partida, db)  # Elimina si el owner abandona antes de comenzar

            jugador.jugando = False
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
            # Obtener la partida
            partida = db.query(Partida).filter(Partida.id == id_partida).first()

            if not partida:
                raise HTTPException(status_code=404, detail="Partida no encontrada")

            # Eliminar las fichas asociadas a los tableros de la partida
            tableros = db.query(Tablero).filter(Tablero.id_partida == id_partida).all()
            for tablero in tableros:
                db.query(Ficha).filter(Ficha.id_tablero == tablero.id).delete()

            # Eliminar los tableros  y las cartas asociadas a la partida
            db.query(Tablero).filter(Tablero.id_partida == id_partida).delete()
            db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida).delete()
            db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == id_partida).delete()

            # Eliminar los jugadores asociados a la partida
            db.query(Jugador_Partida).filter(Jugador_Partida.id_partida == id_partida).delete()

            # Finalmente, eliminar la partida
            db.delete(partida)

            # Confirmar los cambios en la base de datos
            db.commit()

        except Exception as e:
            db.rollback()  # Deshacer los cambios en caso de error
            raise HTTPException(status_code=500, detail=f"Error eliminando la partida: {str(e)}")
        
partida_service = PartidaService()