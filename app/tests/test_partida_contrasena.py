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
def crear_session():
    db = Session()
    try:
        yield db
    finally:
        db.close()  

@pytest.fixture
def partida_test():
    return CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida 1',
        cant_min_jugadores=2,
        cant_max_jugadores=4,
        contrasena="lucas"
    )

@pytest.fixture
def unirse_válido():
    return UnirsePartidaRequest(
        nombreJugador='Jugador de prueba',
        contrasena="lucas"
    )
    
@pytest.fixture
def unirse_inválido():
    return UnirsePartidaRequest(
        nombreJugador='Jugador de prueba',
        contrasena="juan"
    )

@pytest.mark.asyncio
async def test_unirse_partida_válida(crear_session, partida_service: PartidaService, partida_test, unirse_válido):
        session = crear_session
        
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine) 
        Base.metadata.create_all(bind=engine)
        
        partida_creada = await partida_service.crear_partida(partida_test, session)

        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador",
            json=unirse_válido.model_dump()
        )
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_unirse_partida_inválida(crear_session, partida_service: PartidaService, partida_test, unirse_inválido):
        session = crear_session
        
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine) 
        Base.metadata.create_all(bind=engine)
        
        partida_creada = await partida_service.crear_partida(partida_test, session)

        response = client.post(
            f"/partida/{partida_creada.id_partida}/jugador",
            json=unirse_inválido.model_dump()
        )
        assert response.status_code == 450
