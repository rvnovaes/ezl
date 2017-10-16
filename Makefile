build:
	docker-compose build web certbot

collectstatic:
	docker-compose run web python manage.py collectstatic --noinput

create_certificate:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d mtostes.ezlawyer.com.br -m contato@ezlawyer.com.br --agree-tos

deploy: build stop remove run migrate collectstatic

local_sqlserver:
	ln -s docker-compose.sqlserver.yml docker-compose.override.yml

logs:
	docker-compose logs --follow

migrate:
	docker-compose run web python manage.py migrate --noinput

ps:
	docker-compose ps

remove:
	docker-compose rm -f certbot web

run:
	docker-compose up -d

restart:
	docker-compose restart web nginx

set_env_development:
	rm docker-compose.override.yml || true
	ln -s docker-compose.development.yml docker-compose.override.yml

set_env_production:
	rm docker-compose.override.yml || true
	ln -s docker-compose.production.yml docker-compose.override.yml

shell:
	docker-compose run web bash

stop:
	docker-compose stop

test:
	docker-compose run web python manage.py test
