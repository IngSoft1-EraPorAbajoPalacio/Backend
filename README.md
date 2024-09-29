en ~/Backend
Crear entorno virtual
###  python3 -m venv .venv
Activar entorno virtual
###  source .venv/bin/activate
Actualizar pip e instalar dependencias:
###  python -m pip install --upgrade pip
###  python3 -m pip install -r requirements.txt
###  python3 -m pip install mysqlclient

Necesitaremos tener instalado MySQL:
### https://dev.mysql.com/downloads/mysql/

Una vez instalado, iniciamos el servidor MYSQL:
#sudo systemctl start mysql

Verificar el estado de la conexión:
#sudo systemctl status mysql

Iniciar una sesión
### mysql -u root -p

Creamos una base de datos llamada el_switcher
#CREATE DATABASE el_switcher

Correr proyecto
### cd/app 
###  uvicorn main:app --reload
