from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey
from typing import List,Optional
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship,Mapped,mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Jugador(Base) :
   
    __tablename__ = "Jugadores"

    id = Column(Integer, primary_key=True, autoincrement= True)
    nickname = Column(String(255))
    partidas = relationship("Jugador_Partida", back_populates='jugador',cascade="all")
    
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(50))
    
    #relaciones
    partidas: Mapped[List["Jugador_Partida"]] = relationship(back_populates='jugador', cascade= "all")
    
    def __repr__(self) -> str:
        return f"Jugador(id = {self.id}, nickname = {self.nickname})"   


class Partida(Base):
    
    __tablename__ = "Partidas"
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    nombre : Mapped[str] = mapped_column(String(40), nullable=False)
    min : Mapped[int] = mapped_column(nullable=False)
    max : Mapped[int] = mapped_column(nullable=False)
    activa : Mapped[bool] = mapped_column(Boolean,nullable=False)
    id_owner : Mapped[int] = mapped_column(nullable=False)
    #turno : Mapped[int] = mapped_column(nullable=False)
    #psw : Mapped[Optional[str]] = mapped_column(String(40),nullable=False)
    
    #relaciones
    jugadores : Mapped[List['Jugador_Partida']] = relationship(back_populates='partida', cascade="all")
    tablero : Mapped['Tablero'] = relationship(back_populates = 'relacion_partida' , uselist=False)
        
    def __repr__(self):
        return f"Partida( id : {self.id}, name : {self.name})"   

    
class Jugador_Partida(Base) :
    
    __tablename__ = "Jugador_Partida"
    
    id_jugador : Mapped[int] = mapped_column(ForeignKey('Jugadores.id'),primary_key=True)
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id'),primary_key=True)
    
    #relaciones
    jugador : Mapped['Jugador'] = relationship(back_populates='partidas')
    partida : Mapped['Partida'] = relationship(back_populates='jugadores')
    
    def __repr__(self):
        return f"Jugador con id {self.id_jugador} se encuentra en Partida con id : {self.id_partida})"   
 

colores = ["rojo","verde","azul","amarillo"] 
Color = PyEnum("Color",colores)


class Tablero(Base):
    
    __tablename__ = "Tableros"
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True) 
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id'))
    color_prohibido : Mapped[Color] = mapped_column(Enum(Color), nullable = True)
    #turno??
    
    
    #relaciones
    relacion_partida : Mapped['Partida'] = relationship(back_populates='tablero')
    fichas : Mapped[List['Ficha']] = relationship(back_populates='relacion_tablero')

    
class Ficha(Base):
    
    __tablename__ = 'Fichas'
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True) # ? 
    x : Mapped[int] = mapped_column(nullable=False)
    y : Mapped[int] = mapped_column(nullable=False)
    color : Mapped[Color] = mapped_column(Enum(Color),nullable=False)
    id_tablero : Mapped[int] = mapped_column(ForeignKey('Tableros.id')) 
    
    #relaciones
    relacion_tablero : Mapped['Tablero'] = relationship(back_populates='fichas')







