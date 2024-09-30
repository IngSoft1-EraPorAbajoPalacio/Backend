from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from schema.partida_schema import *
from services.partida_service import partida_service
from db.base import crear_session
from sqlalchemy.orm import Session
from app.routers.websocket_manager import manager

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
        await manager.agregar_partida(str(response.id_partida), {
            "idPartida": response.id_partida,
            "nombrePartida": partida.nombre_partida,
            "cantJugadoresMin": partida.cant_min_jugadores,
            "cantJugadoresMax": partida.cant_max_jugadores
        })
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=201)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest, db: Session = Depends(crear_session)):
    try:
        response = await partida_service.unirse_partida(idPartida, request.nombreJugador, db)
        jugadores = partida_service.obtener_jugadores(int(idPartida), db)
        await manager.jugador_unido(idPartida, {
            "idJugador": response.idJugador,
            "ListaJugadores": [[j.id, j.nickname] for j in jugadores]
        })
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/partidas", response_model=List[PartidaResponse])
async def listar_partidas(db: Session = Depends(crear_session)):
    try:
        return partida_service.listar_partidas(db)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/partida/{id_partida}/jugador/{id_jugador}", response_model=InicarPartidaResponse)
async def iniciar_partida(id_partida: int, id_jugador: int, db: Session = Depends(crear_session)):
    try:
        response = partida_service.iniciar_partida(id_partida, id_jugador, db)
        # Aquí deberías obtener la información necesaria para el mensaje de IniciarPartida
        # Este es un ejemplo, ajusta según tu lógica de juego
        await manager.iniciar_partida(str(id_partida), {
            "fichas": [{"x": 0, "y": 0, "color": "red"}],  # Ejemplo, ajusta según tu lógica
            "orden": [1, 2, 3, 4],  # Ejemplo, ajusta según tu lógica
            "cartasMovimiento": [{"id": 1, "movimiento": "adelante"}],  # Ejemplo
            "cartasFigura": [{"idJugador": 1, "nombreJugador": "Jugador1", "cartas": [{"id": 1, "figura": 1}]}]  # Ejemplo
        })
        return response
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
        jugadores = partida_service.obtener_jugadores(id_partida, db)
        if len(jugadores) > 1:
            await manager.eliminar_jugador(str(id_partida), {
                "idJugador": id_jugador,
                "ListaJugadores": [[j.id, j.nickname] for j in jugadores]
            })
        else:
            await manager.terminar_partida(str(id_partida), {
                "nombreJugGanador": jugadores[0].nickname
            })
        return {"message": "Jugador eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.websocket("/ws/{id_partida}")
async def websocket_endpoint(websocket: WebSocket, id_partida: str):
    await manager.connect(websocket, id_partida)
    try:
        while True:
            data = await websocket.receive_text()
            # Aquí puedes manejar los mensajes recibidos del cliente si es necesario
    except WebSocketDisconnect:
        manager.disconnect(websocket)
