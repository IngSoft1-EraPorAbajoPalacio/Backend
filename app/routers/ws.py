from fastapi import APIRouter,  WebSocket, WebSocketDisconnect
from app.routers.websocket_manager import manager
from app.routers.websocket_manager_game import manager_game
from app.routers.websocket_manager_lobby import manager_lobby

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
async def websocket_endpoint_game(websocket: WebSocket, idPartida: int, idJugador: int):
    await manager_game.connect(idPartida, idJugador, websocket)
    print("SE INICIO LA CONEXION DEL GAME")
    print(manager_game.active_connections)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager_game.disconnect(idPartida, idJugador,websocket)    