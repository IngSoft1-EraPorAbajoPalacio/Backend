from pydantic import BaseModel, Field, field_validator
from typing import Optional

class PartidaCreate(BaseModel):
    id_owner : int
    nombre_partida: str
    min: int 
    max: int 
    activa : bool = False
    psw: Optional[str] = None
    

    """
    @field_validator('nombre_host')
    def nombre_host_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre del host no puede estar vacío')
        return v
    """
    
    @field_validator('nombre_partida')
    def nombre_partida_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre de la partida no puede estar vacío')
        return v

    @field_validator('min')
    def min_jugadores_valido(cls, v):
        if v < 2:
            raise ValueError('La cantidad mínima de jugadores debe ser al menos 2')
        return v

    @field_validator('max')
    def max_jugadores_valido(cls, v):
        if v > 4:
            raise ValueError('La cantidad máxima de jugadores no puede ser mayor a 4')
        return v
   
"""
    @field_validator('max')
    def max_jugadores_mayor_que_min(cls, v, values):
        if 'cant_min_jugadores' in values and v < values['cant_min_jugadores']:
            raise ValueError('La cantidad máxima de jugadores debe ser mayor o igual a la cantidad mínima')
        return v
"""

class PartidaResponse(BaseModel):
    id: int
    nombre: str
    min: int = None
    max: int = None
    


class UnirsePartidaRequest(BaseModel):
    id_jugador: int
    id_partida : int
    
"""    
    @field_validator('id_jugador')
    def id_jugador_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El id del jugador no puede estar vacío')
        return v
    
        
    @field_validator('id_partida')
    def id_jugador_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El id de la partida no puede estar vacío')
        return v
"""


class UnirsePartidaResponse(BaseModel):
    id_jugador: int
    id_partida: int



class IniciarPartida(UnirsePartidaRequest):
    pass

class InicarPartidaResponse(UnirsePartidaRequest):
    pass