.PHONY: test test-backend test-frontend dev build docker docker-push

REGISTRY ?= ghcr.io
OWNER ?= arrebol88
BACKEND_IMAGE ?= $(REGISTRY)/$(OWNER)/lost_and_found-backend
FRONTEND_IMAGE ?= $(REGISTRY)/$(OWNER)/lost_and_found-frontend
TAG ?= latest

test: test-backend test-frontend

test-backend:
	cd backend && pytest -v

test-frontend:
	cd frontend && npm test

dev:
	docker compose up --build

build:
	docker compose build

# 本地构建可推送的镜像（带 registry 前缀）
docker:
	docker build -t $(BACKEND_IMAGE):$(TAG) ./backend
	docker build --build-arg VITE_API_BASE=http://localhost:8000 \
		-t $(FRONTEND_IMAGE):$(TAG) ./frontend

# 推送到 registry（需先 docker login）
docker-push: docker
	docker push $(BACKEND_IMAGE):$(TAG)
	docker push $(FRONTEND_IMAGE):$(TAG)
