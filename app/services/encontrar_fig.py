import logging
from collections import defaultdict
from app.services.ficha_service import fichas_service
from typing import List, Set
from app.services.cartas_service import obtener_figuras_en_juego
from operator import index
from sqlalchemy.orm import Session
from app.services.bd_service import *
from app.services.bd_service import *
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
 
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
        logger.debug(' '.join(fila))
    logger.debug("\n")

def normalizar_posiciones(posiciones):
    """Normaliza posiciones para arrancar desde (0, 0)"""
    if not posiciones:
        return set()
    min_x = min(p[0] for p in posiciones)
    min_y = min(p[1] for p in posiciones)
    return {(x - min_x, y - min_y) for x, y in posiciones}

    
def es_figura_valida(posiciones, figNum :int ):
    posiciones_normalizadas = normalizar_posiciones(posiciones)
    if figNum == 1:
        return is_fig1(posiciones_normalizadas)
    elif figNum == 2:
        return is_fig2(posiciones_normalizadas)
    elif figNum == 3:
        return is_fig3(posiciones_normalizadas)
    elif figNum == 4:
        return is_fig4(posiciones_normalizadas)
    elif figNum == 5:
        return is_fig5(posiciones_normalizadas)
    elif figNum == 6:
        return is_fig6(posiciones_normalizadas)
    elif figNum == 7:
        return is_fig7(posiciones_normalizadas)
    elif figNum == 8:
        return is_fig8(posiciones_normalizadas)
    elif figNum == 9:
        return is_fig9(posiciones_normalizadas)
    elif figNum == 10:
        return is_fig10(posiciones_normalizadas)
    elif figNum == 11:
        return is_fig11(posiciones_normalizadas)
    elif figNum == 12:
        return is_fig12(posiciones_normalizadas)
    elif figNum == 13:
        return is_fig13(posiciones_normalizadas)
    elif figNum == 14:
        return is_fig14(posiciones_normalizadas)
    elif figNum == 15:
        return is_fig15(posiciones_normalizadas)
    elif figNum == 16:
        return is_fig16(posiciones_normalizadas)
    elif figNum == 17:
        return is_fig17(posiciones_normalizadas)
    elif figNum == 18:
        return is_fig18(posiciones_normalizadas)
    elif figNum == 19:
        return is_fig19(posiciones_normalizadas)
    elif figNum == 20:
        return is_fig20(posiciones_normalizadas)
    elif figNum == 21:
        return is_fig21(posiciones_normalizadas)
    elif figNum == 22:
        return is_fig22(posiciones_normalizadas)
    elif figNum == 23:
        return is_fig23(posiciones_normalizadas)
    elif figNum == 24:
        return is_fig24(posiciones_normalizadas)
    elif figNum == 25:
        return is_fig25(posiciones_normalizadas)

    return False

def is_fig1(posiciones_normalizadas):
    """3 verical y 3 horizontal en el medio hacia la derecha """
    rotaciones = [
        {(0, 0), (1, 0), (2, 0), (1, 1), (1,2)},  # original
        {(0, 1), (1, 1), (2, 0), (2, 1),(2,2) },  # rotada 90 grados
        {(1,0), (0,2), (1,1), (1,2),(2,2)},  # rotada 180 grados
        {(0,0), (0,1), (0,2), (1,1),(2,1)}   # rotada 270 grados
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)
def is_fig2(posiciones_normalizadas):
    """2 horizontal y 3 horizontal uno abajo y uno a la derecha"""
    rotaciones = [
        {(0,0),(0,1),(1,1),(1,2),(1,3)},
        {(0,1),(1,0),(1,1),(2,0),(3,0)},
        {(0,0),(0,1),(0,2),(1,2),(1,3)},
        {(0,1),(1,1),(2,1),(2,0),(3,0)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig3(posiciones_normalizadas):
    """3 horizontal y dos horizontal arrbia desplazado uno a la derecha"""
    rotaciones =[
        {(0,2),(0,3),(1,0),(1,1),(1,2)},
        {(0,0),(1,0),(1,1),(2,1),(2,1),(3,1)},
        {(0,1),(0,2),(0,3),(1,0),(1,1)},
        {(0,0),(1,0),(2,0),(2,1),(3,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)


def is_fig4(posiciones_normalizadas):
    """escalera, uno, dos abajo desplazados uno derecha
    y dos abajo desplazado derecha"""
    rotaciones =[
        {(0,0),(1,0),(1,1),(2,1),(2,2)},
        {(0,2),(1,1),(1,2),(2,1),(2,0)},
        {(0,0),(0,1),(1,1),(1,2),(2,2)},
        {(0,1),(0,2),(1,0),(1,1),(2,0)}
    ]
    
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)


def is_fig5(posiciones_normalizadas):
    """cinco en linea"""
    rotaciones =[
        {(0,0),(0,1),(0,2),(0,3),(0,4)},
        {(0,0),(1,0),(2,0),(3,0),(4,0)}
    ]
    
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)


def is_fig6(posiciones_normalizadas):
    """ L simetrica (3 y 3)
    """
    rotaciones =[
        {(0,0),(1,0),(2,0),(2,1),(2,2)},
        {(2,0),(2,1),(2,2),(1,2),(0,2)},
        {(0,0),(0,1),(0,2),(1,2),(2,2)},
        {(0,0),(0,1),(0,2),(1,0),(2,0)}
    ]
        
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)


def is_fig7(posiciones_normalizadas):
    """cuatro en linea + 1 abajo derecha"""
    rotaciones =[
        {(0,0),(0,1),(0,2),(0,3),(1,3)},
        {(0,0),(1,0),(2,0),(3,0),(0,1)},
        {(0,0),(1,0),(1,1),(1,2),(1,3)},
        {(3,0),(3,1),(2,1),(1,1),(0,1)}
    ]
    
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)


