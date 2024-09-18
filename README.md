en ~/Backend
Crear entorno virtual
###  python3 -m venv .venv
Activar entorno virtual
###  source .venv/bin/activate
Actualizar pip e instalar dependencias:
###  python -m pip install --upgrade pip
###  python3 -m pip install -r requirements.txt

Correr proyecto 
###  uvicorn app.main:app --reload
