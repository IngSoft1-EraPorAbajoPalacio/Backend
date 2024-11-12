import pytest
from sqlalchemy.orm import sessionmaker
from app.db.base import engine
from app.db.models import *
from app.services.partida_service import PartidaService
from app.schema.juego_schema import DeclararFiguraRequest
from app.schema.partida_schema import CrearPartida
from app.services.bd_service import *
from app.services.juego_service import juego_service

Session = sessionmaker(bind=engine)

@pytest.fixture
def crear_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()  

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
        tipo_figura=9,
        color="Azul"
    )

@pytest.mark.asyncio
async def test_color_prohibido(partida_service: PartidaService, partida_test, figura_valida, crear_session):
    session = crear_session
    
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    
    partida_creada = await partida_service.crear_partida(partida_test, session)
    await partida_service.unirse_partida(partida_creada.id_partida, "Jugador 2", "", session)
    await partida_service.iniciar_partida(int(partida_creada.id_partida), int(partida_creada.id_jugador), session)
    
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
    await juego_service.declarar_figura(
        int(partida_creada.id_partida),
        int(partida_creada.id_jugador),
        figura_valida,
        session
    )
    
    assert db_service.obtener_color_prohibido(int(partida_creada.id_partida), session) == "Azul" 

  