import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.base import engine
from app.db.models import Partida, Jugador_Partida
from app.services.partida_service import PartidaService
from app.schema.partida_schema import CrearPartida, UnirsePartidaRequest
from app.main import app

client = TestClient(app)  

Session = sessionmaker(bind=engine)

@pytest.fixture
def partida_service():
    return PartidaService()

@pytest.fixture
def partida_test():
    return CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida 1',
        cant_min_jugadores=2,
        cant_max_jugadores=4
    )

@pytest.fixture
def nombre_jugador():
    return UnirsePartidaRequest(
        nombreJugador='Jugador de prueba'
    )

@pytest.mark.asyncio
async def test_unirse_partida(partida_service: PartidaService, partida_test, nombre_jugador):
    session = Session()
    try:
        # Crear la partida de prueba
        partida_creada = partida_service.crear_partida(partida_test, session)

        # Hacer la solicitud POST al endpoint
        
        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador",
            json=nombre_jugador.model_dump()
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data['idJugador'] is not None
        session.commit()
        # Verificar que el número de jugadores en la partida ha aumentado
        partida_actualizada = session.query(Partida).filter(Partida.id == partida_creada.id_partida).first()
        assert len(partida_actualizada.jugadores) == 2
    finally:
        session.close()
