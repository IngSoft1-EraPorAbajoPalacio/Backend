from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#from sqlalchemy import insert, select, update, delete

#DB_PATH = os.path.dirname(os.path.abspath(_file_)) + os.sep
#DB_FILE = "datos.mysql"

#escribir path relativo
DATABASE_URL = "mysql+mysqldb://lucas:123@localhost/el_switcher" 

# Configurar conexiones entre SQLAlchemy y MYSQL
engine = create_engine(DATABASE_URL, echo=True)

# Crear session para realizar consultas e inserciones
SessionLocal = sessionmaker(bind=engine)

# Crear la clase Base que heredan todos las clases de models
Base = declarative_base()

def crear_session() :
    session = SessionLocal()
    try : 
        yield session
    finally:
        session.close()
