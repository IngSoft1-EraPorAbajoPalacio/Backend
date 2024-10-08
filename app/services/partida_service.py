from app.schema.partida_schema import *
from typing import List
from fastapi import HTTPException
import uuid
from sqlalchemy.orm import Session
from app.db.models import Partida,Jugador_Partida
from sqlalchemy.exc import *
from app.services.jugador_service import *
from app.services.ficha_service import * 
from app.services.cartas_service import *
from app.schema.websocket_schema import EliminarPartidaDataSchema, EliminarPartidaSchema
from app.routers.websocket_manager import manager

class PartidaService:
    
    def __init__(self):
        self.partidas = {}
        
    def esta_iniciada(self, id_partida: int, db: Session) -> bool:
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        return partida.activa
    
    
    def pertenece(self, id_partida: int, id_jugador: int, db: Session) -> bool:
        id_jugadores = self.obtener_id_jugadores(id_partida, db)
        return id_jugador in id_jugadores
    
     
    def obtener_id_jugadores(self,id_partida:int,db : Session):
        partida = self.obtener_partida(id_partida,db)
        return [jugador.id_jugador for jugador in partida.jugadores]  
       
     
    def obtener_cartas_figuras(self, id_jugador:int,id_partida:int, db: Session):
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        """
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        cartas_figuras = []        
        for carta in jugador.cartas_de_figuras:
            figura = carta.figura
            cartas_figuras.append({
                "idJugador": id_jugador,
                "nombreJugador": jugador.nickname,
                "cartas": [{"id": figura.id, "figura": int(figura.fig.name)}]
                #"idFigura": figura.id,
                #"figura":int(figura.fig.name)
            })
           """
        cartas_figura = []
        for jugador in partida.jugadores:
            jugador_data = {
                "idJugador": jugador.id_jugador,
                "nombreJugador": jugador.jugador.nickname,
                "cartas": [
                    {"id": carta.id, "figura": carta.figura.fig.name} 
                    for carta in jugador.jugador_fig.cartas_de_figuras
                ]
        }
        cartas_figura.append(jugador_data)
        return cartas_figura
          
     
     
    def obtener_cartas_movimientos(self, id_jugador: int, db: Session):
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        cartas_movimientos = []
        
        for carta in jugador.cartas_de_movimientos:
            movimiento = carta.movimiento
            cartas_movimientos.append({
                #"idJugador": id_jugador,
                #"nombreJugador": jugador.nickname,
                "id": movimiento.id,
                "movimiento":movimiento.mov.name
            })
        return cartas_movimientos   
   

        
    def obtener_jugadores(self,id_partida:int,db : Session):
        partida = self.obtener_partida(id_partida,db)
        jugadores = [jugador.jugador for jugador in partida.jugadores]
        return jugadores
    
    
    def obtener_cantidad_jugadores(self, id_partida: int, db: Session):
        partida = self.obtener_partida(id_partida, db)
        return len(partida.jugadores)
        
 
    def obtener_partida_particular(self, id_partida: int, db: Session):
       partida = db.query(Partida).filter(Partida.id == id_partida).first()
       if partida is None:
           raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")
       return PartidaResponse(
           id_partida=str(id_partida),
           nombre_partida=partida.nombre,
           cant_jugadores=str(len(partida.jugadores))
       )
 
 
    async def crear_partida(self, partida: CrearPartida, db: Session):
        owner = crear_jugador(partida.nombre_host, db)
        partida_creada = Partida(
            nombre=partida.nombre_partida,
            min=partida.cant_min_jugadores,
            max=partida.cant_max_jugadores,
            id_owner=owner.id
        )
        try:
            db.add(partida_creada)
            db.commit()
        except SQLAlchemyError as e:
            print(str(e))

        nuevo_jugador_partida = Jugador_Partida(
            id_jugador=owner.id,
            id_partida=partida_creada.id
        )
        db.add(nuevo_jugador_partida)
        db.commit()
        
        return CrearPartidaResponse(
            id_partida=str(partida_creada.id),
            nombre_partida=partida_creada.nombre,
            id_jugador=str(owner.id)
        ) 
         
    
    def obtener_partida(self, id_partida: int, db: Session):
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        if partida is None:
            raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")
        return partida

    
    def listar_partidas(self, db: Session):
        partidas = db.query(Partida).all()
        if not partidas:
            return []
        return [
            PartidaResponse(
                id_partida=str(partida.id),
                nombre_partida=partida.nombre,
                cant_min_jugadores=partida.min, 
                cant_max_jugadores=partida.max
            ) for partida in partidas
        ]       
    
    async def unirse_partida(self, id_partida: str, nombre_jugador: str, db: Session) -> UnirsePartidaResponse:
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        if not partida:
            raise HTTPException(status_code=404, detail=f"No existe partida con id {id_partida}")
        
        if len(partida.jugadores) >= partida.max:
            raise HTTPException(status_code=404, detail="La partida está llena")
        
        jugador_a_unirse = crear_jugador(nombre=nombre_jugador, db=db)
        agregar_jugador = Jugador_Partida(
            id_jugador=jugador_a_unirse.id,
            id_partida=id_partida
        )
        db.add(agregar_jugador)
        db.commit()

        return UnirsePartidaResponse(idJugador=jugador_a_unirse.id)
    

    async def iniciar_partida(self, id_partida: int, id_jugador: int, db: Session) -> IniciarPartidaResponse:
        if not self.pertenece(id_partida, id_jugador, db):
            raise HTTPException(status_code=404, detail=f"El jugador {id_jugador} no pertenece a la partida")

        if not db.query(Partida).filter(Partida.id_owner == id_jugador).first():
            raise HTTPException(status_code=404, detail="Solo el owner puede iniciar la partida")

        if self.obtener_cantidad_jugadores(id_partida, db) == 1:
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
        jugadores = [jugador.jugador for jugador in partida.jugadores]
        for jugador in jugadores:
            jugador.jugando = True
            
        db.commit()
        

        cartas_movimientos = self.obtener_cartas_movimientos(id_jugador, db)
        #cartas_figuras = self.obtener_cartas_figuras(id_jugador,id_partida, db)
        cartas_figuras = [{"id": 1, "figura": 1},{"id": 2, "figura": 2}, {"id": 3, "figura": 3}]
        fichas = obtener_fichas(id_partida, db)
        orden = self.obtener_id_jugadores(id_partida, db)
        resultado = {
            "type": "IniciarPartida",
            "fichas": fichas, 
            "orden": orden,
            "cartasMovimiento": cartas_movimientos,  
            "cartasFigura": cartas_figuras   
        } 
        return resultado
    
    
    '''''
    def pasar_turno(self, id_partida: int, db: Session):  
        partida = self.obtener_partida(id_partida,db)  
        tablero = partida.tablero
        turno_actual = tablero.turno

        id_jugadores = [jugador.id_jugador for jugador in partida.jugadores]
        cantidad_jugadores = len(id_jugadores)
        
        turno_nuevo = (id_jugadores.index(turno_actual) + 1) % cantidad_jugadores
        tablero.turno = id_jugadores[turno_nuevo]

        db.commit()
        
        return PasarTurnoResponse(id_turno = tablero.turno)      
    ''' 
   

    async def abandonar_partida(self,id_partida:int,id_jugador:int,db:Session):
    
        try:
            print(f"Attempting to remove player {id_jugador} from game {id_partida}")

            partida = self.obtener_partida(id_partida, db)
            if not partida:
                raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")

            jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
            if not jugador:
                raise HTTPException(status_code=404, detail=f"No existe ningún jugador con id {id_jugador}")

            jugador_partida = db.query(Jugador_Partida).filter_by(id_partida=id_partida, id_jugador=id_jugador).first()
            if not jugador_partida:
                raise HTTPException(status_code=404, detail=f"El jugador {id_jugador} no está en la partida {id_partida}")

            cantidad_jugadores = self.obtener_cantidad_jugadores(id_partida, db)
            print(f"Cantidad de jugadores: {cantidad_jugadores}")

            if partida.activa:
                if cantidad_jugadores == 2:
                    await self.eliminar_partida(id_partida, db)  # Elimina partida si quedan 2 jugadores y uno abandona
                    return {"partida_eliminada": True}                    
                else:
                    db.delete(jugador_partida)
            else:
                if cantidad_jugadores > 1 and id_jugador != partida.id_owner:
                    db.delete(jugador_partida)
                else:
                    await self.eliminar_partida(id_partida, db)  # Elimina si el owner abandona antes de comenzar
                    return {"partida_eliminada": True}

            jugador.jugando = False
            db.commit()
            print(f"Successfully removed player {id_jugador} from game {id_partida}")
            return {"message": f"Jugador {id_jugador} ha abandonado la partida {id_partida}"}

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

            # Eliminar las cartas de figuras asociadas a la partida
            db.query(CartasFigura).filter(CartasFigura.id_partida == id_partida).delete()

            # Eliminar las cartas de movimientos asociadas a la partida
            db.query(CartaMovimientos).filter(CartaMovimientos.id_partida == id_partida).delete()

            # Obtener los tableros y eliminar las fichas asociadas
            tableros = db.query(Tablero).filter(Tablero.id_partida == id_partida).all()
            for tablero in tableros:
                db.query(Ficha).filter(Ficha.id_tablero == tablero.id).delete()

            # Eliminar los tableros asociados a la partida
            db.query(Tablero).filter(Tablero.id_partida == id_partida).delete()

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