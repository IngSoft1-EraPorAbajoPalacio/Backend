from fastapi import WebSocket
from typing import List,Dict

class ConnectionManagerLobby:
    def __init__(self):
        self.active_connections: Dict[int,List[WebSocket]] = {}

    async def connect(self, idPartida:int, websocket: WebSocket):
        await websocket.accept()
        if idPartida not in self.active_connections:
            self.active_connections[idPartida] = []
        self.active_connections[idPartida].append(websocket)

    async def disconnect(self, idPartida:int, websocket: WebSocket):
        if idPartida in self.active_connections:
            self.active_connections[idPartida].remove(websocket)
            
        if not self.active_connections[idPartida]:
            del self.active_connections[idPartida]

    async def broadcast(self,idPartida:int , message: dict):
        if idPartida in self.active_connections:
            for conexion in self.active_connections[idPartida]:
                await conexion.send_json(message)
                            
manager_lobby = ConnectionManagerLobby()