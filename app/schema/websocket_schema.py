from pydantic import BaseModel
from typing import List, Literal
from enum import Enum

class WebSocketMessageType(str, Enum):
    AGREGAR_PARTIDA = "AgregarPartida"
    JUGADOR_UNIDO = "JugadorUnido"
    INICIAR_PARTIDA = "IniciarPartida"
    ABANDONAR_PARTIDA = "AbandonarPartida"
    ELIMINAR_PARTIDA = "PartidaEliminada"
    MOVIMIENTO_PARCIAL = "MovimientoParcial"
    
class JugadorSchema(BaseModel):
    id: int
    nombre: str

class AgregarPartidaDataSchema(BaseModel):
    idPartida: int
    nombrePartida: str
    cantJugadoresMin: int
    cantJugadoresMax: int

class IniciarPartidaDataSchema(BaseModel):
    jugadorInicial: str
    listaJugadores: List[str]
    cartas: List[str]

class AbandonarPartidaDataSchema(BaseModel):
    idPartida: int
    idJugador: int

class EliminarPartidaDataSchema(BaseModel):
    idPartida: int

class MovimientoParcialDataSchema(BaseModel):
    carta: dict
    fichas: List[dict]

class JugadorUnidoSchema(BaseModel):
    type: Literal[WebSocketMessageType.JUGADOR_UNIDO]
    ListaJugadores: List[JugadorSchema]

class AgregarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.AGREGAR_PARTIDA]
    data: AgregarPartidaDataSchema

class IniciarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.INICIAR_PARTIDA]
    data: IniciarPartidaDataSchema

class AbandonarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.ABANDONAR_PARTIDA]
    data: AbandonarPartidaDataSchema

class EliminarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.ELIMINAR_PARTIDA] = WebSocketMessageType.ELIMINAR_PARTIDA
    data: EliminarPartidaDataSchema

class MovimientoParcialSchema(BaseModel):
    type: Literal[WebSocketMessageType.MOVIMIENTO_PARCIAL]
    data: MovimientoParcialDataSchema