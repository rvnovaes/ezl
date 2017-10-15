test:
	docker-compose run web python manage.py test

local_sqlserver:
	ln -s docker-compose.sqlserver.yml docker-compose.override.yml

run:
	docker-compose up -d

logs:
	docker-compose logs --follow

build:
	docker-compose build web cmd_migrate cmd_collectstatic

shell:
	docker-compose run web bash

stop:
	docker-compose stop

ps:
	docker-compose ps

deploy: build run

set_env_development:
	rm docker-compose.override.yml || true
	ln -s docker-compose.development.yml docker-compose.override.yml

set_env_production:
	rm docker-compose.override.yml || true
	ln -s docker-compose.prod.yml docker-compose.override.yml
