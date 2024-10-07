import pytest
from sqlalchemy.orm import sessionmaker 
from fastapi.testclient import TestClient
from app.db.base import engine
from app.db.models import *
from app.services.partida_service import PartidaService
from app.schema.partida_schema import *
from typing import List

from app.main import app  

Session = sessionmaker(bind=engine)

client = TestClient(app)  

@pytest.fixture
def partida_service():
    return PartidaService()

@pytest.fixture
def partida_1():
    return CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida 1',
        cant_min_jugadores=2,
        cant_max_jugadores=4
    )

@pytest.fixture
def partida_2():
    return CrearPartida(
        nombre_host='Jugador2',
        nombre_partida='Partida 2',
        cant_min_jugadores=3,
        cant_max_jugadores=4
    )

@pytest.mark.asyncio
async def test_listar_partidas(partida_service: PartidaService, partida_1, partida_2):
    session = Session()
    try:
        await partida_service.crear_partida(partida_1, session)
        await partida_service.crear_partida(partida_2, session)
        
        response = client.get("/partidas")
        assert response.status_code == 200
        partidas_json = response.json()

        N_partidas = session.query(Partida).count()
        assert len(partidas_json) == N_partidas
    
        # Verificar que las partidas devueltas son las correctas
        partidas = session.query(Partida).all()
        for partida, partida_json in zip(partidas, partidas_json):
            assert partida.nombre == partida_json["nombre_partida"]
            assert partida.min == partida_json["cant_min_jugadores"]
            assert partida.max == partida_json["cant_max_jugadores"]
            assert partida.id == int(partida_json["id_partida"])
    finally:
        session.close()

@pytest.mark.asyncio
async def test_listar_partidas_vacia(partida_service: PartidaService):
    session = Session()
    try:
        session.query(Ficha).delete()
        session.query(CartaMovimientos).delete()
        session.query(CartasFigura).delete()
        session.query(Jugador_Partida).delete()
        session.query(Tablero).delete()
        session.query(Partida).delete()
        session.commit()
        
        response = client.get("/partidas")
        assert response.status_code == 200
        partidas_json = response.json()

        # Verificar que la lista de partidas está vacía
        assert len(partidas_json) == 0
    finally:
        session.close()