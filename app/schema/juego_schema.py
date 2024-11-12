from pydantic import BaseModel, field_validator
from typing import List
from enum import Enum

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

class idMovimiento(int, Enum):
    mov_diagonal_doble = 1
    mov_lineal_doble = 2
    mov_lineal_simple = 3
    mov_diagonal_simple = 4
    mov_L_izq = 5
    mov_L_der = 6
    mov_lineal_lateral = 7

class DeclararFiguraRequest(BaseModel):
    idCarta: int
    tipo_figura: int
    color: str

class MensajeRequest(BaseModel):
    mensaje: str