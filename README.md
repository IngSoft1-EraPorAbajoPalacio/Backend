en ~/Backend
Crear entorno virtual
###  python3 -m venv .venv
Activar entorno virtual
###  source .venv/bin/activate
Actualizar pip e instalar dependencias:
###  python -m pip install --upgrade pip
###  python3 -m pip install -r requirements.txt
###  python3 -m pip install mysqlclient

Correr proyecto

### cd/app 
###  uvicorn main:app --reload
