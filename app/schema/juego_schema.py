from pydantic import BaseModel, field_validator
from typing import List

class Posicion(BaseModel):
    x: int
    y: int

class JugarMovimientoRequest(BaseModel):
    idCarta: int
    posiciones: List[Posicion]

    @field_validator('idCarta')
    def idCarta_valido(cls, v):
        if v <= 0:
            raise ValueError('El id de la carta debe ser un número positivo')
        return v

    @field_validator('posiciones')
    def posiciones_validas(cls, v):
        if not v:
            raise ValueError('Debe haber al menos una posición')
        return v
