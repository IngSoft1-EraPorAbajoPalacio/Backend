import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.base import engine
from app.db.models import *
from app.services.partida_service import PartidaService
from app.schema.juego_schema import DeclararFiguraRequest, Posicion
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
        cant_max_jugadores=4,
        contrasena=""
    )

@pytest.fixture
def figura_valida():
    return DeclararFiguraRequest(
        idCarta=9,
        tipo_figura=9
    )

@pytest.fixture
def figura_invalida():
    return DeclararFiguraRequest(
        idCarta=9,
        tipo_figura=10
    )

@pytest.mark.asyncio
async def test_declarar_figura(partida_service: PartidaService, partida_test, figura_valida):
    session = Session()
    try:
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine) 
        Base.metadata.create_all(bind=engine)

        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        await partida_service.iniciar_partida(int(partida_creada.id_partida), int(partida_creada.id_jugador), session)
        session.commit()

        # Acomodo las fichas del tablero para la figura 9
        posiciones = []
        fichas_rojas =     [(1, 5), (2, 1), (2, 4), (3, 0), (3, 1), (3, 5), (4, 1), (4, 2), (4, 4)]
        fichas_verdes =    [(0, 0), (2, 0), (2, 3), (2, 5), (3, 2), (3, 4), (5, 2), (5, 4), (5, 5)]
        fichas_azules =    [(0, 2), (0, 4), (0, 5), (1, 0), (2, 2), (3, 3), (4, 3), (5, 0), (5, 1)]
        fichas_amarillas = [(0, 1), (0, 3), (1, 1), (1, 2), (1, 3), (1, 4), (4, 0), (4, 5), (5, 3)]
        
        all_fichas = [
            (x, y, "Rojo") for x, y in fichas_rojas
        ] + [
            (x, y, "Verde") for x, y in fichas_verdes
        ] + [
            (x, y, "Azul") for x, y in fichas_azules
        ] + [
            (x, y, "Amarillo") for x, y in fichas_amarillas
        ]
        all_fichas.sort()  # Ordeno las fichas
        for x, y, color in all_fichas:
            posiciones.append(Ficha(x=x, y=y, color=color, id_tablero=partida_creada.id_partida))
        session.add_all(posiciones)
        session.commit()

        # Asigno figura 9 al jugador 
        figura = session.query(Figuras).filter(Figuras.id == figura_valida.idCarta).first()
        session.query(Jugador).filter(Jugador.id == partida_creada.id_jugador).first().cartas_de_figuras[0].carta_fig = figura.id
        session.query(Jugador).filter(Jugador.id == partida_creada.id_jugador).first().cartas_de_figuras[0].en_mano = True
        session.query(Jugador).filter(Jugador.id == partida_creada.id_jugador).first().cartas_de_figuras[0].figura.fig = figura.fig
        session.commit()

        # Declarar figura
        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}/tablero/declarar-figura",
            json=figura_valida.model_dump()
        )
        print(f"Response: {response.json()}")
        assert response.status_code == 202
        session.commit()
        cf = session.query(CartasFigura).filter(
            CartasFigura.id_jugador == partida_creada.id_jugador,
            CartasFigura.carta_fig == figura.id).first()
        assert cf == None
    finally:
        session.close()

@pytest.mark.asyncio
async def test_declarar_figura_carta_invalida(partida_service: PartidaService, partida_test, figura_invalida):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        await partida_service.iniciar_partida(int(partida_creada.id_partida), int(partida_creada.id_jugador), session)
        session.commit()

        # Asigno figura 9 al jugador 
        figura = session.query(Figuras).filter(Figuras.id == figura_invalida.idCarta).first()
        session.query(Jugador).filter(Jugador.id == partida_creada.id_jugador).first().cartas_de_figuras[0].carta_fig = figura.id
        session.query(Jugador).filter(Jugador.id == partida_creada.id_jugador).first().cartas_de_figuras[0].en_mano = True
        session.query(Jugador).filter(Jugador.id == partida_creada.id_jugador).first().cartas_de_figuras[0].figura.fig = figura.fig
        session.commit()

        # Declarar figura
        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}/tablero/declarar-figura",
            json=figura_invalida.model_dump()
        )
        print(f"Response: {response.json()}")
        assert response.status_code == 432
        session.commit()
        assert session.query(CartasFigura).filter(
            CartasFigura.id_jugador == partida_creada.id_jugador,
            CartasFigura.carta_fig == figura.id
        ).first().en_mano == True

    finally:
        session.close()

@pytest.mark.asyncio
async def test_declarar_figura_jugador_invalido(partida_service: PartidaService, partida_test, figura_valida):
    session = Session()
    try:
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()
        
        # Declarar figura
        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/999/tablero/declarar-figura",
            json=figura_valida.model_dump()
        )
        assert response.status_code == 404
    finally:
        session.close()