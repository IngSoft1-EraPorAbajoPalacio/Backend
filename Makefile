# Variables
VENV_DIR = .venv
REQ_FILE = requirements.txt
DB_NAME = el_switcher
SOURCE_DIR = app

# Targets
.PHONY: all venv activate update-pip install-deps mysql-start mysql-status create-db run test test-report test-all clean

venv:
	python3 -m venv $(VENV_DIR)

install: 
	python -m pip install --upgrade pip
	python3 -m pip install -r $(REQ_FILE)
	python3 -m pip install mysqlclient

mysql-start:
	sudo systemctl start mysql

mysql-stop:
	sudo systemctl stop mysql

mysql-status:
	sudo systemctl status mysql

create-db: mysql-start
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

