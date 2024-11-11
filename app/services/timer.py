from fastapi import  HTTPException
from app.services.partida_service import partida_service
from app.routers.websocket_manager_game import manager_game
from typing import Dict
from app.services.bd_service import *
from app.schema.partida_schema import * 
from app.services.jugador_service import *
from app.services.juego_service import *
from app.services.cartas_service import *
from sqlalchemy.orm import Session
from app.schema.websocket_schema import * 
from sqlalchemy import update
import  asyncio

class Timer:
    
    def __init__(self):
        
        self.timers: Dict[int, asyncio.Task] = {}

    async def reiniciar_temporizador(self, id_partida: int, db: Session):
        
        partida = db_service.obtener_partida(id_partida, db)
        turno_actual = db_service.obtener_turno_actual(id_partida, db)

        if not partida:
            raise HTTPException(status_code=404, detail=f"No existe ninguna partida con id {id_partida}")

        if not partida.activa:
            raise HTTPException(status_code=404, detail=f"La partida {id_partida} no está activa")

        db_service.setear_tiempo(id_partida, 20, db)
        tiempo = db_service.obtener_tiempo_actual(id_partida, db)
        
        # Tiempo de duración del turno
        while tiempo > 0:
            print(tiempo)
            await asyncio.sleep(2)
            tiempo -= 2
            db.execute(update(Partida).values(tiempo=tiempo-2))
            db.commit()
            
        # Pasar al siguiente turno y enviar mensajes de reposición de cartas
        sigTurno = partida_service.pasar_turno(id_partida, turno_actual, db)
        reposicion_figuras = reposicion_cartas_figuras(id_partida, turno_actual, db)
                
        declarar_figura_message = ReposicionFiguras(
            type= WebSocketMessageType.REPOSICION_FIGURAS,
            data= DeclararFiguraDataSchema(
                cartasFig= reposicion_figuras
            )
        )

        await manager_game.broadcast(id_partida, declarar_figura_message.model_dump())    
        await manager_game.broadcast(id_partida, {"type": "PasarTurno", "turno": sigTurno, "timeout": True})
        figuras_data = await computar_y_enviar_figuras(id_partida, db)
        await manager_game.broadcast(id_partida, figuras_data)

        # Reiniciar el temporizador
        timer.manejar_temporizador(id_partida, db)

    def cancelar_temporizador(self, id_partida: int):
        if id_partida in self.timers:
            self.timers[id_partida].cancel()
            del self.timers[id_partida]
            
    def manejar_temporizador(self, id_partida: int, db: Session):
        if id_partida in self.timers:
            self.cancelar_temporizador(id_partida)
        self.timers[id_partida] = asyncio.create_task(self.reiniciar_temporizador(id_partida, db))

timer = Timer()