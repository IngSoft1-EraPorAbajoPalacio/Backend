import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app 
from app.schema.partida_schema import CrearPartidaResponse
import asyncio

client = TestClient(app)

@pytest.mark.asyncio
async def test_crear_partida_ws():
    
    mock_partida_1 = CrearPartidaResponse(
        id_partida = "1",
        nombre_partida = "partida_1",
        id_jugador= "1"
    )
    
    mock_partida_2 = CrearPartidaResponse(
        id_partida = "2",
        nombre_partida = "partida_2",
        id_jugador= "2"
    )

    # Simulamos 2 conexiones a WebSocket
    with client.websocket_connect("/ws") as websocket1, client.websocket_connect("/ws") as websocket2:
            
            #mockeamos la primer llamada a crear_partida
            
            with patch("app.services.partida_service.PartidaService.crear_partida", return_value = mock_partida_1):
                
                #el primer websocket llama al endpoint de crear partida
                
                response_1 = client.post("/partida",json={
                    "nombre_host": "lucas",
                    "nombre_partida": "partida_1",
                    "cant_min_jugadores": 2,
                    "cant_max_jugadores": 3,
                    "contrasena": " "    
                })

                assert response_1.status_code == 201                
                
                #verifico que los 2 websockets reciban la informacion de la primer partida creada
                
                await asyncio.sleep(0.1)
            
                data_ws_1 = websocket1.receive_json()
                data_ws_2 = websocket2.receive_json()
            
                expected_data = {
                    "type": "AgregarPartida",
                    "data": {
                        "idPartida": 1,
                        "nombrePartida": "partida_1",
                        "cantJugadoresMin": 2,
                        "cantJugadoresMax": 3
                    }
                }
                
                assert data_ws_1 == expected_data
                assert data_ws_2 == expected_data
                
            
            #mockeamos la segunda llamada a crear_partida
            
            with patch("app.services.partida_service.PartidaService.crear_partida", return_value = mock_partida_2):
                
                #el primer websocket llama al endpoint de crear partida
                
                response_2 = client.post("/partida",json={
                    "nombre_host": "mateo",
                    "nombre_partida": "partida_2",
                    "cant_min_jugadores": 3,
                    "cant_max_jugadores": 4,
                    "contrasena": ""     
                })
                assert response_2.status_code == 201
                
                #verifico que los 2 websockets reciban la informacion de la segunda partida creada
            
                await asyncio.sleep(0.1)
                 
                data_ws_1 = websocket1.receive_json()
                data_ws_2 = websocket2.receive_json()
            
                expected_data = {
                    "type": "AgregarPartida",
                    "data": {
                        "idPartida": 2,
                        "nombrePartida": "partida_2",
                        "cantJugadoresMin": 3,
                        "cantJugadoresMax": 4,
                    }
                }
                
                assert data_ws_1 == expected_data
                assert data_ws_2 == expected_data
                
                    