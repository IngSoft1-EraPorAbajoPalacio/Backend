from fastapi import APIRouter, HTTPException, Depends
from app.routers.partida import computar_y_enviar_figuras
from app.schema.juego_schema import * 
from app.services.juego_service import juego_service 
from app.db.base import crear_session
from sqlalchemy.orm import Session
from app.routers.websocket_manager_game import manager_game
from app.schema.websocket_schema import * 

router = APIRouter()

@router.patch("/partida/{idPartida}/jugador/{idJugador}/tablero/jugar-movimiento", status_code=202)
async def jugar_movimiento(idPartida: int, idJugador: int, request: JugarMovimientoRequest, db: Session = Depends(crear_session)):
    try:
        response = await juego_service.jugar_movimiento(idPartida, idJugador, request, db)
        jugar_movimiento_message = MovimientoParcialSchema(
            type=WebSocketMessageType.MOVIMIENTO_PARCIAL,
            data=MovimientoParcialDataSchema(
                carta=response["carta"],
                fichas=response["fichas"]
            )
        )
        await manager_game.broadcast(idPartida, jugar_movimiento_message.model_dump())    
        figuras_data = await computar_y_enviar_figuras(idPartida, db)
        await manager_game.broadcast(idPartida, figuras_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/partida/{idPartida}/jugador/{idJugador}/tablero/deshacer-movimiento", status_code=202) 
async def deshacer_movimiento(idPartida: int, idJugador: int, db: Session = Depends(crear_session)):
    try:
        deshacer_movimiento = juego_service.deshacer_movimiento(idPartida, idJugador, db)
        deshacer_movimiento_message = DeshacerMovimiento(
            type= WebSocketMessageType.DESHACER_MOVIMIENTO ,
            posiciones= deshacer_movimiento['posiciones']
        )
        
        resultado = {
            "carta": [
                {
                    "id": deshacer_movimiento['idCarta'],
                    "movimiento": deshacer_movimiento['movimiento']
                }
            ]
        }
        await manager_game.broadcast(idPartida, deshacer_movimiento_message.model_dump())
        figuras_data = await computar_y_enviar_figuras(idPartida, db)
        await manager_game.broadcast(idPartida, figuras_data)
        
        return resultado
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    
@router.patch("/partida/{idPartida}/jugador/{idJugador}/tablero/deshacer-movimientos", status_code=202) 
async def deshacer_movimientos(idPartida: int, idJugador: int, db: Session = Depends(crear_session)):
    try:
        resultado = juego_service.deshacer_movimientos(idPartida, idJugador, db)
        
        if(resultado['cantMovimientosDesechos'] != 0):
            deshacer_movimientos_message = DeshacerMovimientos(
                type= WebSocketMessageType.DESHACER_MOVIMIENTOS,
                posiciones= resultado['posiciones'],
                cantMovimientosDesechos= resultado['cantMovimientosDesechos']
            )
            await manager_game.broadcast(idPartida, deshacer_movimientos_message.model_dump()) 
        figuras_data = await computar_y_enviar_figuras(idPartida, db)
        await manager_game.broadcast(idPartida, figuras_data)
        return { "cartas": resultado['cartas'] }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))    

@router.post("/partida/{idPartida}/jugador/{idJugador}/tablero/declarar-figura", status_code=202)
async def declarar_figura(idPartida: int, idJugador: int, request: DeclararFiguraRequest, db: Session = Depends(crear_session)):
    try:
        response = await juego_service.declarar_figura(idPartida, idJugador, request, db)
        if response["completarFigura"] == "descartarFigura" or response["completarFigura"] == "desbloquearFigura":
            declarar_figura_message = DeclararFiguraSchema(
                type=WebSocketMessageType.FIGURA_DESCARTAR,
                data=DeclararFiguraColorProhibido(
                    cartasFig=response["cartasFig"],
                    colorProhibido=response["colorProhibido"]
                )
            )
            await manager_game.broadcast(idPartida, declarar_figura_message.model_dump())            
            if response["completarFigura"] == "desbloquearFigura":
                desbloquear_figuras_message = DesbloquearFiguraSchema(
                    type=WebSocketMessageType.DESBLOQUEAR_FIGURA,
                    data=DesbloquearFiguraDataSchema(
                        idCarta=response["idCarta"],
                        idJugador=response["idJugador"],
                        colorProhibido=response["colorProhibido"]
                    )
                )
                await manager_game.broadcast(idPartida, desbloquear_figuras_message.model_dump())
        elif response["completarFigura"] == "bloquearFigura":
            bloquear_figuras_message = BloquearFiguraSchema(
                type=WebSocketMessageType.BLOQUEAR_FIGURA,
                data=BloquearFiguraDataSchema(
                    idCarta=response["idCarta"],
                    idJugador=response["idJugador"],
                    colorProhibido=response["colorProhibido"]
                )
            )
            await manager_game.broadcast(idPartida, bloquear_figuras_message.model_dump())
        figuras_data = await computar_y_enviar_figuras(idPartida, db)
        await manager_game.broadcast(idPartida, figuras_data)
    except HTTPException as e:    
        await computar_y_enviar_figuras(idPartida, db)
        raise e