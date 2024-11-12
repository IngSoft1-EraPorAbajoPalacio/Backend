import logging
from collections import defaultdict
from app.services.ficha_service import fichas_service
from typing import List
from app.services.cartas_service import obtener_figuras_en_juego
from operator import index
from sqlalchemy.orm import Session
from app.services.bd_service import *
from app.services.bd_service import *
from app.services.rotaciones import ROTACIONES

def normalizar_posiciones(posiciones):
    """ Normaliza posiciones para arrancar desde (0, 0) """
    if not posiciones:
        return set()
    min_x = min(p[0] for p in posiciones)
    min_y = min(p[1] for p in posiciones)
    return {(x - min_x, y - min_y) for x, y in posiciones}

def es_figura_valida(posiciones, figNum :int ):
    posiciones_normalizadas = normalizar_posiciones(posiciones)
    return any(posiciones_normalizadas == rotacion for rotacion in ROTACIONES.get(figNum, []))

def obtener_grupo_adyacente(posicion, posiciones):
    """ Obtener grupo adyacente de una posición """
    grupo = set()
    pila = [posicion]
    
    while pila:
        pos = pila.pop()
        if pos not in grupo:
            grupo.add(pos)
            # Buscamos fichas vecinas que estén en el conjunto de posiciones
            for vecina in posiciones:
                if vecina not in grupo and son_vecinas(pos, vecina):
                    pila.append(vecina)
    
    return grupo

def obtener_grupos_adyacentes(posiciones):
    """Encontrar todos los grupos adyacentes de un conjunto de posiciones"""
    visitadas = set()
    grupos_adyacentes = []

    for pos in posiciones:
        if pos not in visitadas:
            # Para toda posición no visitada, obtenemos su grupo adyacente
            grupo_adyacente = obtener_grupo_adyacente(pos, posiciones)
            visitadas.update(grupo_adyacente)  # Marcamos como visitadas
            grupos_adyacentes.append(grupo_adyacente)
    
    return grupos_adyacentes

def son_vecinas(pos1, pos2):
    """ Verifica si dos posiciones son ortogonalmente adyacentes """
    return (abs(pos1[0] - pos2[0]) == 1 and pos1[1] == pos2[1]) or \
           (abs(pos1[1] - pos2[1]) == 1 and pos1[0] == pos2[0])

def agrupar_fichas(lista_fichas):
    """ Agrupar fichas por color directamente desde la lista de fichas """
    grupos = defaultdict(list)
    for ficha in lista_fichas:
        x = ficha['x']
        y = ficha['y']
        color = ficha['color']
        grupos[color].append((x, y))  # Agrupa por color y almacena las posiciones
    return grupos

def  encontrar_figuras(id_partida : int, listaFig : List[int], db : Session):
    """ Encontrar las figuras de la listaFig en el tablero de la partida con id = id_partida """
    tablero = fichas_service.obtener_fichas(id_partida, db)
    grupos = agrupar_fichas(tablero)
    figuras = []
    
    for color, posiciones in grupos.items():
        if color == db_service.obtener_color_prohibido(id_partida, db):
            continue
        # Dividimos en grupos adyacentes
        grupos_adyacentes = obtener_grupos_adyacentes(posiciones)

        # Verificamos figuras en cada grupo adyacente
        for grupo in grupos_adyacentes:
            for figNum in listaFig:  # Iteramos sobre la lista de tipos de figura
                if es_figura_valida(grupo, figNum):
                    figuras.append((figNum, color, grupo))

    return figuras

async def computar_y_enviar_figuras(id_partida: int, db: Session):
    try:
        figuras_en_juego = obtener_figuras_en_juego(id_partida, db)
        figuras = encontrar_figuras(id_partida, figuras_en_juego, db)
        
        figuras_data = {
            "type": "DeclararFigura",
            "figuras": {
                "figura": [
                    {
                        "idFig": f"{tipo}_{index}",
                        "tipoFig": tipo,
                        "coordenadas": list(map(lambda pos: [pos[1], pos[0]], posiciones))
                    } for tipo, _, posiciones in figuras
                ]
            }
        } 
        return figuras_data
    except Exception as e:
        logging.error(f"Error al computar figuras para partida {id_partida}: {str(e)}")