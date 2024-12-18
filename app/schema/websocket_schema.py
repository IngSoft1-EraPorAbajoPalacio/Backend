from pydantic import BaseModel
from typing import List, Literal
from enum import Enum
from app.schema.juego_schema import Posicion
from app.db.models import Color

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
    FIGURA_DESCARTAR = "FiguraDescartar"
    REPOSICION_FIGURAS = "ReposicionFiguras"
    REPOSICION_MOVIMIENTOS = "ReposicionMovimientos"
    PARTIDA_FINALIZADA = "PartidaFinalizada"
    BLOQUEAR_FIGURA = "FiguraBloqueada"
    DESBLOQUEAR_FIGURA = "FiguraDesbloqueada"
    INICIO_CONEXION = "InicioConexion"
    MENSAJE_ENVIADO = "Mensaje"

class JugadorSchema(BaseModel):
    id: int
    nombre: str

class AgregarPartidaDataSchema(BaseModel):
    idPartida: int
    nombrePartida: str
    cantJugadoresMin: int
    cantJugadoresMax: int
    privada: bool

class IniciarPartidaDataSchema(BaseModel):
    jugadorInicial: str
    listaJugadores: List[str]
    cartas: List[str]


class Coordenada(BaseModel):
    x: int
    y: int
    
class FiguraResaltada(BaseModel):
    idFig: str
    tipoFig: int
    coordenadas: List[Coordenada]
    
class InicioConexionDataSchema(BaseModel):
    fichas: List[dict]
    orden: List[int]
    turnoActual: int
    colorProhibido: str
    tiempo: int
    cartasMovimiento: List[dict]
    cartasFigura: List[dict]
    cartasBloqueadas: List[int]
    cantMovimientosParciales: int    
    
class FiguraSchema(BaseModel):
    idFig: str
    tipoFig: str
    coordenadas: List[Coordenada]

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

class DeshacerMovimiento(BaseModel):
    type: Literal[WebSocketMessageType.DESHACER_MOVIMIENTO]
    posiciones: List[Posicion]
    
class DeshacerMovimientos(BaseModel):
    type: Literal[WebSocketMessageType.DESHACER_MOVIMIENTOS]
    posiciones: List[List[Posicion]]    
    cantMovimientosDesechos: int

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

class DeclararFiguraColorProhibido(BaseModel):
    cartasFig: List[dict]
    colorProhibido : str


class DeclararFiguraSchema(BaseModel):
    type: Literal[WebSocketMessageType.FIGURA_DESCARTAR]
    data: DeclararFiguraColorProhibido
    
    
class ReposicionFiguras(BaseModel):
    type : Literal[WebSocketMessageType.REPOSICION_FIGURAS]
    data: DeclararFiguraDataSchema

    
class ReposicionCartasFiguras(BaseModel):
    type : Literal[WebSocketMessageType.REPOSICION_FIGURAS]
    data: ReposicionFiguras

class ReposicionCartasMovimientos(BaseModel):
    type : Literal[WebSocketMessageType.REPOSICION_MOVIMIENTOS]
    cartas: List[dict]
    
class FinalizarPartidaDataSchema(BaseModel):
    idGanador: int
    nombreGanador: str

class FinalizarPartidaSchema(BaseModel):
    type: Literal[WebSocketMessageType.PARTIDA_FINALIZADA]
    data: FinalizarPartidaDataSchema    


class BloquearFiguraDataSchema(BaseModel):
    idCarta: int
    idJugador: int
    colorProhibido: str

class BloquearFiguraSchema(BaseModel):
    type: Literal[WebSocketMessageType.BLOQUEAR_FIGURA]
    data: BloquearFiguraDataSchema

class DesbloquearFiguraDataSchema(BaseModel):
    idCarta: int
    idJugador: int
    colorProhibido: str

class DesbloquearFiguraSchema(BaseModel):
    type: Literal[WebSocketMessageType.DESBLOQUEAR_FIGURA]
    data: DesbloquearFiguraDataSchema

class MensajeSchema(BaseModel):
    type: Literal[WebSocketMessageType.MENSAJE_ENVIADO]
    mensaje: str