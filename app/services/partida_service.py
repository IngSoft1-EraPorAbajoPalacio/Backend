from schema.partida_schema import *
from typing import List
from fastapi import HTTPException
import uuid
from sqlalchemy.orm import Session
from db.models import Partida,Jugador_Partida
from sqlalchemy.exc import *
from services.jugador_service import *
from services.ficha_service import * 
from services.cartas_service import *


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
        cartas_figuras = [{"id": 1, "figura":"f1"},{"id": 2, "figura":"f2"}, {"id": 3, "figura":"f3"}]
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
    
        partida = self.obtener_partida(id_partida,db)
        cantidad_jugadores = self.obtener_cantidad_jugadores(id_partida,db)
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()       
        
        if (partida.activa):
            if(cantidad_jugadores == 2):
                db.delete(partida)
            else:
                db.delete(jugador)
        else:
            if cantidad_jugadores > 1:
                db.delete(jugador)   
            else:
                db.delete(partida)
                    
        db.commit()
        

partida_service = PartidaService()