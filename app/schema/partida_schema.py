from pydantic import BaseModel, Field, field_validator #field no me anda
from typing import List
from typing import Optional



class CrearPartidaResponse(BaseModel):
    id_partida: str
    #nombre_partida: str
    #esto agrego para devolver el id del jugador 
    id_jugador : str =  None
    


class PartidaResponse(BaseModel):
    id_partida: str
    nombre_partida: str
    #cant_jugadores: str
    cant_min_jugadores: int
    cant_max_jugadores: int
         
    
    
#class PartidasListResponse(BaseModel):
#    partidas: List[PartidaListItem]



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

    """
    @field_validator('cant_max_jugadores')
    def max_jugadores_mayor_que_min(cls, v, values):
        if 'cant_min_jugadores' in info.data and v < info.data['cant_min_jugadores']:
            raise ValueError('La cantidad máxima de jugadores debe ser mayor o igual a la cantidad mínima')
        return v
    """



class UnirsePartidaRequest(BaseModel):
    nombreJugador: str

    @field_validator('nombreJugador')
    def nombreJugador_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre del jugador no puede estar vacío')
        return v


class UnirsePartidaResponse(BaseModel):
    idJugador: int


#class IniciarPartida(UnirsePartidaRequest):
#    id_partida : int
    

class IniciarPartidaResponse(BaseModel):
    id_partida : str