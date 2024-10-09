import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker 
from app.db.base import engine
from app.db.models import *
from app.schema.partida_schema import *
from app.services.partida_service import PartidaService
from app.main import app  

Session = sessionmaker(bind=engine)

client = TestClient(app)  


@pytest.fixture
def partida_test():
    return CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida 1',
        cant_min_jugadores=2,
        cant_max_jugadores=4
    )

@pytest.fixture
def partida_service():
    return PartidaService()

@pytest.mark.asyncio
async def test_abandonar_partida_exitoso(partida_service: PartidaService, partida_test):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 2', session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 3', session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200

        # Abandonar la partida
        response = client.post(
             f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response.status_code == 202

        assert response.json() == {"detail": f"Jugador {partida_creada.id_jugador} ha abandonado la partida {partida_creada.id_partida}"}

        # Verificar que la relación Jugador_Partida ha sido eliminada
        relacion_abandonada = session.query(Jugador_Partida).filter(
            Jugador_Partida.id_jugador == partida_creada.id_jugador,
            Jugador_Partida.id_partida == partida_creada.id_partida
        ).first()
        assert relacion_abandonada is None

        # Verificar que la partida todavía existe
        partida_existente = session.query(Partida).filter(Partida.id == partida_creada.id_partida).first()
        assert partida_existente is not None

    finally:
        session.close()
