from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from schema.partida_schema import * 
from services.partida_service import partida_service
from db.base import crear_session
from sqlalchemy.orm import Session
from routers.websocket_manager import manager
from typing import List

router = APIRouter()

@router.get("/partidas/{id}", response_model=PartidaResponse)
def obtener_partida(id: int, db: Session = Depends(crear_session)):
    try:
        return partida_service.obtener_partida_particular(id, db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/partida", response_model=CrearPartidaResponse, status_code=201)
async def crear_partida(partida: CrearPartida, db: Session = Depends(crear_session)):
    try:
        response = partida_service.crear_partida(partida, db)
        await manager.broadcast({
            "type": "AgregarPartida",
            "data": {
                "idPartida": response.id_partida,
                "nombrePartida": partida.nombre_partida,
                "cantJugadoresMin": partida.cant_min_jugadores,
                "cantJugadoresMax": partida.cant_max_jugadores
            }
        })
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=201)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest, db: Session = Depends(crear_session)):
    try:
        response = await partida_service.unirse_partida(idPartida, request.nombreJugador, db)
        jugadores = partida_service.obtener_jugadores(int(idPartida), db)
        await manager.broadcast({
            "type":"JugadorUnido",
            "ListaJugadores":[
                {"id": j.id, "nombre": j.nickname} for j in jugadores
            ]
        })
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/partidas", response_model=List[PartidaResponse])
async def listar_partidas(db: Session = Depends(crear_session)):
    return partida_service.listar_partidas(db)


@router.post("/partida/{id_partida}/jugador/{id_jugador}", status_code=200, response_model=IniciarPartidaResponse)
async def iniciar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        response = partida_service.iniciar_partida(id_partida, id_jugador, db)
        await manager.broadcast(response)
        return IniciarPartidaResponse(id_partida=str(id_partida))
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
'''''
@router.patch("/partida/{idPartida}", response_model=PasarTurnoResponse)
async def pasar_turno(id_partida: int, db: Session = Depends(crear_session)):
    try:
        response = partida_service.pasar_turno(id_partida, db)
        await manager.pasar_turno(str(id_partida))
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
'''''

@router.delete("/partida/{idPartida}/jugador/{idJugador}")
async def abandonar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        
        partida_service.abandonar_partida(id_partida, id_jugador, db)
        return partida_service.listar_partidas(db)
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
