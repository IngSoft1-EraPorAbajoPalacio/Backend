import asyncio
from fastapi import HTTPException
from app.db.models import *
from app.services.partida_service import partida_service
from app.services.cartas_service import *
from datetime import datetime, timedelta
from app.routers.websocket_manager_game import manager_game
from typing import Dict

from app.schema.websocket_schema import *
    
class TimerService:
    def __init__(self):
        self.timers: Dict[int, asyncio.Task] = {}
    
    async def reiniciar_temporizador(self, id_partida: int, db: Session):
        partida = partida_service.obtener_partida(id_partida, db)

        if not partida:
            raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")

        if not partida.activa:
            raise HTTPException(status_code=404, detail=f"La partida {id_partida} no está activa")

        duracion_turno = datetime.utcnow() + timedelta(seconds=5) # Despues cambiar a 2 minutos  

        while datetime.utcnow() <= duracion_turno:
            tiempo_restante = (duracion_turno - datetime.utcnow()).total_seconds()
            await manager_game.broadcast(id_partida, {"type": "Temporizador", "tiempoRestante": tiempo_restante})
            await asyncio.sleep(1)

        await manager_game.broadcast(id_partida, {"type": "PasarTurno", "timeout": True})
        
    def cancelar_temporizador(self, id_partida: int):
        if id_partida in self.timers:
            self.timers[id_partida].cancel()
            del self.timers[id_partida]
            
    def manejar_temporizador(self, id_partida: int, db: Session):
        if id_partida in self.timers:
            self.cancelar_temporizador(id_partida)
        self.timers[id_partida] = asyncio.create_task(self.reiniciar_temporizador(id_partida, db))

timer_service = TimerService()