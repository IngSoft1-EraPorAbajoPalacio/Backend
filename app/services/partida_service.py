from schema.partida_schema import *
from typing import List
from fastapi import HTTPException
import uuid
from sqlalchemy.orm import Session
from db.models import Partida,Jugador_Partida
from sqlalchemy.exc import *
from services.jugador_service import *
from services.ficha_service import * 
from services.cartas_service import inicializacion_figuras_db,inicializacion_movimientos_db,repartir_cartas_figuras, repartir_cartas_movimientos


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
       
     
    def cartas_jugador(self, id_jugador: int, db: Session):
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        list_cartas_figuras = []
        list_cartas_movimientos = []
        
        print(f"El jugar con id {id_jugador} tiene las siguientes cartas de figuras :")
        for carta in jugador.cartas_de_figuras:
            figura = carta.figura
            list_cartas_figuras.append({
                "id_jugador": id_jugador,
                "nombre_jugador": jugador.nickname,
                "id_figura": figura.id,
                "figura":figura.fig.name
            })
            
        print(f"El jugar con id {id_jugador} tiene las siguientes cartas de movimientos :")
        for carta in jugador.cartas_de_movimientos:
            list_cartas_movimientos.append({
                "id_jugador": id_jugador,
                "nombre_jugador": jugador.nickname,
                "id_movimiento": carta.movimiento.id,
                "figura": carta.movimiento.mov.name
            })
        
        print(list_cartas_figuras)  
        print(list_cartas_movimientos)    
            
        
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
 
 
    def crear_partida(self, partida: CrearPartida, db: Session):
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
            raise HTTPException(status_code=404, detail="No existe ninguna partida")
        return [
            PartidaResponse(
                id_partida=str(partida.id),
                nombre_partida=partida.nombre,
                cant_jugadores=str(len(partida.jugadores))
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
    

    def iniciar_partida(self, id_partida: int, id_jugador: int, db: Session) -> InicarPartidaResponse:
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

        return InicarPartidaResponse(id_partida=str(partida.id))
    
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

    def abandonar_partida(self,id_partida:int,id_jugador:int,db:Session):
    
        partida = self.obtener_partida(id_partida,db)
        cantidad_jugadores = self.obtener_cantidad_jugadores(id_partida,db)
        print(cantidad_jugadores)
        
        #si cant jug == 2 debo eliminar todo lo relacionado a la partida
        if cantidad_jugadores == 2:
            db.delete(partida)
            db.commit()
            
        #en el caso que sean 3 o 4 solo elimino ese jugador y los datos relacionados a él

#Crea una instancia del servicio que se utilizará en el router.
partida_service = PartidaService()