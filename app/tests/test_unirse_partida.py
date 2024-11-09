import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.base import engine
from app.db.models import *
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
        cant_max_jugadores=4,
        contrasena=""
    )

@pytest.fixture
def nombre_jugador():
    return UnirsePartidaRequest(
        nombreJugador='Jugador de prueba',
        contrasena=""
    )

@pytest.mark.asyncio
async def test_unirse_partida(partida_service: PartidaService, partida_test, nombre_jugador):
    session = Session()
    try:
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine) 
        Base.metadata.create_all(bind=engine)
        
        partida_creada = await partida_service.crear_partida(partida_test, session)

        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador",
            json=nombre_jugador.model_dump()
        )
        assert response.status_code == 201
        response_data = response.json()
        assert response_data['idJugador'] is not None
        session.commit()

        # Verificar que el número de jugadores sea el correcto
        partida_actualizada = session.query(Partida).filter(Partida.id == partida_creada.id_partida).first()
        assert len(partida_actualizada.jugadores) == 2
    finally:
        session.close()

@pytest.mark.asyncio
async def test_unirse_partida_id_invalido(nombre_jugador):
    response = client.post(
        "/partida/999/jugador",
        json=nombre_jugador.model_dump()
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_unirse_partida_iniciada(partida_service: PartidaService, partida_test, nombre_jugador):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", "", session)
        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response.status_code == 200

        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador",
            json=nombre_jugador.model_dump()
        )
        assert response.status_code == 404
    finally:
        session.close()
    
@pytest.mark.asyncio
async def test_unirse_partida_llena(partida_service: PartidaService, partida_test, nombre_jugador):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", "", session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 3", "", session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 4", "", session)

        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador",
            json=nombre_jugador.model_dump()
        )
        assert response.status_code == 404
        response_data = response.json()
        assert response_data['detail'] == "La partida está llena"

    finally:
        session.close()
