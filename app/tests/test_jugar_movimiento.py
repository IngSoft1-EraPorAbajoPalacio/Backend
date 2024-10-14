import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.base import engine
from app.db.models import *
from app.services.partida_service import PartidaService
from app.schema.juego_schema import JugarMovimientoRequest, Posicion
from app.schema.partida_schema import CrearPartida
from app.main import app

client = TestClient(app)

Session = sessionmaker(bind=engine)

@pytest.fixture
def partida_service():
    return PartidaService()

@pytest.fixture
def partida_test():
    return CrearPartida(
        nombre_host='Jugador 1',
        nombre_partida='Partida 1',
        cant_min_jugadores=2,
        cant_max_jugadores=4
    )

@pytest.fixture
def movimiento_request():
    return JugarMovimientoRequest(
        idCarta=1,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=2, y=2)
        ]
    )

@pytest.fixture
def movimiento_invalido():
    return JugarMovimientoRequest(
        idCarta=999,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=2, y=2)
        ]
    )

@pytest.mark.asyncio
async def test_jugar_movimiento(partida_service: PartidaService, partida_test, movimiento_request):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()
        jugador = session.query(Tablero).filter(Tablero.id_partida == partida_creada.id_partida).first().turno
        
        # Realizar movimiento
        response = client.patch(
            f"/partida/{partida_creada.id_partida}/jugador/{jugador}/tablero/jugar-movimiento",
            json=movimiento_request.model_dump()
        )
        assert response.status_code == 202
        response_data = response.json()
        assert response_data['type'] == "MovimientoParcial"
        assert response_data['carta']['id'] == movimiento_request.idCarta

    finally:
        session.close()

@pytest.mark.asyncio
async def test_jugar_movimiento_id_invalido(partida_service: PartidaService, partida_test, movimiento_invalido):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()
        jugador = session.query(Tablero).filter(Tablero.id_partida == partida_creada.id_partida).first().turno
        
        # Realizar movimiento
        response = client.patch(
            f"/partida/{partida_creada.id_partida}/jugador/{jugador}/tablero/jugar-movimiento",
            json=movimiento_invalido.model_dump()
        )
        assert response.status_code == 404

    finally:
        session.close()

@pytest.mark.asyncio
async def test_jugar_movimiento_turno_incorrecto(partida_service: PartidaService, partida_test, movimiento_request):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()
        
        # Realizar movimiento
        response = client.patch(
            f"/partida/{partida_creada.id_partida}/jugador/999/tablero/jugar-movimiento",
            json=movimiento_request.model_dump()
        )
        assert response.status_code == 404

    finally:
        session.close()