import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app 
from app.schema.partida_schema import CrearPartidaResponse
from app.db.models import *
from sqlalchemy.orm import sessionmaker 
from app.db.base import engine
from app.services.partida_service import partida_service
from app.services.juego_service import juego_service
from app.services.ficha_service import *
from app.schema.partida_schema import *
from app.schema.juego_schema import *
import asyncio

Session = sessionmaker(bind=engine)

client = TestClient(app)

Base.metadata.drop_all(bind=engine) 
Base.metadata.create_all(bind=engine) 

@pytest.fixture
def crear_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()  
    
def movimiento_1(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta=id_movimiento,
        posiciones=[
            Posicion(x=2, y=0),
            Posicion(x=0, y=2)
        ]
    )

def movimiento_2(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta=id_movimiento,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=2, y=0)
        ]
    )

def movimiento_3(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta=id_movimiento,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=1, y=0)
        ]
    )

def movimiento_4(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta=id_movimiento,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=1, y=1)
        ]
    )

def movimiento_5(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta=id_movimiento,
        posiciones=[
            Posicion(x=2, y=0),
            Posicion(x=0, y=1)
        ]
    )

def movimiento_6(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta=id_movimiento,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=2, y=1)
        ]
    )

def movimiento_7(id_movimiento: int):
    return JugarMovimientoRequest(
        idCarta= id_movimiento ,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=4, y=0)
        ]
    )

def switch_case(movimiento: int, id_movimiento):
    jugar_moviento = {
        1: movimiento_1(id_movimiento),
        2: movimiento_2(id_movimiento),
        3: movimiento_3(id_movimiento),
        4: movimiento_4(id_movimiento),
        5: movimiento_5(id_movimiento),
        6: movimiento_6(id_movimiento),
        7: movimiento_7(id_movimiento),
    }
    return jugar_moviento.get(movimiento)


@pytest.mark.asyncio
async def test_deshacer_movimiento(crear_session):

    datos_partida = CrearPartida(  
        nombre_host = "owner1",
        nombre_partida = "partida_test_1",
        cant_min_jugadores = 2,
        cant_max_jugadores = 4
     )
    
    db = crear_session
    
    await partida_service.crear_partida(datos_partida, db)
    await partida_service.unirse_partida("1", "j1", db)
    await partida_service.unirse_partida("1", "j2", db)
    partida_iniciada = await partida_service.iniciar_partida(1, 1, db)
    
    tablero_inicial = partida_iniciada["fichas"]
    
    id_movimientos_en_mano = obtener_id_movimientos_en_mano(1, 1, db)
    
    movimientos_en_mano = obtener_movimientos_en_mano(1, 1, db)
    
    primer_id = id_movimientos_en_mano[0]
    print(f"el id de la carta de movimiento es : {primer_id}")
    
    primera_figura = movimientos_en_mano[0]
    print(f"la figura relacionada al id : {primer_id} es : {primera_figura}")
    

    jugar_mov = switch_case(primera_figura, primer_id)
    print(f"la jugada que voy a hacer es : {jugar_mov}")

    await juego_service.jugar_movimiento(1, 1, jugar_mov, db)

    fichas_actualizadas = juego_service.deshacer_movimiento(1, 1, db)

    assert tablero_inicial == fichas_actualizadas
    assert db.query(MovimientosParciales).count() == 0


@pytest.mark.asyncio
async def test_deshacer_movimientos(crear_session):

    datos_partida = CrearPartida(  
        nombre_host = "owner2",
        nombre_partida = "partida_test_2",
        cant_min_jugadores = 2,
        cant_max_jugadores = 4
     )
    
    db = crear_session
    
    await partida_service.crear_partida(datos_partida, db)
    await partida_service.unirse_partida("2", "j3", db)
    await partida_service.unirse_partida("2", "j4", db)
    partida_iniciada = await partida_service.iniciar_partida(2, 4, db)
    
    tablero_inicial = partida_iniciada["fichas"]
    
    id_movimientos_en_mano = obtener_id_movimientos_en_mano(2, 4, db)
    
    movimientos_en_mano = obtener_movimientos_en_mano(2, 4, db)
    
    for carta in range(3):
        primer_id = id_movimientos_en_mano[carta]
        print(f"el id de la carta de movimiento es : {primer_id}")

        primera_figura = movimientos_en_mano[carta]
        print(f"la figura relacionada al id : {primer_id} es : {primera_figura}")

        jugar_mov = switch_case(primera_figura, primer_id)
        print(f"la jugada que voy a hacer es : {jugar_mov}")

        await juego_service.jugar_movimiento(2, 4, jugar_mov, db)

    fichas_actualizadas = juego_service.deshacer_movimientos(2, 4, db)

    assert tablero_inicial == fichas_actualizadas
    assert db.query(MovimientosParciales).count() == 0


        