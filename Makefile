build:
	docker-compose build builder luigi
	@docker-compose build certbot || true

check_compose_override:
	@test -s docker-compose.override.yml || { echo "docker-compose.override.yml não foi encontrado. Você precisa rodar o comando 'make set_env_development' para começar."; exit 1;}

collectstatic:
	docker-compose run web python manage.py collectstatic --noinput

create_certificate:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d mtostes.ezlawyer.com.br -m contato@ezlawyer.com.br --agree-tos

create_certificate_teste:
	docker-compose run certbot certbot certonly --webroot -w /tmp/www -d teste.ezlawyer.com.br -m contato@ezlawyer.com.br --agree-tos

deploy: check_compose_override build restart migrate collectstatic load_fixtures

local_sqlserver:
	ln -s docker-compose.sqlserver.yml docker-compose.override.yml

logs:
	docker-compose logs --follow

migrate:
	docker-compose run web python manage.py migrate --noinput

load_fixtures0:
	docker-compose run web python manage.py loaddata auth_user office country state court_district
	docker-compose run web python manage.py ezl_create_groups_and_permissions

load_fixtures:
	docker-compose run web python manage.py ezl_create_groups_and_permissions

create_groups_and_permissions: 
	docker-compose run web python manage.py ezl_create_groups_and_permissions

adjust_contact_mechanism:
	docker-compose run web python manage.py adjust_contact_mechanism
ps:
	docker-compose ps

psql:
	docker-compose run web bash -c "PGPASSWORD=ezl psql -h db -U ezl"

remove:
	docker-compose rm -f web
	docker-compose rm -f certbot || true

run: check_compose_override
	docker-compose up -d

restart:
	docker-compose stop
	docker-compose up -d

restart_web:
	docker-compose restart web ws ws-worker

set_env_development:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.development.yml docker-compose.override.yml

set_env_production:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.production.yml docker-compose.override.yml

set_env_teste:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.teste.yml docker-compose.override.yml

set_env_demo:
	@rm docker-compose.override.yml || true
	ln -s docker-compose.demo.yml docker-compose.override.yml

shell:
	docker-compose run web bash

stop:
	docker-compose stop web nginx

test:
	docker-compose run web python manage.py test --parallel --keepdb
