from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#escribir path relativo
DATABASE_URL = "mysql+mysqldb://lucas:123@localhost/el_switcher" 

# Configurar conexiones entre SQLAlchemy y MYSQL
engine = create_engine(DATABASE_URL, echo=True)

# Crear session para realizar consultas e inserciones
SessionLocal = sessionmaker(bind=engine)


def crear_session() :
    session = SessionLocal()
    try : 
        yield session
    finally:
        session.close()
