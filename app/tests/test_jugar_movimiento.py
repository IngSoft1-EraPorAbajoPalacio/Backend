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
def movimiento_1():
    return JugarMovimientoRequest(
        idCarta=1,
        posiciones=[
            Posicion(x=1, y=3),
            Posicion(x=3, y=1)
        ]
    )

@pytest.fixture
def movimiento_2():
    return JugarMovimientoRequest(
        idCarta=2,
        posiciones=[
            Posicion(x=2, y=0),
            Posicion(x=0, y=0)
        ]
    )

@pytest.fixture
def movimiento_3():
    return JugarMovimientoRequest(
        idCarta=3,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=1, y=0)
        ]
    )

@pytest.fixture
def movimiento_4():
    return JugarMovimientoRequest(
        idCarta=4,
        posiciones=[
            Posicion(x=1, y=1),
            Posicion(x=0, y=0)
        ]
    )

@pytest.fixture
def movimiento_5():
    return JugarMovimientoRequest(
        idCarta=5,
        posiciones=[
            Posicion(x=0, y=0),
            Posicion(x=2, y=1)
        ]
    )

@pytest.fixture
def movimiento_6():
    return JugarMovimientoRequest(
        idCarta=6,
        posiciones=[
            Posicion(x=2, y=3),
            Posicion(x=1, y=1)
        ]
    )

@pytest.fixture
def movimiento_7():
    return JugarMovimientoRequest(
        idCarta=7,
        posiciones=[
            Posicion(x=3, y=3),
            Posicion(x=5, y=3)
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
async def test_jugar_movimientos(partida_service: PartidaService, partida_test, movimiento_1, movimiento_2, movimiento_3, movimiento_4, movimiento_5, movimiento_6, movimiento_7):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()
        jugador = session.query(Tablero).filter(Tablero.id_partida == partida_creada.id_partida).first().turno

        for movimiento in [movimiento_1, movimiento_2, movimiento_3, movimiento_4, movimiento_5, movimiento_6, movimiento_7]:
            mov = session.query(Movimientos).filter(Movimientos.id == movimiento.idCarta).first()
            session.query(Jugador).filter(Jugador.id == jugador).first().cartas_de_movimientos[0].carta_mov = mov.id
            session.query(Jugador).filter(Jugador.id == jugador).first().cartas_de_movimientos[0].en_mano = True
            session.query(Jugador).filter(Jugador.id == jugador).first().cartas_de_movimientos[0].movimiento.mov = mov.mov
            session.commit()
            color_ficha_1 = session.query(Ficha).filter(Ficha.id_tablero == partida_creada.id_partida, 
                                                        Ficha.x == movimiento.posiciones[0].x,
                                                        Ficha.y == movimiento.posiciones[0].y).first().color
            color_ficha_2 = session.query(Ficha).filter(Ficha.id_tablero == partida_creada.id_partida, 
                                                        Ficha.x == movimiento.posiciones[1].x,
                                                        Ficha.y == movimiento.posiciones[1].y).first().color

            # Realizar movimiento
            response = client.patch(
                f"/partida/{partida_creada.id_partida}/jugador/{jugador}/tablero/jugar-movimiento",
                json=movimiento.model_dump()
            )
            assert response.status_code == 202
            response_data = response.json()
            assert response_data['type'] == "MovimientoParcial"
            assert response_data['carta']['id'] == movimiento.idCarta
            assert response_data['fichas'] == [
                {"x": movimiento.posiciones[1].x, "y": movimiento.posiciones[1].y, "color": color_ficha_1.name},
                {"x": movimiento.posiciones[0].x, "y": movimiento.posiciones[0].y, "color": color_ficha_2.name}
            ]
            session.commit()
            assert session.query(Ficha).filter(Ficha.id_tablero == partida_creada.id_partida, 
                                                        Ficha.x == movimiento.posiciones[0].x,
                                                        Ficha.y == movimiento.posiciones[0].y).first().color == color_ficha_2

            assert session.query(Ficha).filter(Ficha.id_tablero == partida_creada.id_partida, 
                                                        Ficha.x == movimiento.posiciones[1].x,
                                                        Ficha.y == movimiento.posiciones[1].y).first().color == color_ficha_1

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
async def test_jugar_movimiento_turno_incorrecto(partida_service: PartidaService, partida_test, movimiento_1):
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
            json=movimiento_1.model_dump()
        )
        assert response.status_code == 404

    finally:
        session.close()
