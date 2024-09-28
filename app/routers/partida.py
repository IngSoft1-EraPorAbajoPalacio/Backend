from fastapi import APIRouter, HTTPException,Depends
from schema.partida_schema import *
from services.partida_service import partida_service
from db.base import crear_session
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/partidas/{id}", response_model=PartidaResponse)
def obtener_partida(id : int, db:Session = Depends(crear_session)) :
    try:
        return partida_service.obtener_partida_particular(id,db)        
    except Exception as e: 
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/partida", response_model=CrearPartidaResponse, status_code=201)
async def crear_partida(partida: CrearPartida, db :Session =  Depends(crear_session)):    
    try:
        return partida_service.crear_partida(partida,db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/partida/{idPartida}/jugador", response_model=UnirsePartidaResponse, status_code=201)
async def unirse_partida(idPartida: str, request: UnirsePartidaRequest, db:Session = Depends(crear_session)):
    try:
        return await partida_service.unirse_partida(idPartida, request.nombreJugador,db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/partidas", response_model=list[PartidaResponse])
async def listar_partidas(db:Session = Depends(crear_session)):
    try:
        return partida_service.listar_partidas(db)
    except Exception as e: 
        raise HTTPException(status_code=404, detail=str(e))
    

@router.post("/partida/{id_partida}/jugador/{id_jugador}", response_model=InicarPartidaResponse)
def iniciar_partida(id_partida :int, id_jugador : int, db : Session = Depends(crear_session)):
    try:
        return partida_service.iniciar_partida(id_partida,id_jugador,db)
    except Exception as e:
        raise HTTPException(status_code= 404, detail= str(e))
    

@router.delete("/partida/{idPartida}/jugador/{idJugador}")
def abandonar_partida(id_partida :int, id_jugador : int, db : Session = Depends(crear_session)):
    try:
        return partida_service.abandonar_partida(id_partida,id_jugador,db)
    except Exception as e:
        raise HTTPException(status_code= 404, detail= str(e))