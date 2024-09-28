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
        
     
    def cartas_jugador(self,id_jugador : int,db : Session):
        jugador = db.query(Jugador).filter(Jugador.id == id_jugador).first()
        cartas_figuras = jugador.cartas_de_figuras
        for carta in cartas_figuras:
            figurax = carta.figura
            print(f"id de figura : {figurax.id}, Figura : {figurax.fig}")
    
     
        
    def obtener_jugadores(self,id_partida:int,db : Session):
        partida = self.obtener_partida(id_partida,db)
        jugadores = [jugador.jugador for jugador in partida.jugadores]
        return jugadores
 
 
 
    def obtener_partida_particular(self,id_partida:int, db:Session):
      partida = db.query(Partida).filter(Partida.id == id_partida).first()
      if partida is None:
          raise HTTPException(status_code="404", detail=f"No existe ninguna partida con id {id_partida}")
      return PartidaResponse(id_partida = str(id_partida), nombre_partida=partida.nombre,
                             cant_jugadores=str(len(partida.jugadores))) 

        

    def crear_partida(self, partida: CrearPartida, db : Session):

        owner = crear_jugador(partida.nombre_host,db)
        
        partida_creada = Partida(nombre = partida.nombre_partida,
                             min=partida.cant_min_jugadores,
                             max=partida.cant_max_jugadores,
                             id_owner = owner.id)

        try:
            db.add(partida_creada)
            db.commit()
        except SQLAlchemyError as e : 
            print(str(e))

        nuevo_jugador_partida = Jugador_Partida(
                                id_jugador=owner.id,
                                id_partida= partida_creada.id)    
        
        db.add(nuevo_jugador_partida)
        db.commit()
        
        return CrearPartidaResponse(id_partida = str(partida_creada.id), nombre_partida = partida_creada.nombre,id_jugador=str(owner.id))
        

   
    
    def obtener_partida(self,id_partida:int, db:Session):
        resultado = db.query(Partida).filter(Partida.id == id_partida).first()
        if resultado is None:
            raise HTTPException(status_code="404", detail=f"No existe ninguna partida con id {id_partida}")
        return resultado 

    
    
    
    def listar_partidas(self,db :Session):
            partidas = db.query(Partida).all()
            if not partidas:
                raise HTTPException(status_code=404, detail="No existe niguna partida")
            return [PartidaResponse(id_partida = str(partida.id), nombre_partida= partida.nombre,
                                    cant_jugadores=str(len(partida.jugadores))) for partida in partidas]
         
         
    
    
         
    async def unirse_partida(self, id_partida: str, nombre_jugador: str, db:Session) -> UnirsePartidaResponse:
    
        partida_obtenida = db.query(Partida).filter(Partida.id == id_partida).first()
        if partida_obtenida is None:
            raise HTTPException(status_code=404,detail=f"No existe partida con id {id_partida}")
        
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        cantidad_jugadores = len(partida.jugadores)

        if (cantidad_jugadores >= partida.max) :
            raise HTTPException(status_code=404, detail=f"La partida está llena mami")
        
        jugador_a_unirse = crear_jugador(nombre=nombre_jugador, db=db)


        agregar_jugador = Jugador_Partida(id_jugador = jugador_a_unirse.id,
                                         id_partida = id_partida)

        db.add(agregar_jugador)
        db.commit()

        return UnirsePartidaResponse(idJugador=jugador_a_unirse.id)   
       
       

    def iniciar_partida(self, id_partida:int, id_jugador:int , db : Session) -> InicarPartidaResponse:

        is_owner = db.query(Partida).filter(Partida.id_owner == id_jugador).first()

        if (is_owner is None):
            raise HTTPException(status_code=404, detail="Solo puede iniciar la partida el owner")


        partida = self.obtener_partida(id_partida,db)

        if(partida.activa):
            raise HTTPException(status_code=404, detail=f"La partida con id : {id_partida} ya esta iniciada")

        crear_tablero(id_partida,db)
        repartir_fichas(id_partida, db)

      
        inicializacion_figuras_db(db)        
        inicializacion_movimientos_db(db)
        
        
        #reparticas cartas de figuras
        
        #repartir_cartas_movimientos(id_partida,db)    
        #repartir_cartas_figuras(id_partida,db) 
               
        partida.activa = True
        
        
        jugadores = [jugador.jugador for jugador in partida.jugadores]
        for jugador in jugadores:
            jugador.jugando = True
        
        db.commit()
       
        
        #self.cartas_jugador(id_jugador,db)

        return InicarPartidaResponse(id_partida=str(partida.id))
    
    
    
    
  
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    """
    def abandonar_partida(self, id_partida:int, id_jugador:int , db : Session):
        
        #me fijo si la partida existe
        partida = self.obtener_partida(id_partida,db)
        
        # me fijo si el jugador esta en esa partida
        jugadores = self.obtener_jugadores(id_partida,db)

        
        
        #elimino el jugador de la partida, y todo lo que tenga que ver con sus cartas, fichas,etc
        
       
       
       
       return 
       """ 
        
        
        
        
        
        
    

#Crea una instancia del servicio que se utilizará en el router.
partida_service = PartidaService()