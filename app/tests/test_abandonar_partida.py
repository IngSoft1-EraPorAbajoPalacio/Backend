import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, configure_mappers
from app.db.base import engine
from app.db.models import *
from app.schema.partida_schema import *
from app.services.partida_service import PartidaService
from app.main import app  

Session = sessionmaker(bind=engine)

client = TestClient(app)  

# Configurar el mapeador para no confirmar el número de filas eliminadas
configure_mappers()
for mapper in Base.registry.mappers:
    mapper.confirm_deleted_rows = False

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
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine) 
        Base.metadata.create_all(bind=engine)

        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 2', session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 3', session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200

        # Abandonar la partida
        response = client.delete(
             f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response.status_code == 202
        session.commit()

        # Verificar que la relación Jugador_Partida ha sido eliminada
        relacion_abandonada = session.query(Jugador_Partida).filter(
            Jugador_Partida.id_jugador == partida_creada.id_jugador,
            Jugador_Partida.id_partida == partida_creada.id_partida
        ).first()
        assert relacion_abandonada is None

        # Verificar que la partida todavía existe
        partida_existente = session.query(Partida).filter(Partida.id == partida_creada.id_partida).first()
        assert partida_existente is not None

        # Guardar los cambios
        session.commit()

    finally:
        session.close()

@pytest.mark.asyncio
async def test_abandonar_partida_creador_lobby(partida_service: PartidaService, partida_test):
    session = Session()
    try:
        # Crear una partida y unir jugadores
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 2', session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 3', session)
        
        # Abandonar la partida como creador
        response = client.delete(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response.status_code == 202
        session.commit()
        
        # Verificar que la partida ha sido eliminada
        partida_borrada = session.query(Partida).filter(Partida.id == partida_creada.id_partida).first()
        assert partida_borrada is None

        session.commit()
    finally:
        session.close()

@pytest.mark.asyncio
async def test_abandonar_partida_jugador_no_encontrado(partida_service: PartidaService, partida_test):
    session = Session()
    try:
        # Crear una partida y unir un jugador
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 2', session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()
        
        # Intentar abandonar la partida con un jugador no existente
        response = client.delete(
            f"/partida/{partida_creada.id_partida}/jugador/999")
        assert response.status_code == 404
        session.commit()
    finally:
        session.close()
        
@pytest.mark.asyncio
async def test_abandonar_partida_no_existente():
    session = Session()
    try:
        # Intentar abandonar una partida que no existe
        response = client.delete("/partida/999/jugador/1")
        assert response.status_code == 404
    finally:
        session.close()

@pytest.mark.asyncio
async def test_abandonar_partida_no_participante(partida_service: PartidaService, partida_test):
    session = Session()
    try:
        # Crear una partida y unir un jugador
        partida_creada = await partida_service.crear_partida(partida_test, session)
        await partida_service.unirse_partida(partida_creada.id_partida, 'Jugador 2', session)
        response_inicio = client.post(
            f"/partida/{partida_creada.id_partida}/jugador/{partida_creada.id_jugador}")
        assert response_inicio.status_code == 200
        session.commit()

        # Intentar abandonar la partida con un jugador que no es participante
        response = client.delete(
            f"/partida/{partida_creada.id_partida}/jugador/999")
        assert response.status_code == 404

        session.commit()
    finally:
        session.close()