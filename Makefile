.PHONY: test test-backend test-frontend dev build

test: test-backend test-frontend

test-backend:
	cd backend && pytest -v

test-frontend:
	cd frontend && npm test

dev:
	docker compose up --build

build:
	docker compose build
