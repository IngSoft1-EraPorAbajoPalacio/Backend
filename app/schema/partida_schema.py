from pydantic import BaseModel, Field, validator
from typing import List
from typing import Optional

class PartidaListItem(BaseModel):
    id_patida: str
    nombrePartida: str
    cantJugadores: int
    
class PartidasListResponse(BaseModel):
    partidas: List[PartidaListItem]

class PartidaCreate(BaseModel):
    id_host: str  
    nombre_host: str
    nombre_partida: str
    cant_min_jugadores: int
    cant_max_jugadores: int

    @validator('nombre_host')
    def nombre_host_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre del host no puede estar vacío')
        return v

    @validator('nombre_partida')
    def nombre_partida_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre de la partida no puede estar vacío')
        return v

    @validator('cant_min_jugadores')
    def min_jugadores_valido(cls, v):
        if v < 2:
            raise ValueError('La cantidad mínima de jugadores debe ser al menos 2')
        return v

    @validator('cant_max_jugadores')
    def max_jugadores_valido(cls, v):
        if v > 4:
            raise ValueError('La cantidad máxima de jugadores no puede ser mayor a 4')
        return v

    @validator('cant_max_jugadores')
    def max_jugadores_mayor_que_min(cls, v, values):
        if 'cant_min_jugadores' in values and v < values['cant_min_jugadores']:
            raise ValueError('La cantidad máxima de jugadores debe ser mayor o igual a la cantidad mínima')
        return v

class PartidaResponse(BaseModel):
    id_partida: str
    nombre_partida: str
    cant_jugadores: int

class UnirsePartidaRequest(BaseModel):
    nombreJugador: str

    @validator('nombreJugador')
    def nombreJugador_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre del jugador no puede estar vacío')
        return v


class UnirsePartidaResponse(BaseModel):
    idJugador: int
