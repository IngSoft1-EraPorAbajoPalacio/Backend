from collections import defaultdict
from app.services.ficha_service import obtener_fichas
import random
from typing import List, Set, Tuple
from sqlalchemy.orm import Session


def imprimir_tablero(lista_fichas):
    """Imprimir el tablero a partir de la lista de fichas"""
    tablero = [[' ' for _ in range(6)] for _ in range(6)]  # Crea un tablero vacío de 6x6
    for ficha in lista_fichas:
        x = ficha['x']
        y = ficha['y']
        color = ficha['color']
        # Usar las iniciales según el color
        if color == "Azul":
            tablero[y][x] = "A"
        elif color == "Rojo":
            tablero[y][x] = "R"
        elif color == "Verde":
            tablero[y][x] = "V"
        elif color == "Amarillo":
            tablero[y][x] = "Y"  # Suponiendo "Y" para Amarillo

    for fila in tablero:
        print(' '.join(fila))
    print()

def normalizar_posiciones(posiciones):
    """Normalize positions to start from (0, 0)"""
    if not posiciones:
        return set()
    min_x = min(p[0] for p in posiciones)
    min_y = min(p[1] for p in posiciones)
    return {(x - min_x, y - min_y) for x, y in posiciones}

    
def es_figura_valida(posiciones, figNum :int ):
    posiciones_normalizadas = normalizar_posiciones(posiciones)
    """
    TODO : añadir los 24 casos
    case figNum = 1 :
        valid_fig1(posiciones)
    case figNum = 2 
        valid_fig2(posiciones)
        ...
    """
    return False

def obtener_grupo_adyacente(posicion, posiciones):
    """Obtener grupo adyacente de una posición"""
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


def imprimir_grupos_adyacentes(grupos):
    """Imprimir los grupos de fichas adyacentes (debug)"""
    for color, posiciones in grupos.items():
        print(f"Color {color}:")
        visitadas = set()
        for pos in posiciones:
            if pos not in visitadas:
                grupo_adyacente = obtener_grupo_adyacente(pos, posiciones)
                visitadas.update(grupo_adyacente)
                print(f"Grupo adyacente en {grupo_adyacente}")
        print()

def son_vecinas(pos1, pos2):
    """Verifica si dos posiciones son ortogonalmente adjacentes """
    return (abs(pos1[0] - pos2[0]) == 1 and pos1[1] == pos2[1]) or \
           (abs(pos1[1] - pos2[1]) == 1 and pos1[0] == pos2[0])


def agrupar_fichas(lista_fichas):
    """Agrupar fichas por color directamente desde la lista de fichas"""
    grupos = defaultdict(list)
    for ficha in lista_fichas:
        x = ficha['x']
        y = ficha['y']
        color = ficha['color']
        grupos[color].append((x, y))  # Agrupa por color y almacena las posiciones
    return grupos

def encontrar_figuras(id_partida : int, listaFig : List[int], db : Session):
    """Encontrar las figuras de la listaFig en el tablero de la partidaID"""
    tablero = obtener_fichas(id_partida, db)
    imprimir_tablero(tablero) #debugg
    grupos = agrupar_fichas(tablero)
    figuras = []
    
    for color, posiciones in grupos.items():
        # Dividimos en grupos adyacentes
        grupos_adyacentes = obtener_grupos_adyacentes(posiciones)
        #debug
        print(f"Color {color}:")
        for i, grupo in enumerate(grupos_adyacentes, 1):
            print(f"  Grupo adyacente {i}: {grupo}")
        print()
        #fin debug
        # Verificamos figuras en cada grupo adyacente
        for grupo in grupos_adyacentes:
            for figNum in listaFig:  # Iteramos sobre la lista de tipos de figura
                if es_figura_valida(grupo, figNum):
                    figuras.append((figNum, color, grupo))
    """"
    
    """
    return figuras
