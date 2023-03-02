all:
	@echo "Hello $(LOGNAME), nothing to do by default"
	@echo "Try 'make help'"

help:
	@egrep "^# target:" [Mm]akefile

test:
	docker-compose exec web python manage.py test

build:
	docker-compose build

static:
	docker-compose run web python manage.py collectstatic --noinput

rebuild: 
	docker-compose build --no-cache

up: 
	docker-compose up

up-d: 
	docker-compose up -d

down: 
	docker-compose down

stop: 
	docker-compose stop

purge: 
	sudo rm .postgres-data -r

restart: 
	docker-compose restart

migrations: 
	docker-compose exec web python manage.py makemigrations

migrate:
	docker-compose exec web python manage.py migrate

setup:
	cp .env.template .env
	make build

superuser:
	docker-compose exec web python manage.py createsuperuser

bash:
	docker-compose exec web bash

shell:
	docker-compose exec web python manage.py shell

