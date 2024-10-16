from sqlalchemy import String, Boolean, Enum, ForeignKey
from typing import List
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_base

Base = declarative_base()

class Jugador(Base) :
   
    __tablename__ = "Jugadores"

    partidas = relationship("Jugador_Partida", back_populates='jugador',cascade="all")
    
    id : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(50))
    jugando : Mapped[bool] = mapped_column(default=False)
    
    #relaciones
    partidas: Mapped[List["Jugador_Partida"]] = relationship(back_populates='jugador', cascade= "all")
    cartas_de_figuras : Mapped[List["CartasFigura"]] = relationship(back_populates='jugador_fig', cascade="all")#
    cartas_de_movimientos : Mapped[List["CartaMovimientos"]] = relationship(back_populates='jugador_mov', cascade="all")#

    def __repr__(self) -> str:
        return f"Jugador(id = {self.id}, nickname = {self.nickname})"   
 

class Partida(Base):
    
    __tablename__ = "Partidas"
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    nombre : Mapped[str] = mapped_column(String(40), nullable=False)
    min : Mapped[int] = mapped_column(nullable=False)
    max : Mapped[int] = mapped_column(nullable=False)
    activa : Mapped[bool] = mapped_column(Boolean,default=False)
    id_owner : Mapped[int] = mapped_column(nullable=False)
    
    #relaciones
    jugadores : Mapped[List['Jugador_Partida']] = relationship(back_populates='partida', cascade="all")
    tablero : Mapped['Tablero'] = relationship(back_populates = 'relacion_partida' , cascade="all")
        
    def __repr__(self):
        return f"Partida( id : {self.id}, name : {self.name})"   

    
class Jugador_Partida(Base) :
    
    __tablename__ = "Jugador_Partida"
    
    id_jugador : Mapped[int] = mapped_column(ForeignKey('Jugadores.id', ondelete='CASCADE'),primary_key=True)
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id',ondelete='CASCADE'), primary_key=True)
    
    #relaciones
    jugador : Mapped['Jugador'] = relationship(back_populates='partidas')
    partida : Mapped['Partida'] = relationship(back_populates='jugadores')
    
    def __repr__(self):
        return f"Jugador con id {self.id_jugador} se encuentra en Partida con id : {self.id_partida})"   
 

colores = ["Rojo","Verde","Azul","Amarillo"] 
Color = PyEnum("Color",colores)


class Tablero(Base):
    
    __tablename__ = "Tableros"
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True) 
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id',ondelete='CASCADE'))
    color_prohibido : Mapped[Color] = mapped_column(Enum(Color), nullable = True)
    turno : Mapped[int] = mapped_column(nullable=False)
    
    #relaciones
    relacion_partida : Mapped['Partida'] = relationship(back_populates='tablero')
    fichas : Mapped[List['Ficha']] = relationship(back_populates='relacion_tablero')
    
    
class Ficha(Base):
    
    __tablename__ = 'Fichas'
    
    id : Mapped[int] = mapped_column(primary_key=True,autoincrement=True) # ? 
    x : Mapped[int] = mapped_column(nullable=False)
    y : Mapped[int] = mapped_column(nullable=False)
    color : Mapped[Color] = mapped_column(Enum(Color),nullable=False)
    id_tablero : Mapped[int] = mapped_column(ForeignKey('Tableros.id_partida')) 
    
    #relaciones
    relacion_tablero : Mapped['Tablero'] = relationship(back_populates='fichas')


Figura = PyEnum("Figura", ["1","2","3","4","5","6","7",
                           "8","9","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25"])

Movimiento = PyEnum("Movimiento", ["1","2","3","4","5","6","7"])


class Figuras(Base):
    
    __tablename__ = "Figuras"
    
    id : Mapped[int]  = mapped_column(primary_key=True,autoincrement=True) 
    fig : Mapped[Figura] = mapped_column(Enum(Figura))
    
    #relaciones
    cartas_de_figura: Mapped[List["CartasFigura"]] = relationship(back_populates='figura')

    
class CartasFigura(Base):
    
    __tablename__ = "CartasFiguras"
    
    id : Mapped[int]  = mapped_column(primary_key=True,autoincrement=True) 
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id',ondelete='CASCADE'))
    id_jugador : Mapped[int] = mapped_column(ForeignKey('Jugadores.id',ondelete='CASCADE')) 
    carta_fig : Mapped[int]  = mapped_column(ForeignKey('Figuras.id'))
    en_mano : Mapped[Boolean] = mapped_column(Boolean,nullable=False)

    #relaciones
    jugador_fig: Mapped["Jugador"] = relationship(back_populates='cartas_de_figuras')

    figura: Mapped["Figuras"] = relationship(back_populates='cartas_de_figura')


class Movimientos(Base):
    
    __tablename__ = "Movimientos"
    
    id : Mapped[int]  = mapped_column(primary_key=True,autoincrement=True) 
    mov : Mapped[Movimiento] = mapped_column(Enum(Movimiento), primary_key=True)
    
    #relaciones
    cartas_de_movimiento: Mapped["CartaMovimientos"] = relationship(back_populates='movimiento')


class CartaMovimientos(Base):
    
    __tablename__ = "CartasMovimientos"
    
    id : Mapped[int]  = mapped_column(primary_key=True,autoincrement=True) 
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id',ondelete='CASCADE'))
    id_jugador : Mapped[int] = mapped_column(ForeignKey('Jugadores.id',ondelete='CASCADE'))
    carta_mov : Mapped[int] = mapped_column(ForeignKey('Movimientos.id'))   
    en_mano : Mapped[Boolean] = mapped_column(Boolean,nullable=False) 

    #relaciones
    jugador_mov: Mapped["Jugador"] = relationship(back_populates='cartas_de_movimientos')
    movimiento: Mapped["Movimientos"] = relationship(back_populates='cartas_de_movimiento')


class MovimientosParciales(Base):

    _tablename_ = "MovimientosParciales"
    
    id : Mapped[int]  = mapped_column(primary_key=True,autoincrement=True) 
    id_partida : Mapped[int] = mapped_column(ForeignKey('Partidas.id',ondelete='CASCADE'))
    id_jugador : Mapped[int] = mapped_column(ForeignKey('Jugadores.id',ondelete='CASCADE'))
    movimiento : Mapped[int] = mapped_column(ForeignKey("Movimientos.id"))
    x1 : Mapped[int] = mapped_column(nullable=False)
    y1 : Mapped[int] = mapped_column(nullable=False)
    x2 : Mapped[int] = mapped_column(nullable=False)
    y2 : Mapped[int] = mapped_column(nullable=False)
    




