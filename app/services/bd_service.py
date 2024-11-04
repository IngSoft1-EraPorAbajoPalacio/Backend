from app.db.models import Jugador
from sqlalchemy.exc import *
from sqlalchemy.orm import Session
from app.db.models import *
from sqlalchemy import desc
from app.services.jugador_service import *
from app.db.models import Color
import random

class DB_Service:
    
    
    
    ########## QUERIES RELACIONADAS A PARTIDAS ##########
    
    def crear_partida(self, nombre_partida: str, min_jugadores: int, max_jugadores: int,
                      id_owner: int, db: Session):
        """
        Se crea una partida en la base de datos.
        El id_owner representa que la partida fue creada por el jugador con ese id.
        """    
        partida_creada = Partida(
                nombre=nombre_partida,
                min=min_jugadores,
                max=max_jugadores,
                id_owner=id_owner
            )
        db.add(partida_creada)
        db.commit()
        
        return partida_creada
    
    def obtener_partida(self, id_partida: int, db: Session):
        """
        Obtengo la partida con id_partida.
        En caso de no existir, devuelvo None
        """
        return db.query(Partida).filter(Partida.id == id_partida).first()
    
    def obtener_partidas(self, db: Session):
        """
        Obtengo el total de las partidas.
        En caso de no existir ninguna, devuelvo una lista vacía.
        """
        return db.query(Partida).all()
    
    def obtener_partida_owner(self, id_jugador: int, db: Session):
        """
        Obtengo la partida creada por id_jugador.
        En caso de no existir ninguna, devuelvo None.
        """
        return db.query(Partida).filter(Partida.id_owner == id_jugador).first()
         
    def obtener_partidas_lobby(self, db: Session):
        """
        Obtengo las partidas no iniciadas.
        En caso de no existir, devuelvo una lista vacía.
        """
        return db.query(Partida).filter(Partida.activa == False).all()
    
    def partida_iniciada(self, id_partida: int, db: Session):
        """
        Obtengo un booleano indicando si la partida con id_partida ha iniciado.
        """
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        return partida.activa
    
    def obtener_tablero(self, id_partida: int, db: Session):
        return db.query(Tablero).filter(Tablero.id_partida == id_partida).first()
    
    def crear_tablero(self, id_partida: int, db: Session):
        """
        Se crea un tablero asociado al id_partida
        """
        partida = self.obtener_partida(id_partida, db)
        id_jugadores= [jugador.id_jugador for jugador in partida.jugadores]  
        #id_jugadores = obtener_id_jugadores(id_partida, db)

        tablero_nuevo = Tablero(
            id_partida = id_partida,
            #color_prohibido=random.choice(list(Color)),
            turno = random.choice(id_jugadores) 
        )
        db.add(tablero_nuevo)
        db.commit()
    
    def setear_partida_activa(self, id_partida, db: Session):
        """
        Inicia la partida con id: id_partida en la base de datos
        """
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        partida.activa = True
        db.commit()

    ########## QUERIES RELACIONADAS A JUGADORES ##########
    
    def crear_jugador(self, nombre: str, db: Session):
        """
        Se crea un jugador
        """
        jugador_creado = Jugador(nickname=nombre)
        db.add(jugador_creado)
        db.commit()
        
        return jugador_creado
           
    
    def obtener_jugador(self, id_jugador: int, db: Session):
        """
        Obtengo el jugador con id id_jugador.
        En caso de no existir, devuelvo None
        """
        return db.query(Jugador).filter(Jugador.id == id_jugador).first()
    
    def crear_jugador_partida(self, id_jugador: int, id_partida: int, db: Session):
        """
        Se inserta una fila en la tabla Jugador_Partida con id_jugador y id_partida
        """
        jugador_partida = Jugador_Partida(
                id_jugador=id_jugador,
                id_partida=id_partida
            )
        db.add(jugador_partida)
        db.commit()
    
    def setear_jugadores_jugando(self, id_partida: int, db: Session):
        """
        A todos los jugadores de la partida con id: id_partida los coloca como si estuvieran jugando 
        """        
        partida = db.query(Partida).filter(Partida.id == id_partida).first()
        jugadores =  [jugador.jugador for jugador in partida.jugadores]
        for jugador in jugadores:
            jugador.jugando = True
        db.commit()
    
    
    ########## QUERIES RELACIONADAS A CARTAS DE MOVIMIENTOS ##########
    
    def obtener_movimiento_bd(self, id: int, db: Session): 
        """
        Se obtiene la carta de movimiento con id en la tabla "Movimientos"
        """
        return db.query(Movimientos).filter(Movimientos.id == id).first()
    

    def obtener_movimientos_en_mano(self, id_partida: int, id_jugador: int, db: Session): 
        """
        Obtengo las cartas de movimientos en mano del jugador con id : id_jugador
        que se encuentra en la partida con id: id_partida.
        En caso de no encontrar ninguna carta de movimiento, devuelvo una lista vacía.
        """
        return db.query(CartaMovimientos).filter(
        CartaMovimientos.id_partida == id_partida,
        CartaMovimientos.id_jugador == id_jugador,
        CartaMovimientos.en_mano == True
    ).all()
        
    def obtener_movimiento(self, id_partida: int, id_jugador: int, id_movimiento, db: Session):
        return db.query(CartaMovimientos).filter(
                CartaMovimientos.id_jugador == id_jugador,
                CartaMovimientos.id_partida == id_partida,
                CartaMovimientos.carta_mov == id_movimiento, 
            ).first()
        
    def cantidad_movimientos(self, db: Session): 
        return db.query(Movimientos).count()
    
    
    def obtener_movimiento_en_mano(self, id_partida: int, id_carta: int, db: Session):
        """
        Obtengo la carta de movimiento en mano que se encuentra en la partida con id: id_partida.
        En caso de no encontrar ninguna carta de movimiento, devuelvo None.
        """  
        return db.query(CartaMovimientos).filter(
                CartaMovimientos.id_partida == id_partida, 
                CartaMovimientos.carta_mov == id_carta).first().en_mano
            
    def eliminar_carta_movimiento(self, id_partida: int, id_jugador: int, id_carta: int, db: Session):
        """
        Elimino de las cartas de movimientos del jugador con id : id_jugador a la carta de movimiento
        con id: id_carta que se encuentra en la partida con id: id_partida
        Se asume que existe la carta de movimiento.
        """
        db.query(CartaMovimientos).filter(
            CartaMovimientos.id_partida == id_partida,
            CartaMovimientos.id_jugador == id_jugador,
            CartaMovimientos.carta_mov == id_carta
        ).first().en_mano = False
        
    def setear_carta_movimiento(self, carta_movimiento: CartaMovimientos, db: Session):
        """
        Al atributo "en_mano" de carta_movimiento lo coloca en True
        """
        carta_movimiento.en_mano = True
        db.commit()
        
    def crear_movimiento_parcial(self, id_partida: int, id_jugador: int, movimiento: int,
                                 x1: int, y1: int, x2: int, y2: int, db: Session) :
        """
        Se crea un movimiento parcial en la partida con id: id_partida al jugador con id : id_jugador
        donde las posiciones son x1,y1,x2,y2.
        """    
        movimiento_parcial = MovimientosParciales(
            id_partida = id_partida, id_jugador = id_jugador,
            movimiento = movimiento,
            x1 = x1,
            y1 = y1,
            x2 = x2,
            y2= y2
        )
        db.add(movimiento_parcial)
        db.commit()
        
    def obtener_movimientos_parciales(self, id_partida: int, id_jugador: int, db: Session):
        """
        Se obtiene todos los movimientos parciales del jugador con id: id_jugador
        que se encuentra en la partida con id: id_partida
        """
        return db.query(MovimientosParciales).filter(
            MovimientosParciales.id_jugador == id_jugador,
            MovimientosParciales.id_partida == id_partida,
        ).all()
        
    def obtener_ultimo_movimiento_parcial(self, id_partida: int, id_jugador: int, db: Session):
        return (db.query(MovimientosParciales)
            .filter(
                MovimientosParciales.id_partida == id_partida,
                MovimientosParciales.id_jugador == id_jugador
            )
            .order_by(desc(MovimientosParciales.id))
            .first()
        )
    
    def eliminar_movimientos_parciales(self, id_partida: int, id_jugador: int, db: Session):
        """
        Elimino todos los movimentos parciales del jugador con id: id_jugador que se encuentra
        en la partida con id: id_partida.
        """
        movimientos_parciales = self.obtener_movimientos_parciales(id_partida, id_jugador, db)
        for mov in movimientos_parciales:
            db.delete(mov)
        db.commit()

    ########## QUERIES RELACIONADAS A CARTAS DE FIGURAS ##########
    
    def obtener_figura_en_mano(self, id_partida: int, id_jugador: int, id_figura: int, db: Session):
        """
        Obtengo la carta de figura  del jugador con id : id_jugador
        que se encuentra en la partida con id: id_partida.
        En caso de que la carta no se encuntre en la mano del jugador, devuelvo None.
        """    
        return db.query(CartasFigura).filter(
            CartasFigura.id_partida == id_partida,
            CartasFigura.id_jugador == id_jugador,
            CartasFigura.carta_fig == id_figura,
            CartasFigura.en_mano == True
        ).first()
        
    def obtener_figuras_en_mano(self, id_partida: int, id_jugador: int, db: Session):
         """
         Obtengo las cartas de figuras en mano del jugador con id : id_jugador
         que se encuentra en la partida con id: id_partida.
         En caso de no encontrar ninguna carta de movimiento, devuelvo una lista vacía.
         """    
         return db.query(CartasFigura).filter(
             CartasFigura.id_partida == id_partida,
             CartasFigura.id_jugador == id_jugador,
             CartasFigura.en_mano == True
         ).all()        


    def cantidad_figuras(self, db: Session):
        return db.query(Figuras).count()


    def eliminar_carta_figura(self, id_partida: int, id_jugador: int, id_figura: int, db: Session):
        """
        Se elimina la carta de figura con id: id_figura del jugador con id : id_jugador
        """    
        db.query(CartasFigura).filter(
            CartasFigura.id_partida == id_partida,
            CartasFigura.id_jugador == id_jugador,
            CartasFigura.carta_fig == id_figura
        ).delete()
        db.commit()
    def obtener_figura(self, id_figura: int, db: Session):
        """
        Devuelve la figura con el id: id_figura
        """
        return db.query(Figuras).filter(Figuras.id == id_figura).first()
    
    
    ########## QUERIES RELACIONADAS A FICHAS ##########
    
    
    def obtener_ficha(self, id_partida: int, x: int, y: int, db: Session):
        """
        Obtengo la ficha que se encuentra en la partida con id : id_partida,
        con las posiciones x e y.
        En caso de no encontrar ninguna ficha, devuelvo None.
        """
        return db.query(Ficha).filter(
                Ficha.id_tablero == id_partida, 
                Ficha.x == x,
                Ficha.y == y
        ).first()
        
    def obtener_color(self, id_partida: int, id_jugador: int, figura: int, db: Session):
        """    
        figura representa el valor en si de la figura.
        Se asume que la carta de figura le pertenece al jugador con id: id_jugador.
        figura = db.query(Figuras).filter(Figuras.id == figura).first()
        cartas_figura = figura.cartas_de_figura
        for fig in cartas_figura:
            print(fig.id)
            print(fig.color)
            print(fig.id_jugador)
            print(fig.id_partida)
            if fig.id_jugador == id_jugador and fig.id_partida == id_partida:
                return fig.color.value
        #print(f"el color es : {mio[0]}")
        #return mio[0]       
        """
        
        
    def swapear_color_fichas(self, ficha1: Ficha, ficha2: Ficha, db: Session):
        ficha1.color, ficha2.color = ficha2.color, ficha1.color
        db.commit()
        
"""
    def cambiar_color_prohibido(self, id_partida: int,  color: Color , db: Session):
        tablero = db.query(Tablero).filter(Tablero.id_partida == id_partida).first()
        tablero.color_prohibido = color
        db.commit()
"""
        
db_service = DB_Service()