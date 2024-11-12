# Variables
VENV_DIR = .venv
REQ_FILE = requirements.txt
DB_NAME = el_switcher
SOURCE_DIR = app

# Targets
.PHONY: all venv activate update-pip install-deps start status create-db run test test-report test-all clean env

venv:
	python3 -m venv $(VENV_DIR)

install: 
	python3 -m pip install --upgrade pip
	python3 -m pip install -r $(REQ_FILE)
	python3 -m pip install mysqlclient
	pip3 install coverage
	pip3 install pytest
	pip3 install pytest-asyncio

start:
	sudo systemctl start mysql

stop:
	sudo systemctl stop mysql

status:
	sudo systemctl status mysql

create-db: start
	mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS $(DB_NAME);"

run: 
	uvicorn app.main:app --reload

test:
	coverage run --source=$(SOURCE_DIR) -m pytest

test-report:
	coverage report -m

test-all:
	coverage run --source=$(SOURCE_DIR) -m pytest
	coverage report -m

clean:
	rm -rf .coverage
	rm -rf $(SOURCE_DIR)/__pycache__
	rm -rf $(SOURCE_DIR)/routers/__pycache__
	rm -rf $(SOURCE_DIR)/schema/__pycache__
	rm -rf $(SOURCE_DIR)/services/__pycache__
	rm -rf $(SOURCE_DIR)/tests/__pycache__
	rm -rf .pytest_cache
	rm -rf .mypy

env:
	@read -p "Ingrese su usuario de mysql: " DB_USER; \
	read -p "Ingrese su contraseña de mysql: " DB_PASSWORD; \
	echo "DB_USER=$$DB_USER" > .env; \
	echo "DB_PASSWORD=$$DB_PASSWORD" >> .env; \
	echo "DB_HOST=localhost" >> .env; \
	echo "DB_NAME=$(DB_NAME)" >> .env;