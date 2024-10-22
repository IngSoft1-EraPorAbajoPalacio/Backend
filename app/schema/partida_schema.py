from pydantic import BaseModel, field_validator
from typing import List

#### INPUT SCHEMAS ###

class CrearPartida(BaseModel):  
    nombre_host: str
    nombre_partida: str
    cant_min_jugadores: int
    cant_max_jugadores: int
    

    @field_validator('nombre_host')
    def nombre_host_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre del host no puede estar vacío')
        return v

    @field_validator('nombre_partida')
    def nombre_partida_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre de la partida no puede estar vacío')
        return v

    @field_validator('cant_min_jugadores')
    def min_jugadores_valido(cls, v):
        if v < 2:
            raise ValueError('La cantidad mínima de jugadores debe ser al menos 2')
        elif v > 4:
            raise ValueError('La cantidad mínima de jugadores no debe ser mayor que 4')
        return v

    @field_validator('cant_max_jugadores')
    def max_jugadores_valido(cls, v):
        if v > 4:
            raise ValueError('La cantidad máxima de jugadores no puede ser mayor a 4')
        return v


class UnirsePartidaRequest(BaseModel):
    nombreJugador: str

    @field_validator('nombreJugador')
    def nombreJugador_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre del jugador no puede estar vacío')
        return v


### OUTPUT SCHEMAS ###

class CrearPartidaResponse(BaseModel):
    id_partida: str
    nombre_partida: str
    id_jugador: str     


class PartidaResponse(BaseModel):
    id_partida: str
    nombre_partida: str
    cant_min_jugadores: int
    cant_max_jugadores: int
         

class JugadorListado(BaseModel):
    id: str
    nombre: str

class UnirsePartidaResponse(BaseModel):
    idJugador: str
    unidos: List[JugadorListado]


class IniciarPartidaResponse(BaseModel):
    idPartida : str