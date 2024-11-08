import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker 
from app.db.base import engine
from app.db.models import *
from app.schema.partida_schema import *
from app.main import app  

Session = sessionmaker(bind=engine)

client = TestClient(app)  

@pytest.mark.integration_test
def test_crear_partida_bien():
    session = Session()
    try:
        # Borrar las tablas de la base de datos
        Base.metadata.drop_all(bind=engine) 
        Base.metadata.create_all(bind=engine)
        
        N_partidas = session.query(Partida).count()
        partida_data = CrearPartida(
            nombre_host='Jugador1',
            nombre_partida='Partida Test',
            cant_min_jugadores=2,
            cant_max_jugadores=4,
            contrasena=""
        )
        response = client.post("/partida", json=partida_data.model_dump())
        session.commit()
        assert response.status_code == 201
        data = response.json()

        # Verificar que la partida fue creada
        assert data["id_partida"] is not None
        assert data["id_jugador"] is not None
        assert data["nombre_partida"] == partida_data.nombre_partida
        assert session.query(Partida).filter(Partida.contrasena == "").count() == 1
        assert session.query(Partida).count() == N_partidas + 1

    finally:
        session.close()

@pytest.mark.integration_test
def test_identificador_unico():
    partida_data_1 = CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida Test 1',
        cant_min_jugadores=2,
        cant_max_jugadores=4,
        contrasena=""
    )
    partida_data_2 = CrearPartida(
        nombre_host='Jugador2',
        nombre_partida='Partida Test 2',
        cant_min_jugadores=2,
        cant_max_jugadores=4,
        contrasena=""
    )

    response_1 = client.post("/partida", json=partida_data_1.model_dump())
    response_2 = client.post("/partida", json=partida_data_2.model_dump())
    assert response_1.status_code == 201
    assert response_2.status_code == 201

    data_1 = response_1.json()
    data_2 = response_2.json()

    # Verificar que los id de las partidas son distintos
    assert data_1["id_partida"] != data_2["id_partida"]

@pytest.mark.integration_test
def test_menos_de_dos_jugadores_max():
    partida_data = CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida Test',
        cant_min_jugadores=2,
        cant_max_jugadores=1,
        contrasena=""
    )
    response = client.post("/partida", json=partida_data.model_dump())
    assert response.status_code == 400

@pytest.mark.integration_test
def test_min_mayor_que_max_jugadores():
    partida_data = CrearPartida(
        nombre_host='Jugador1',
        nombre_partida='Partida Test',
        cant_min_jugadores=4,
        cant_max_jugadores=2,
        contrasena=""
    )
    response = client.post("/partida", json=partida_data.model_dump())
    assert response.status_code == 400

@pytest.mark.integration_test
def test_partida_con_contrasena():
    session = Session()
    try:
        partida_data = CrearPartida(
            nombre_host='Jugador1',
            nombre_partida='Partida Test',
            cant_min_jugadores=2,
            cant_max_jugadores=4,
            contrasena="1234"
        )
        response = client.post("/partida", json=partida_data.model_dump())
        assert response.status_code == 201
        data = response.json()
        assert data["id_partida"] is not None
        assert data["id_jugador"] is not None
        assert data["nombre_partida"] == partida_data.nombre_partida
        assert session.query(Partida).filter(Partida.contrasena == "1234").count() == 1

    finally:
        session.close()