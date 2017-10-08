test:
	docker-compose run web python manage.py test

local_sqlserver:
	ln -s docker-compose.sqlserver.yml docker-compose.override.yml

build_prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build web

run:
	docker-compose up -d

shell:
	docker-compose run web bash

stop:
	docker-compose stop

ps:
	docker-compose ps

run_prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

deploy_prod: build_prod up_prod