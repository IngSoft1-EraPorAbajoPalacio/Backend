import pytest
from sqlalchemy.orm import sessionmaker 
from fastapi.testclient import TestClient
from app.db.base import engine
from app.db.models import Partida
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


@pytest.mark.integration_test
def test_listar_partidas(partida_service: PartidaService, partida_1, partida_2):
    session = Session()

    # Crear algunas partidas de prueba
    partida_service.crear_partida(partida_1, session)
    partida_service.crear_partida(partida_2, session)
    
    # Hacer una solicitud GET al endpoint
    response = client.get("/partidas")
    assert response.status_code == 200
    partidas_json = response.json()

    N_partidas = session.query(Partida).count()
    assert len(partidas_json) == N_partidas
 