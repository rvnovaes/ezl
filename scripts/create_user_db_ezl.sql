-- Cria usuário e banco para desenvolvimento
-- USO: psql -U postgres < create_user_db_ezl.sql
CREATE USER ezl WITH PASSWORD 'ezl';
ALTER USER ezl WITH VALID UNTIL 'infinity';
ALTER USER ezl WITH SUPERUSER;
CREATE DATABASE ezl;
ALTER DATABASE ezl OWNER TO ezl;
