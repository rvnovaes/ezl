# EasyLawyer

O projeto está configurado para rodar com Docker e Docker compose. Ambos devem estar instalados:

Link para instalação do Docker compose:
https://docs.docker.com/compose/install/#install-compose

Link para instalação do Docker no Ubuntu:
https://docs.docker.com/engine/installation/linux/ubuntu/

## Rodando o projeto em ambiente de desenvolvimento

### Executando em ambiente de desenvolvimento

Para executar o projeto em ambiente de desenvolvimento você precisa executar o comando abaixo para definir o ambiente:

```bash
sudo make set_env_development
```

Em seguida você deverá rodar o comando `make deploy` para que todos os containers sejam criados juntamente com o banco de dados e os arquivos estáticos:

```
sudo make deploy
```

Após a primeira execução do projeto você pode roda-lo com o comando abaixo:

```
sudo make run
```

#### Atualizando imagem docker

Sempre que uma nova dependência for adicionada no requirements.txt o comando abaixo deve ser executado para gerar novamente a imagem docker.

```bash
sudo make build
```

### Comandos disponíveis

Para facilitar o desenvolvimento os seguintes comandos estão disponíveis através do `make`:

- `run` - Executa todos os serviços em backgroud
- `stop` - Para de executar a aplicação. Para voltar é só rodar o `run`
- `restart` - Reinicia todos os containers
- `deploy` - Atualiza as dependências, executa as migrations, gera os arquivos estáticos e executa a aplicação (make run)
- `logs` - Exibe todos os logs de todos os containers
- `shell` - Abre um shell dentro do container da aplicação
- `psql` - Abre a linha de comando do banco de dados Postgres
- `migrate` - Executa as migrações do projeto
- `collectstatic` - Executa o comando `collectstatic` do Django
- `test` - Executa os testes unitários

## Componentes

A aplicação está distribuida nos seguintes serviços Docker:

### Desenvolvimento

- web - Projeto Django rodando com runserver na porta `8000` do computador `localmente`
- nginx - Nginx rodando na porta `8080` do computador `localmente`
- db - Postgres rodando `internamente` na porta `5432`
- cmd_collectstatic - Comando `collectstatic` do Django que é executado toda vez que um `up` ou `restart` é executado
- cmd_migrate - Comando `migrate` do Django que é executado toda vez que um `up` ou `restart` é executado
- sqlserver - SQLServer rodando `internamente` na porta `1433`.
  - Esse serviço não é executado automaticamente por padrão

### Produção

- web - Projeto Django rodando `internamente` com uWsgi na porta `8000`
- nginx - Nginx rodando na porta `80` do computador `localmente`
- db - Idem ao ambiente de desenvolvimento
- certbot - Cronjob que renova o certificado SSL automaticamente

Para rodar o SQLServer em ambiente de desenvolvimento você deve rodar o seguinte comando:

```
sudo make local_sqlserver
```

Ao executar o comando acima será criado um link simbólico com o nome `docker-compose.override.yml` apontando para `docker-compose.sqlserver.yml` e na próxima vez que você rodar a aplicação você poderá acessar o SQLServer da seguinte maneira:

- Host: `sqlserver`
- Port:  `1433`
- User: `sa`
- Password: `%SuperEZL%1`



## Deploy

Para fazer deploy você deve executar os comandos abaixo:

### Produção
```
cd deploy
fab production deploy:dev
```

### Teste
```
cd deploy
fab teste deploy:dev
```

#### Testando o deploy sem fazer push

Você pode testar o deploy sem fazer push da seguinte maneira:

```
cd deploy
fab teste deploy:rsync=true
```

Ao executar o comando acima ao invés de atualizar o repositório no servidor atavés do Mercurial ele será atualizado utilizando o `rsync` copiando os arquivos de sua maquina para o servidor


#### Fazendo deploy de uma revisão específica

Você pode fazer deploy de uma revisão específica da seguinte maneira:

```
cd deploy
fab teste deploy:100000000
```
