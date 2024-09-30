from fastapi import APIRouter, HTTPException
from app.schema.partida_schema import PartidaCreate, PartidaResponse, PartidasListResponse, UnirsePartidaRequest, UnirsePartidaResponse
from app.services.partida_service import partida_service

router = APIRouter()

@router.post("/partida", response_model=PartidaResponse, status_code=201)
async def crear_partida(partida: PartidaCreate):
    try:
        id_partida = await partida_service.crear_partida(partida)
        return PartidaResponse(
            id_partida=id_partida,
            nombre_partida=partida.nombre_partida
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=201)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest):
    try:
        id_jugador = await partida_service.unirse_partida(idPartida, request.nombreJugador)
        return UnirsePartidaResponse(idJugador=id_jugador)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/partidas", response_model=PartidasListResponse)
def listar_partidas():
    partidas = partida_service.listar_partidas()
    if not partidas:
        return PartidasListResponse(partidas=[], mensaje="No hay partidas disponibles en este momento.")
    return PartidasListResponse(partidas=partidas, mensaje="Partidas disponibles encontradas.")
    