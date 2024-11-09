from fastapi import APIRouter,  WebSocket, WebSocketDisconnect, Depends
from app.db.base import crear_session
from sqlalchemy.orm import Session
from app.routers.websocket_manager import manager
from app.routers.websocket_manager_game import manager_game
from app.routers.websocket_manager_lobby import manager_lobby
from app.services.juego_service import *
from app.schema.websocket_schema import *

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print("SE INICIO CONEXION")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect as e :
        await manager.eliminar_lista(websocket)
    except RuntimeError as e:
        print(str(e))
    

@router.websocket("/ws/lobby/{idPartida}")
async def websocket_endpoint_lobby(websocket: WebSocket, idPartida: str):
    await manager_lobby.connect(int(idPartida),websocket)
    print("SE INICIO LA CONEXION DEL LOBBY")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager_lobby.disconnect(int(idPartida),websocket)
          
        
@router.websocket("/ws/game/{idPartida}/jugador/{idJugador}")
async def websocket_endpoint_game(websocket: WebSocket, idPartida: int, idJugador: int, db: Session = Depends(crear_session)):
    await manager_game.connect(idPartida, idJugador, websocket)
    
    print("SE INICIO LA CONEXION DEL GAME")
    print(manager_game.active_connections)
    
    # Obtiene los datos de la partida
    response =  juego_service.obtener_datos_partida(idPartida, idJugador, db)

    # Crea un mensaje de inicio de conexión con los datos de la partida
    conexion_message = InicioConexionSchema(
        type=WebSocketMessageType.INICIO_CONEXION,
        data=InicioConexionDataSchema(
            fichas=response["fichas"],
            orden=response["orden"],
            turnoActual=response["turnoActual"],
            colorProhibido=response["colorProhibido"],
            tiempo=response["tiempo"],
            cartasMovimiento=response["cartasMovimiento"],
            cartasFigura=response["cartasFigura"],
            cartasBloqueadas=response["cartasBloqueadas"],
            cantMovimientosParciales=response["cantMovimientosParciales"],
            figurasResaltadas=response["figurasResaltadas"]
        )
    )
    
    print(f"LAS FIGURAS RESALTADAS SON : {conexion_message.data.figurasResaltadas}")
    
    # Envía el mensaje de inicio de conexión
    await manager_game.broadcast_personal(idPartida, idJugador, conexion_message.dict())
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager_game.disconnect(idPartida, idJugador,websocket)    