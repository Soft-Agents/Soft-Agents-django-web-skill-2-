.PHONY: copy_package \
		ct.copy.dev \
		ct.build.image \
		ct.destroy.image \
		ct.run \
		ct.test \
		ct.cleanup

copy_package:
	@echo "Copiando requirements.txt..."
	@cp $(PROJECT_DIR)/requirements.txt docker/local/requirements.txt

ct.copy.dev:
	@echo "Copiando archivos..."
	@cp $(PROJECT_DIR)/requirements.txt docker/dev/requirements.txt

ct.build.image: copy_package ## Build image for development.
	@cd docker/local && \
		docker build -f Dockerfile -t $(IMAGE) . --no-cache && \
		rm -f db.sqlite3

ct.destroy.image: 
	@echo "Destruyendo imagen de Docker..."
	@docker rmi $(IMAGE) -f

ct.run: ## Run container
	@export IMAGE="$(IMAGE)" && \
	export WORKDIR="$(WORKDIR)" && \
	export PROJECT_DIR="$(PROJECT_DIR)" && \
	export HTTP_PORT="$(HTTP_PORT)" && \
	export ENV="$(ENV)" && \
	export APP_ENV="$(APP_ENV)" && \
	docker compose up --remove-orphans

ct.test: ## Ejecutar pruebas
	@echo "Ejecutando pruebas..."
	@docker exec -it $(PROJECT_NAME) python3 $(PROJECT_DIR)/manage.py test

ct.cleanup: ## Detener y eliminar contenedor
	@echo "Limpiando contenedor..."
	@docker stop $(PROJECT_NAME) || true
	@docker rm $(PROJECT_NAME) || true