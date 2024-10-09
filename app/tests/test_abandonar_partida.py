import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.partida_service import PartidaService
from app.db.models import (
    Base, 
    Partida,
    Jugador,
    Jugador_Partida
)

@pytest.fixture(scope='module')
def test_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)  # Crea todas las tablas definidas en Base
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()



def test_abandonar_partida(setup_data, test_db):

    jugador1 = Jugador(nombre="Jugador 1", id=1)
    jugador2 = Jugador(nombre="Jugador 2", id=2)
    jugador3 = Jugador(nombre="Jugador 3", id=3)
    partida = Partida(nombre="Partida1", min=2, max=4, id_owner=1)

    test_db.add(jugador1)
    test_db.add(jugador2)
    test_db.add(jugador3)
    test_db.add(partida)
    test_db.commit()

    jugador_partida1 = Jugador_Partida(id_jugador=jugador1.id, id_partida=partida.id)
    jugador_partida2 = Jugador_Partida(id_jugador=jugador2.id, id_partida=partida.id)
    jugador_partida3 = Jugador_Partida(id_jugador=jugador3.id, id_partida=partida.id)
    test_db.add(jugador_partida1)
    test_db.add(jugador_partida2)
    test_db.add(jugador_partida3)
    test_db.commit()
    jugador_id = jugador_partida3.id_jugador
    partida_id =jugador_partida3.id_partida
    PartidaService.abandonar_partida(jugador_id, partida_id, test_db)

    # Verificar que relación Jugador_Partida ha sido eliminada
    relacion_abandonada = test_db.query(Jugador_Partida).filter(
        Jugador_Partida.id_jugador == jugador_id,
        Jugador_Partida.id_partida == partida_id
    ).first()
    assert relacion_abandonada is None

    # Verificar que jugador todavía existe
    jugador_existente = test_db.query(Jugador).filter(Jugador.id == jugador_id).first()
    assert jugador_existente is not None

    # Verificar que partida todavía existe
    partida_existente = test_db.query(Partida).filter(Partida.id == partida_id).first()
    assert partida_existente is not None

    