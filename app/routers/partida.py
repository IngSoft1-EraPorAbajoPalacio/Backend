from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from schema.partida_schema import CrearPartidaResponse, CrearPartida, PartidaResponse, UnirsePartidaResponse, UnirsePartidaRequest, InicarPartidaResponse 
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

@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=200)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest, db: Session = Depends(crear_session)):
    try:
        print("holaaaa")
        print(idPartida)
        response = await partida_service.unirse_partida(idPartida, request.nombreJugador, db)
        jugadores = partida_service.obtener_jugadores(int(idPartida), db)
        await manager.broadcast({
            "type":"JugadorUnido",
            "data":{
                "idJugador": response.idJugador,
                "ListaJugadores": [[j.id, j.nickname] for j in jugadores]
            }
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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("SE INICIO CONEXION")
    try:
        while True:
            data = await websocket.receive_text()
            print("SE INICIO CONEXION")
            print(f"la data es : {data}")
    except WebSocketDisconnect as e :
        print("SE CERRO LA CONEXION")
        print(e)
        await manager.disconnect(websocket)        
    except Exception as e:
        print("WebSocket connection closed", e)
    finally:
        await manager.disconnect(websocket)