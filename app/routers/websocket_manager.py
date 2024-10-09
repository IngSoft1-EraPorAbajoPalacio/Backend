from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            if websocket in self.active_connections:
                await websocket.close()
                self.active_connections.remove(websocket)
        except Exception as e:
            print(str(e))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                await self.disconnect(connection)
    
    async def eliminar_lista(self,socket:WebSocket):
        self.active_connections.remove(socket)            
                
                
manager = ConnectionManager()