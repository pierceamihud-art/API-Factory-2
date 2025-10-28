.PHONY: setup run test docker-build docker-up docker-down

setup:
	python3 -m venv .venv && . .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	. .venv/bin/activate && pytest -q

docker-build:
	docker build -t api-factory:mvp .

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
