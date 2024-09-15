# Backend

/backend
├── /app
│   ├── __init__.py                 # Archivo que marca "app" como paquete Python
│   ├── main.py                     # Punto de entrada de la aplicación FastAPI
│   ├── dependencies.py             # Definición de dependencias comunes
│   ├── /routers
│   │   ├── __init__.py             # Archivo que marca "routers" como subpaquete
│   │   ├── partida.py              # Endpoints relacionados con partidas
│   │   └── jugadores.py            # Endpoints relacionados con jugadores
│   ├── /models                     # Definición de modelos (Pydantic)
│   │   ├── __init__.py             # Archivo que marca "schemas" como subpaquete
│   │   ├── partida_schema.py              # Schemas para partidas
│   │   └── jugador_schema.py              # Schemas para jugadores
│   ├── /services
│   │   ├── __init__.py             # Archivo que marca "services" como subpaquete
│   │   ├── partida_service.py      # Lógica de negocio para partidas
│   │   └── jugador_service.py      # Lógica de negocio para jugadores
│   └── /db                         # Interacción con la base de datos
│       ├── __init__.py             # Archivo que marca "db" como subpaquete
│       ├── models.py               # Definición de modelos con SQLAlchemy
│       ├── base.py                 # Base de modelos SQLAlchemy
│       └── session.py              # Configuración de la sesión con la base de datos
├── /tests                          # Tests unitarios y de integración
│   ├── __init__.py
│   ├── test_partida.py             # Pruebas para endpoints de partida
│   └── test_jugador.py             # Pruebas para endpoints de jugador
├── .env                            # Variables de entorno (opcional)
|── requirements.txt                # Lista de dependencias
|__ README.md                       # Instrucciones y documentación del proyecto
|__ .gitignore                      # indica qué archivos deben ser excluidos del control de versiones
