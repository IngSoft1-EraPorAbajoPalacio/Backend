# Proyecto de la materia Ingeniería de Software 1: El switcher
## Backend

Este proyecto es el backend de la aplicación El Switcher, desarrollado en Python con el framework FastAPI.

### Requisitos

- Python 3.8 o superior
- MySQL 5.7 o superior

### Instalación y environment

1. Clona el repositorio:

```bash
git clone https://github.com/IngSoft1-EraPorAbajoPalacio/Backend.git
cd Backend
```

2. Crea y activa el entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Instala las dependencias:

```bash
make install
```

5. Crea el enviroment de mysql:

```bash
make env
```

6. Inicia el servidor MYSQL:

```bash
make start
```

### Ejecución del servidor
Para ejecutar el servidor, usa:
```bash
make run
```
El servidor estará disponible en `http://localhost:8000`.

### Pruebas

Este proyecto utiliza Pytest para las pruebas. Para ejecutar las pruebas, usa:

```bash
make test
```

### Pruebas con reportes

Para ejecutar las pruebas con reportes, usa:

```bash
make test-report
```

### Comandos Adicionales

#### Verificar el estado del servidor MySQL:

```bash
make status
```

#### Detener el servidor MySQL:

```bash
make stop
```

#### Crear la base de datos:

```bash
make create-db
```

#### Ejecutar pruebas:

```bash
make test
```

#### Ejecutar pruebas con reportes:

```bash
make test-report
```

#### Ejecutar todas las pruebas y generar reportes:

```bash
make test-all
```

#### Limpiar archivos generados:

```bash
make clean
```