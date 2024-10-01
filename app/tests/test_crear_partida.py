import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker 
from app.db.base import engine
from app.db.models import *
from app.services.partida_service import PartidaService
from app.schema.partida_schema import *
from app.main import app  

Session = sessionmaker(bind=engine)

client = TestClient(app)  

@pytest.fixture
def partida_service():
    return PartidaService()

@pytest.fixture
def partida_data():
    return CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida Test',
        cant_min_jugadores=2,
        cant_max_jugadores=4
    )


@pytest.mark.integration_test
def test_create_partida(partida_service: PartidaService, partida_data):

    session = Session()
    try:
        N_partidas = session.query(Partida).count()
        
        partida_service.crear_partida(partida_data, session)
        
        assert session.query(Partida).count() == N_partidas + 1

    finally:
        session.close()


@pytest.mark.integration_test
def test_crear_partida_endpoint(partida_data):

    response = client.post("/partida", json=partida_data.model_dump())

    assert response.status_code == 201
    data = response.json()
    assert data["id_partida"] is not None 
    assert data["id_jugador"] is not None 
