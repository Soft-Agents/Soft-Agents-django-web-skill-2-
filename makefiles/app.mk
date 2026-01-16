.PHONY: app.test  		 \
		app.local 		 \
		app.tailwind	 \
		app.add   		 \
		app.migrate		 \
		app.static

app.local: ## Ejecutar la aplicación en local
	python manage.py runserver

app.tailwind: ## Ejecutar Tailwind CSS
	python manage.py tailwind start

app.add: ## Crear una nueva aplicación
	@echo "Creando una nueva aplicación..."
	@echo "Nombre de la aplicación: "
	@read app_name; \
	python manage.py startapp $$app_name

app.migrate: ## Realizar migraciones
	python manage.py makemigrations
	python manage.py migrate

app.test: ## Ejecutar pruebas
	python manage.py test

app.static: ## Recolectar archivos estáticos
	python manage.py collectstatic

app.rm.static: ## Eliminar archivos estáticos
	rm -rf static