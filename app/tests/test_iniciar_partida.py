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
        cant_max_jugadores=4
    )

@pytest.fixture
def nombre_jugador():
    return UnirsePartidaRequest(
        nombreJugador='Jugador de prueba'
    )

@pytest.mark.asyncio
async def test_iniciar_partida(partida_service: PartidaService, partida_test, nombre_jugador):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, nombre_jugador, session)

        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response.status_code == 200
        response_iniciar = response.json()

        # Chequeo que la partida fue iniciada
        idPartida = response_iniciar['idPartida']
        partida = session.query(Partida).filter(Partida.id == idPartida).first()
        assert partida is not None
        session.commit()

        # Chequeo la cantidad de fichas 
        tablero = session.query(Tablero).filter(Tablero.id_partida == idPartida).first()
        assert tablero is not None
        assert len(tablero.fichas) == 36

        # Chequeo la cantidad de cartas repartidas
        jugadores = session.query(Jugador).join(Jugador_Partida).filter(Jugador_Partida.id_partida == idPartida).all()
        for jugador in jugadores:
            cartas_figuras = session.query(CartasFigura).filter(CartasFigura.id_jugador == jugador.id, CartasFigura.en_mano == True).all()
            cartas_movimientos = session.query(CartaMovimientos).filter(CartaMovimientos.id_jugador == jugador.id, CartaMovimientos.en_mano == True).all()
            assert len(cartas_figuras) == 3
            assert len(cartas_movimientos) == 3
    finally:
        session.close()