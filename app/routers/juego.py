from fastapi import APIRouter, HTTPException, Depends
from app.schema.juego_schema import * 
from app.services.juego_service import juego_service 
from app.db.base import crear_session
from sqlalchemy.orm import Session
from app.schema.websocket_schema import * 

router = APIRouter()

@router.patch("/partida/{idPartida}/jugador/{idJugador}/tablero/jugar-movimiento", status_code=202)
async def jugar_movimiento(idPartida: int, idJugador: int, request: JugarMovimientoRequest, db: Session = Depends(crear_session)):
    try:
        response = await juego_service.jugar_movimiento(idPartida, idJugador, request, db)
        return response
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