def is_fig8(posiciones_normalizadas):
    """cuatro en linea + uno arriba derecha"""
    rotaciones =[
        {(1,0),(1,1),(1,2),(1,3),(0,3)},
        {(0,0),(0,1),(1,1),(2,1),(3,1)},
        {(0,0),(0,1),(0,2),(0,3),(1,0)},
        {(0,0),(1,0),(2,0),(3,0),(3,1)}
    ]
    
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig9(posiciones_normalizadas):
    rotaciones =[
        {(1,0),(1,1),(0,2),(1,2),(2,1)},
        {(0,0),(0,1),(1,1),(1,2),(2,1)},
        {(1,0),(2,0),(0,1),(1,1),(1,2)},
        {(1,0),(2,2),(0,1),(1,1),(2,1)}
    ]
    
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig10(posiciones_normalizadas):
    rotaciones =[
        {(1,0),(0,3),(1,1),(1,2),(2,0)},
        {(0,0),(0,1),(1,1),(2,1),(2,2)},
    ]
    
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig11(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(1,1),(1,2),(1,0),(2,1)},
        {(0,1),(1,1),(1,2),(2,0),(2,1)},
        {(0,1),(1,1),(1,0),(1,2),(2,2)},
        {(0,1),(1,1),(0,2),(1,0),(2,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig12(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(1,1),(1,0),(1,2),(2,2)},
        {(0,1),(1,1),(0,2),(2,0),(2,1)},
        
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig13(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(0,1),(0,2),(0,3),(1,2)},
        {(0,0),(1,0),(1,1),(2,0),(3,0)},
        {(0,1),(1,0),(1,1),(1,2),(1,3)},
        {(0,1),(0,2),(1,1),(2,1),(2,0)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig14(posiciones_normalizadas):
    rotaciones =[
        {(0,2),(1,0),(1,1),(1,2),(1,3)},
        {(1,1),(0,1),(1,1),(2,1),(3,1)},
        {(0,0),(0,1),(0,2),(0,3),(1,1)},
        {(0,0),(1,0),(2,0),(3,0),(2,1)}
        ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig15(posiciones_normalizadas):
    rotaciones =[
        {(0,1),(0,2),(1,0),(1,1),(1,2)},
        {(0,0),(0,1),(1,0),(1,1),(2,1)},
        {(0,0),(0,1),(1,0),(1,1),(0,2)},
        {(0,0),(1,0),(1,1),(2,0),(2,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig16(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(0,2),(1,0),(1,1),(1,2)},
        {(0,0),(0,1),(1,1),(2,0),(2,1)},
        {(0,0),(0,1),(0,2),(1,0),(1,2)},
        {(0,0),(0,1),(1,0),(2,0),(2,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig17(posiciones_normalizadas):
    rotacion = {(0,1),(1,0),(1,1),(1,2),(2,1)}
    return posiciones_normalizadas == rotacion 

def is_fig18(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(0,1),(0,2),(1,1),(1,2)},
        {(0,0),(0,1),(1,0),(1,1),(2,0)},
        {(0,0),(0,1),(1,0),(1,1),(1,2)},
        {(0,1),(1,0),(1,1),(2,0),(2,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig19(posiciones_normalizadas):
    rotaciones =[
        {(0,1),(0,2),(1,0),(1,1)},
        {(0,0),(1,0),(1,1),(2,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig20(posiciones_normalizadas):
    rotacion = {(0,0),(0,1),(1,0),(1,1)}
    return posiciones_normalizadas == rotacion

def is_fig21(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(0,1),(1,1),(1,2)},
        {(1,0),(0,1),(1,1),(2,0)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig22(posiciones_normalizadas):
    rotaciones =[
        {(0,1),(1,0),(1,1),(1,2)},
        {(0,1),(1,1),(1,0),(2,1)},
        {(0,1),(0,0),(0,2),(1,1)},
        {(0,0),(1,0),(2,0),(1,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)
def is_fig23(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(0,1),(0,2),(1,2)},
        {(0,1),(1,1),(2,1),(2,0)},
        {(0,0),(1,1),(1,0),(1,2)},
        {(0,0),(1,0),(2,0),(0,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig24(posiciones_normalizadas):
    rotaciones =[
        {(0,0),(0,1),(0,2),(0,3)},
        {(0,0),(1,0),(2,0),(3,0)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)

def is_fig25(posiciones_normalizadas):
    rotaciones =[
        {(0,2),(1,0),(1,1),(1,2)},
        {(0,0),(0,1),(1,1),(2,1)},
        {(0,0),(1,0),(0,1),(0,2)},
        {(0,0),(1,0),(2,0),(2,1)}
    ]
    return any(posiciones_normalizadas == rotacion for rotacion in rotaciones)


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

def  encontrar_figuras(id_partida : int, listaFig : List[int], db : Session):
    """Encontrar las figuras de la listaFig en el tablero de la partida con id = id_partida"""
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