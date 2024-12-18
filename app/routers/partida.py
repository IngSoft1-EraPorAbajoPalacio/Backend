from fastapi import APIRouter, HTTPException, Depends
from app.schema.partida_schema import * 
from app.services.partida_service import partida_service
from app.services.jugador_service import *
from app.services.cartas_service import *
from app.db.base import crear_session
from sqlalchemy.orm import Session
from app.routers.websocket_manager import manager
from app.routers.websocket_manager_game import manager_game
from app.routers.websocket_manager_lobby import manager_lobby
from app.schema.websocket_schema import * 
from typing import List
import logging
from app.services.encontrar_fig import computar_y_enviar_figuras
import  asyncio
from app.services.timer import timer

router = APIRouter()

@router.get("/partidas/{id}", response_model=PartidaResponse)
def obtener_partida(id_partida: int, db: Session = Depends(crear_session)):
    try:
        partida = db_service.obtener_partida(id_partida, db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))    

    return PartidaResponse(
        id_partida=str(id_partida),
        nombre_partida=partida.nombre,
        cant_min_jugadores= partida.min,
        cant_max_jugadores= partida.max,
        privada=True if partida.contrasena else False
    )    

@router.post("/partida", response_model=CrearPartidaResponse, status_code=201)
async def crear_partida(partida: CrearPartida, db: Session = Depends(crear_session)):
    try:
        partida_creada = await partida_service.crear_partida(partida, db)
        agregar_partida_message = AgregarPartidaSchema(
            type=WebSocketMessageType.AGREGAR_PARTIDA,
            data=AgregarPartidaDataSchema(
                idPartida=int(partida_creada.id_partida),
                nombrePartida=partida.nombre_partida,
                cantJugadoresMin=partida.cant_min_jugadores,
                cantJugadoresMax=partida.cant_max_jugadores,
                privada= True if partida.contrasena else False  
            )
        )
        await manager.broadcast(agregar_partida_message.model_dump())
        return partida_creada    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=201)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest, db: Session = Depends(crear_session)):
    try:
        response = await partida_service.unirse_partida(idPartida, request.nombreJugador, request.contrasena, db)
        jugadores = obtener_jugadores(int(idPartida), db)

        lista_jugadores = [
            JugadorSchema(id=j.id, nombre=j.nickname) for j in jugadores
        ]
        jugador_unido_message = JugadorUnidoSchema(
            type=WebSocketMessageType.JUGADOR_UNIDO,
            ListaJugadores=lista_jugadores
        )
        await manager_lobby.broadcast(int(idPartida), jugador_unido_message.model_dump())
        return response
    except HTTPException as e:
        raise e

@router.get("/partidas", response_model=List[PartidaResponse])
async def listar_partidas(db: Session = Depends(crear_session)):
    partidas = db_service.obtener_partidas(db)
    return [
            PartidaResponse(
                id_partida=str(partida.id),
                nombre_partida=partida.nombre,
                cant_min_jugadores=partida.min, 
                cant_max_jugadores=partida.max,
                privada= True if partida.contrasena else False  
            ) for partida in partidas
        ] 

@router.post("/partida/{id_partida}/jugador/{id_jugador}", status_code=200, response_model=IniciarPartidaResponse)
async def iniciar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        eliminar_partida_message = EliminarPartidaSchema(
                   type=WebSocketMessageType.ELIMINAR_PARTIDA,
                   data=EliminarPartidaDataSchema( idPartida=id_partida )
               )

        response = await partida_service.iniciar_partida(id_partida, id_jugador, db)
        await manager_lobby.broadcast(id_partida, response)
        await manager.broadcast(eliminar_partida_message.model_dump())
        figuras_data = await computar_y_enviar_figuras(id_partida, db)
        await manager_game.broadcast(id_partida, figuras_data)

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 
    
    await asyncio.sleep(0.5)    
    figuras_data = await computar_y_enviar_figuras(id_partida, db)
    await manager_game.broadcast(id_partida, figuras_data)
    timer.manejar_temporizador(id_partida, db)
    return IniciarPartidaResponse(idPartida=str(id_partida))

    
@router.patch("/partida/{id_partida}/jugador/{id_jugador}", status_code=202)
async def pasar_turno(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        
        sigTurno = partida_service.pasar_turno(id_partida, id_jugador, db)
        reposicion_figuras = reposicion_cartas_figuras(id_partida, id_jugador, db)
                
        declarar_figura_message = ReposicionFiguras(
            type= WebSocketMessageType.REPOSICION_FIGURAS,
            data= DeclararFiguraDataSchema(
                cartasFig= reposicion_figuras
            )
        )

        await manager_game.broadcast(id_partida, declarar_figura_message.model_dump())    
        await manager_game.broadcast(id_partida, {"type": "PasarTurno", "turno": sigTurno, "timeout": False})
        figuras_data = await computar_y_enviar_figuras(id_partida, db)
        await manager_game.broadcast(id_partida, figuras_data)
        timer.manejar_temporizador(id_partida, db)
    except Exception as e:
        raise HTTPException(status_code=410, detail=str(e))


@router.delete("/partida/{id_partida}/jugador/{id_jugador}", status_code = 202)
async def abandonar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:   
        partida = db_service.obtener_partida(id_partida, db)
        if partida is None:
            raise HTTPException(status_code=404, detail=f"No existe partida con id: {id_partida}")
        cantidad_jugadores = obtener_cantidad_jugadores(id_partida, db)
                
        abandonar_partida_message = AbandonarPartidaSchema(
            type=WebSocketMessageType.ABANDONAR_PARTIDA,
            data=AbandonarPartidaDataSchema(
                idPartida=id_partida,
                idJugador=id_jugador
            )
        )

        eliminar_partida_message = EliminarPartidaSchema(
                   type=WebSocketMessageType.ELIMINAR_PARTIDA,
                   data=EliminarPartidaDataSchema( idPartida=id_partida )
               )

        if partida.activa:
            if cantidad_jugadores == 2:
               #ws para que si queda un jugador finalice el juego
               await manager_game.broadcast(id_partida, eliminar_partida_message.model_dump())
               #ws para que se deje de mostrar en el inicio si la partida terminó
               await manager.broadcast(eliminar_partida_message.model_dump())
               timer.cancelar_temporizador(id_partida)

            else:
               #ws para que se deje de mostrar jugador el juego
               await manager_game.broadcast(id_partida, abandonar_partida_message.model_dump())
        else:
            if id_jugador == partida.id_owner:
               #ws para que los demas jugadores vuelvan al inicio si el host cancela la partida
               await manager_lobby.broadcast(id_partida, eliminar_partida_message.model_dump())
               #ws para que la partida se deje de mostrar en el inicio
               await manager.broadcast(eliminar_partida_message.model_dump())
            else:
               #ws para que deje de mostrar al jugador en el lobby
               await manager_lobby.broadcast(id_partida, abandonar_partida_message.model_dump()) #para que deje de mostrar al jugador en el lobby

        await partida_service.abandonar_partida(id_partida, id_jugador, db)   
        figuras_data = await computar_y_enviar_figuras(id_partida, db)   
        await manager_game.broadcast(id_partida, figuras_data)
    
    except HTTPException as he:
        logging.error(f"HTTP exception in abandonar_partida route: {str(he)}")
        raise he
    except Exception as e:
        logging.error(f"Unexpected error in abandonar_partida route: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

