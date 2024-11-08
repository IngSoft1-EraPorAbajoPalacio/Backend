from pydantic import BaseModel
from typing import List, Literal
from enum import Enum
from app.schema.juego_schema import Posicion

class WebSocketMessageType(str, Enum):
    AGREGAR_PARTIDA = "AgregarPartida"
    JUGADOR_UNIDO = "JugadorUnido"
    INICIAR_PARTIDA = "IniciarPartida"
    ABANDONAR_PARTIDA = "AbandonarPartida"
    ELIMINAR_PARTIDA = "PartidaEliminada"
    FIGURAS_ENCONTRADAS = "DeclararFigura"
    MOVIMIENTO_PARCIAL = "MovimientoParcial"
    DESHACER_MOVIMIENTO = "DeshacerMovimiento"
    DESHACER_MOVIMIENTOS = "DeshacerMovimientos"
    FIGURA_DECLARADA = "FiguraDescartar"
    REPOSICION_FIGURAS = "ReposicionFiguras"
    REPOSICION_MOVIMIENTOS = "ReposicionMovimientos"
    INICIO_CONEXION = "InicioConexion"

class JugadorSchema(BaseModel):
    id: int
    nombre: str

class AgregarPartidaDataSchema(BaseModel):
    idPartida: int
    nombrePartida: str
    cantJugadoresMin: int
    cantJugadoresMax: int

class InicioConexionDataSchema(BaseModel):
    fichas: List[dict]
    orden: List[int]
    turnoActual: int
    colorProhibido: str
    tiempo: int
    cartasMovimiento: List[dict]
    cartasFigura: List[dict]
    cartasBloqueadas: List[int]

class AbandonarPartidaDataSchema(BaseModel):
    idPartida: int
    idJugador: int

class EliminarPartidaDataSchema(BaseModel):
    idPartida: int

class MovimientoParcialDataSchema(BaseModel):
    carta: dict
    fichas: List[dict]

class DeclararFiguraDataSchema(BaseModel):
    cartasFig: List[dict]

class JugadorUnidoSchema(BaseModel):
    type: Literal[WebSocketMessageType.JUGADOR_UNIDO]
    ListaJugadores: List[JugadorSchema]

class AgregarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.AGREGAR_PARTIDA]
    data: AgregarPartidaDataSchema

class IniciarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.INICIAR_PARTIDA]

class InicioConexionSchema(BaseModel):
    type: Literal[WebSocketMessageType.INICIO_CONEXION]
    data: InicioConexionDataSchema

class AbandonarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.ABANDONAR_PARTIDA]
    data: AbandonarPartidaDataSchema

class EliminarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.ELIMINAR_PARTIDA] = WebSocketMessageType.ELIMINAR_PARTIDA
    data: EliminarPartidaDataSchema

class MovimientoParcialSchema(BaseModel):
    type: Literal[WebSocketMessageType.MOVIMIENTO_PARCIAL]
    data: MovimientoParcialDataSchema
    
class DeshacerMovimiento(BaseModel):
    type: Literal[WebSocketMessageType.DESHACER_MOVIMIENTO]
    posiciones: List[Posicion]
    
class DeshacerMovimientos(BaseModel):
    type: Literal[WebSocketMessageType.DESHACER_MOVIMIENTOS]
    posiciones: List[List[Posicion]]    
    cantMovimientosDesechos: int
    
class Coordenada(BaseModel):
    x: int
    y: int

class Figura(BaseModel):
    tipoFig: int
    coordenadas: List[Coordenada]

class FigurasEncontradasDataSchema(BaseModel):
    figuras: List[Figura]

class FigurasEncontradasSchema(BaseModel):
    type: Literal[WebSocketMessageType.FIGURAS_ENCONTRADAS]
    data: FigurasEncontradasDataSchema

class MovimientoParcialSchema(BaseModel):
    type: Literal[WebSocketMessageType.MOVIMIENTO_PARCIAL]
    data: MovimientoParcialDataSchema

class DeclararFiguraSchema(BaseModel):
    type: Literal[WebSocketMessageType.FIGURA_DECLARADA]
    data: DeclararFiguraDataSchema
    
    
class ReposicionFiguras(BaseModel):
    type : Literal[WebSocketMessageType.REPOSICION_FIGURAS]
    data: DeclararFiguraDataSchema

    
class ReposicionCartasFiguras(BaseModel):
    type : Literal[WebSocketMessageType.REPOSICION_FIGURAS]
    data: ReposicionFiguras

class ReposicionCartasMovimientos(BaseModel):
    type : Literal[WebSocketMessageType.REPOSICION_MOVIMIENTOS]
    cartas: List[dict]