import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.schema.websocket_schema import *
from app.services.partida_service import PartidaService
from app.schema.partida_schema import CrearPartida
from app.db.base import engine
from app.db.models import *
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

@pytest.mark.asyncio
async def test_enviar_mensaje(partida_service: PartidaService, partida_test):
    session = Session()
    try:
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        partida = await partida_service.crear_partida(partida_test, session)
        mensaje_request = MensajeSchema(
            type=WebSocketMessageType.MENSAJE_ENVIADO,
            mensaje="Hola a todos"
        )

        response = client.post(
            f"/partida/{partida.id_partida}/jugador/{partida.id_jugador}/mensaje", json=mensaje_request.model_dump())
        assert response.status_code == 202
    finally:
        session.close()