.PHONY: copy_package \
		ct.copy.dev \
		ct.build.image \
		ct.destroy.image \
		ct.run \
		ct.test \
		ct.cleanup

copy_package:
	@echo "Verificando requirements.txt..."

ct.copy.dev:
	@echo "Verificando archivos para dev..."

ct.build.image: ## Build image for development.
	@echo "Construyendo imagen desde $(PROJECT_DIR)..."
	@docker build -f $(PROJECT_DIR)/Dockerfile -t $(IMAGE) $(PROJECT_DIR) --no-cache

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