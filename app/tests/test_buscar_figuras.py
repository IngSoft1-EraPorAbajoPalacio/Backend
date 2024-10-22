import logging
from app.services.encontrar_fig import encontrar_figuras
import pytest
from unittest.mock import MagicMock
from app.services.ficha_service import fichas_service

def imprimir_tablero(lista_fichas):
    """Imprimir el tablero a partir de la lista de fichas"""
    tablero = [[' ' for _ in range(6)] for _ in range(6)]  
    for ficha in lista_fichas:
        x = ficha['x']
        y = ficha['y']
        color = ficha['color']
        
        if color == "Azul":
            tablero[x][y] = "A"
        elif color == "Rojo":
            tablero[x][y] = "R"
        elif color == "Verde":
            tablero[x][y] = "V"
        elif color == "Amarillo":
            tablero[x][y] = "Y"  

    for fila in tablero:
        print(' '.join(fila))
    print()

@pytest.fixture
def mock_db(monkeypatch):
    def _mock_db(db_mock):
        def mock_obtener_fichas(id_partida, db):
            return db_mock
        
        monkeypatch.setattr(fichas_service, "obtener_fichas", mock_obtener_fichas)

    return _mock_db

def test_encontrar_figuras(mock_db):
    test_cases = [
        {
            "db_mock": [
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Rojo"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Verde"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Verde"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Verde"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Verde"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Verde"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Verde"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Verde"},
                {"x": 4, "y": 4, "color": "Verde"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Verde"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 1,
            "expected_count": 4,
            "figura_esperada": 1
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Rojo"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Rojo"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Verde"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Verde"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Verde"},
                {"x": 2, "y": 5, "color": "Verde"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Verde"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Verde"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Verde"},
                {"x": 4, "y": 3, "color": "Verde"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 2,
            "expected_count": 4,
            "figura_esperada": 2
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Rojo"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Verde"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Verde"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Verde"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Verde"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Verde"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Verde"},
                {"x": 3, "y": 5, "color": "Verde"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Verde"},
                {"x": 4, "y": 3, "color": "Verde"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Verde"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 3,
            "expected_count": 4,
            "figura_esperada": 3
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Rojo"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Verde"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 4,
            "expected_count": 2,
            "figura_esperada": 5
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Rojo"},
                {"x": 0, "y": 1, "color": "Rojo"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Verde"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Rojo"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Verde"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Verde"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Verde"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Verde"},
                {"x": 4, "y": 2, "color": "Verde"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 5,
            "expected_count": 3,
            "figura_esperada": 6
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Rojo"},
                {"x": 0, "y": 5, "color": "Rojo"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 5,
            "expected_count": 1,
            "figura_esperada": 6
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Rojo"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Verde"},
                {"x": 1, "y": 4, "color": "Verde"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Verde"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 6,
            "expected_count": 2,
            "figura_esperada": 19
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Rojo"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Verde"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Rojo"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Verde"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 7,
            "expected_count": 2,
            "figura_esperada": 21
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Rojo"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Rojo"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Verde"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Verde"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Verde"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Verde"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 8,
            "expected_count": 4,
            "figura_esperada": 22
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Verde"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Verde"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Verde"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Verde"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 9,
            "expected_count": 4,
            "figura_esperada": 23
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Rojo"},
                {"x": 0, "y": 1, "color": "Rojo"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Rojo"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Rojo"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Verde"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Verde"},
                {"x": 3, "y": 2, "color": "Verde"},
                {"x": 3, "y": 3, "color": "Verde"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Verde"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Verde"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 10,
            "expected_count": 2,
            "figura_esperada": 24
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Verde"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 11,
            "expected_count": 4,
            "figura_esperada": 25
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Rojo"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Verde"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Verde"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Verde"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Verde"},
                {"x": 4, "y": 4, "color": "Verde"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 12,
            "expected_count": 4,
            "figura_esperada": 15
        },
                {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Rojo"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Verde"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Verde"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Verde"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Verde"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Verde"},
                {"x": 4, "y": 4, "color": "Verde"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 13,
            "expected_count": 4,
            "figura_esperada": 18
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Rojo"},
                {"x": 0, "y": 1, "color": "Rojo"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Rojo"},
                {"x": 0, "y": 5, "color": "Rojo"},
                {"x": 1, "y": 0, "color": "Rojo"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Verde"},
                {"x": 2, "y": 2, "color": "Verde"},
                {"x": 2, "y": 3, "color": "Verde"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Verde"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 14,
            "expected_count": 1,
            "figura_esperada": 17
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Verde"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Verde"},
                {"x": 0, "y": 5, "color": "Verde"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Rojo"},
                {"x": 1, "y": 2, "color": "Verde"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Verde"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Verde"},
                {"x": 2, "y": 5, "color": "Verde"},
                {"x": 3, "y": 0, "color": "Verde"},
                {"x": 3, "y": 1, "color": "Verde"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Verde"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Verde"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Verde"},
                {"x": 5, "y": 0, "color": "Verde"},
                {"x": 5, "y": 1, "color": "Verde"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Verde"},
                {"x": 5, "y": 4, "color": "Verde"},
                {"x": 5, "y": 5, "color": "Verde"}
            ],
            "numero_de_test": 15,
            "expected_count": 4,
            "figura_esperada": 16
        },
        {
            "db_mock":[
                {"x": 0, "y": 0, "color": "Verde"},
                {"x": 0, "y": 1, "color": "Verde"},
                {"x": 0, "y": 2, "color": "Rojo"},
                {"x": 0, "y": 3, "color": "Rojo"},
                {"x": 0, "y": 4, "color": "Rojo"},
                {"x": 0, "y": 5, "color": "Rojo"},
                {"x": 1, "y": 0, "color": "Verde"},
                {"x": 1, "y": 1, "color": "Verde"},
                {"x": 1, "y": 2, "color": "Rojo"},
                {"x": 1, "y": 3, "color": "Rojo"},
                {"x": 1, "y": 4, "color": "Rojo"},
                {"x": 1, "y": 5, "color": "Rojo"},
                {"x": 2, "y": 0, "color": "Rojo"},
                {"x": 2, "y": 1, "color": "Rojo"},
                {"x": 2, "y": 2, "color": "Rojo"},
                {"x": 2, "y": 3, "color": "Rojo"},
                {"x": 2, "y": 4, "color": "Rojo"},
                {"x": 2, "y": 5, "color": "Rojo"},
                {"x": 3, "y": 0, "color": "Rojo"},
                {"x": 3, "y": 1, "color": "Rojo"},
                {"x": 3, "y": 2, "color": "Rojo"},
                {"x": 3, "y": 3, "color": "Rojo"},
                {"x": 3, "y": 4, "color": "Rojo"},
                {"x": 3, "y": 5, "color": "Rojo"},
                {"x": 4, "y": 0, "color": "Rojo"},
                {"x": 4, "y": 1, "color": "Rojo"},
                {"x": 4, "y": 2, "color": "Rojo"},
                {"x": 4, "y": 3, "color": "Rojo"},
                {"x": 4, "y": 4, "color": "Rojo"},
                {"x": 4, "y": 5, "color": "Rojo"},
                {"x": 5, "y": 0, "color": "Rojo"},
                {"x": 5, "y": 1, "color": "Rojo"},
                {"x": 5, "y": 2, "color": "Rojo"},
                {"x": 5, "y": 3, "color": "Rojo"},
                {"x": 5, "y": 4, "color": "Rojo"},
                {"x": 5, "y": 5, "color": "Rojo"}
            ],
            "numero_de_test": 16,
            "expected_count": 1,
            "figura_esperada": 20
        }

    ]

    for case in test_cases:
        mock_db(case["db_mock"])
        imprimir_tablero(case["db_mock"])
        figuras_encontradas = encontrar_figuras(1, [case["figura_esperada"]], case["db_mock"])
        if figuras_encontradas:
            for tipo, color, posiciones in figuras_encontradas:
                print(f"- {tipo} de color {color} en posiciones {posiciones}")
        else:
            print("No se encontraron figuras.")
            
        #assert se encontraron 4 figuras del tipo esperado
        assert case["db_mock"] == fichas_service.obtener_fichas(1, case["db_mock"])
        assert len(figuras_encontradas) == case["expected_count"]

        tipos_encontrados = [tipo for tipo, color, posiciones in figuras_encontradas]
        assert all(t == case["figura_esperada"] for t in tipos_encontrados)