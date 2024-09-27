from app.schema.partida_schema import PartidaCreate, PartidaListItem, UnirsePartidaRequest
from typing import List
import uuid

# Esto es temporal, reemplazar por la base de datos
class Jugador:
    def __init__(self, id: str, nombre: str):
        self.id = id
        self.nombre = nombre

class PartidaService:
    def __init__(self):
        self.partidas = {}

    def crear_partida(self, partida: PartidaCreate) -> str:
        id_partida = str(uuid.uuid4())
        #esto es temporal y debería reemplazarse por una base de datos real
        self.partidas[id_partida] = {
            "id_host": partida.id_host,
            "nombre_host": partida.nombre_host,
            "nombre_partida": partida.nombre_partida,
            "cant_min_jugadores": partida.cant_min_jugadores,
            "cant_max_jugadores": partida.cant_max_jugadores,
            "jugadores": [partida.id_host]
        }
        return id_partida

    def obtener_partida(self, id_partida: str):
        return self.partidas.get(id_partida) 
    
    def listar_partidas(self) -> List[PartidaListItem]:
         return [
            PartidaListItem(
                id_patida=id,
                nombrePartida=info['nombre_partida'],
                cantJugadores=len(info['jugadores'])
            )
            for id, info in self.partidas.items()
        ]
    async def unirse_partida(self, id_partida: str, nombre_jugador: str) -> int:
        id_partida = id_partida.strip().strip('"')
        if id_partida not in self.partidas:
            raise ValueError("La partida no existe")
        
        partida = self.partidas[id_partida]
        
        if len(partida["jugadores"]) >= partida["cant_max_jugadores"]:
            raise ValueError("La partida está llena")
        
        nuevo_jugador_id = len(partida["jugadores"]) + 1
        partida["jugadores"].append(nombre_jugador)
        
        return nuevo_jugador_id

# Crea una instancia del servicio que se utilizará en el router.
partida_service = PartidaService()
