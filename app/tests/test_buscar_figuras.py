from app.services.encontrar_fig import encontrar_figuras, agrupar_fichas, obtener_grupos_adyacentes, is_fig1, normalizar_posiciones
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_db1():
    # Create a MagicMock for the database session 
    return MagicMock()

def test_encontrar_figuras1(mock_db1, monkeypatch):
    # Mock data that simulates the output of obtener_fichas
    mock_fichas = [
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
    ]

    print("\n--- Mock Data ---")
    for ficha in mock_fichas:
        print(ficha)

    def mock_obtener_fichas(id_partida, db):
        print("\nMock obtener_fichas called")
        return mock_fichas

    # Use monkeypatch to replace obtener_fichas in ficha_service with the mock version
    monkeypatch.setattr('app.services.ficha_service.obtener_fichas', mock_obtener_fichas)

    listaFig = [1]  
    resultado = encontrar_figuras(1, listaFig, mock_db1)
    
    # Debug output for the test
    print("\n--- DEBUG: Resultado de encontrar_figuras ---")
    print(f"Figuras encontradas: {resultado}")

    assert len(resultado) == 4, f"Expected 3 figures, but found {len(resultado)}"