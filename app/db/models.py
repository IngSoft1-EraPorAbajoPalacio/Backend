from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jugador(Base) :
    """Clase de Jugador

    Args:
        Base (Base): clase base declarativa

    Returns:
        class 'models.Productos': Clase de Jugador
    """
    
    __tablename__ = "Jugadores"

    id = Column(Integer, primary_key=True, autoincrement= True)
    nickname = Column(String(255))
    partidas = relationship("Jugador_Partida", back_populates='jugador',cascade="all")
    
    def __init__(self, id=None, nickname=None) :
        self.id = id
        self.nickname = nickname
        
    def __repr__(self):
        return f"Jugadores({self.id}, {self.nickname})"   

    def __str__(self):
        return self.nickname
    

class Partida(Base):
    
    __tablename__ = "Partidas"
    
    id = Column(Integer, primary_key=True, autoincrement= True)
    name = Column(String(40), nullable=False)
    max = Column(Integer, nullable=False)
    min = Column(Integer,nullable=False)
    activa = Column(Boolean, nullable=True)
    psw = Column(String(15), nullable=True)
    turno = Column(Integer,nullable=True)
    jugadores = relationship("Jugador_Partida",back_populates='partida')

    
    def __init__(self, name,min, max, id=None, activa=None , psw=None,turno=None) :
        self.id = id
        self.name = name
        self.min = min
        self.max = max
        self.activa = activa
        self.psw = psw
        self.turno = turno
        
    def __repr__(self):
        return f"Partidas({self.id}, {self.name})"   

    def __str__(self):
        return self.name
    
    
class Jugador_Partida(Base) :
    
    __tablename__ = "Jugador_Partida"
    
    id_jugador = Column(Integer,ForeignKey('Jugadores.id'), primary_key=True, ) 
    id_partida = Column(Integer,ForeignKey('Partidas.id') ,primary_key=True)
    jugador = relationship("Jugador",back_populates = 'partidas')
    partida = relationship("Partida",back_populates = 'jugadores')
    
     
    def __init__(self, id_jugador,id_partida) :
        self.id_jugador = id_jugador
        self.id_partida = id_partida
    
    def __repr__(self):
        return f"Jugadores - Partidas({self.id_jugador}, {self.id_partida})"   
    
    def __str__(self):
        return self.id_partida
