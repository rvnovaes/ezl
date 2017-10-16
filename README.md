# EasyLawyer

O projeto está configurado para dodar com Docker e Docker composer.

## Rodando o projeto em ambiente de desenvolvimento


### Executando em ambiente de desenvolvimento

```bash
make run
```

#### Atualizando imagem docker

Sempre que uma nova dependência for adicionada no requirements.txt o comando abaixo deve ser executado para gerar novamente a imagem docker.

```bash
make build
```

### Executando em ambiente de produção

```bash
make run_prod
```

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
- cmd_collectstatic - Idem ao ambiente de desenvolvimento
- cmd_migrate - Idem ao ambiente de desenvolvimento

Para rodar o SQLServer em ambiente de desenvolvimento você deve rodar o seguinte comando:

```
make local_sqlserver
```

Ao executar o comando acima será criado um link simbólico com o nome `docker-compose.override.yml` apontando para `docker-compose.sqlserver.yml` e na próxima vez que você rodar a aplicação você poderá acessar o SQLServer da seguinte maneira:

- Host: `sqlserver`
- Port:  `1433`
- User: `sa`
- Password: `%SuperEZL%1`


