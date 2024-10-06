from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from app.schema.partida_schema import * 
from app.services.partida_service import partida_service
from app.services.jugador_service import *
from app.db.base import crear_session
from sqlalchemy.orm import Session
from app.routers.websocket_manager import manager

from typing import List


router = APIRouter()

@router.get("/partidas/{id}", response_model=PartidaResponse)
def obtener_partida(id_partida: int, db: Session = Depends(crear_session)):
    try:
        partida = partida_service.obtener_partida(id_partida, db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))    
    
    return PartidaResponse(
        id_partida=str(id_partida),
        nombre_partida=partida.nombre,
        cant_min_jugadores= partida.min,
        cant_max_jugadores= partida.max
    )    


@router.post("/partida", response_model=CrearPartidaResponse, status_code=201)
async def crear_partida(partida: CrearPartida, db: Session = Depends(crear_session)):
    try:
        partida_creada = await partida_service.crear_partida(partida, db)
        await manager.broadcast({
            "type": "AgregarPartida",
            "data": {
                "idPartida": partida_creada.id_partida,
                "nombrePartida": partida.nombre_partida,
                "cantJugadoresMin": partida.cant_min_jugadores,
                "cantJugadoresMax": partida.cant_max_jugadores
            }
        })
        return partida_creada    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=201)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest, db: Session = Depends(crear_session)):
    try:
        response = await partida_service.unirse_partida(idPartida, request.nombreJugador, db)
        jugadores = obtener_jugadores(int(idPartida), db)
        await manager.broadcast({
            "type":"JugadorUnido",
            "ListaJugadores":[
                {"id": j.id, "nombre": j.nickname} for j in jugadores
            ]
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))    
    return response


@router.get("/partidas", response_model=List[PartidaResponse])
async def listar_partidas(db: Session = Depends(crear_session)):
    partidas = partida_service.obtener_partidas(db)
    return [
            PartidaResponse(
                id_partida=str(partida.id),
                nombre_partida=partida.nombre,
                cant_min_jugadores=partida.min, 
                cant_max_jugadores=partida.max
            ) for partida in partidas
        ] 

@router.post("/partida/{id_partida}/jugador/{id_jugador}", status_code=200, response_model=IniciarPartidaResponse)
async def iniciar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        response = await partida_service.iniciar_partida(id_partida, id_jugador, db)
        await manager.broadcast(response)
        print(response)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))     
    return IniciarPartidaResponse(idPartida=str(id_partida))

    
@router.patch("/partida/{id_partida}/jugador/{id_jugador}", status_code=202)
async def pasar_turno(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        sigTurno = partida_service.pasar_turno(id_partida, id_jugador, db)
        await manager.broadcast({"type": "PasarTurno", "turno": sigTurno})
        return
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/partida/{idPartida}/jugador/{idJugador}")
async def abandonar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        return partida_service.abandonar_partida(id_partida, id_jugador, db)        
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("SE INICIO CONEXION")
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect as e :
        print(str(e))
    except RuntimeError as e:
        print(str(e))
    