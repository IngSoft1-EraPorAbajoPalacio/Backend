from fastapi import WebSocket
from typing import List, Dict

class ConnectionManagerGame:
    def __init__(self):
        self.active_connections: Dict[int, List[Dict[int, WebSocket]]] = {}

    async def connect(self, idPartida:int, idJugador: int, websocket: WebSocket):
        await websocket.accept()
        if idPartida not in self.active_connections:
            self.active_connections[idPartida] = []
        self.active_connections[idPartida].append({idJugador : websocket}) 

    async def disconnect(self, idPartida:int, idJugador: int, websocket: WebSocket):
        if idPartida in self.active_connections:
            for socket in self.active_connections[idPartida]:
                if idJugador in socket and socket[idJugador] == websocket:
                    self.active_connections[idPartida].remove(socket)
                    break
            
        if not self.active_connections[idPartida]:
            del self.active_connections[idPartida]

    async def broadcast(self, idPartida:int, message: dict):
        if idPartida in self.active_connections:
            for socket in self.active_connections[idPartida]:
                for _, conexion in socket.items():
                    await conexion.send_json(message)
                
    async def broadcast_personal(self, idPartida: int, idJugador: int, message: dict):
        if idPartida in self.active_connections:
            for socket in self.active_connections[idPartida]:
                if idJugador in socket:
                    await socket[idJugador].send_json(message)                      
                      
manager_game = ConnectionManagerGame()