# **Configuração** #

**1. Criar o diretório /opt/files_easy_lawyer/GEDs caso não exista**

* Este diretório é responsavél por armazenar os arguivos vindos do ADVWin

**2. Configuração da comunicação com o banco do advwin.** 

* No projeto, dentro do diretório connections o arquivo advwin_ho.cfg é necessário colocar as configurações do banco advwin_ho

* *Obs: (Atualmente está configurado no código, para utilizar as configurações do arquivo advwin_ho.cfg.
          Para rodar em produção, isto deverá ser alterado)*

**3. Configurações do arquivo etl/advwin_ezl/settings.py**

* USER - Usuário do sistema que irá persistir os novos dados no ezl

* host_sftp - Este é o IP do servidor sftp advwin que armazena os arquivos que serão importados para o EZL

* port_sftp - Esta é a porta do servidor sftp advwin que armazena os arquivos que serão importados para o EZL
    
* password_sftp - Esta é a senha do servidor sftp advwin que armazena os arquivos que serão importados para o EZL 

* username_sftp - Este é a porta do servidor sftp dvwin que armazena os arquivos que serão importados para o EZL
    
* local_path - local onde será armazenado os arquivos (GEDs) do ADVWin (Padrão: /opt/files_easy_lawyer/GEDs/)
                   (Não altere este diretório, pois está linkado as configurações do campo path da classe task.models.Ecm)
        
* LUIGI_PORT - Porta utilizada para execução do luigid 

    * **Atenção**: PARA CONFIGURAR UMA PORTA DIFERENTE DA 8082 QUE E PADRAO DO LUIGI, E NECESSARIO CRIAR O ARQUIVO luigi.cfg DENTRO DE /etc/luigi/ exemplo: http://luigi.readthedocs.io/en/stable/configuration.html

    * PARA A CONFIGURACAO DA PORTA, O ARTRIBUTO NO luigi.cfg deve ser **default-scheduler-port=porta**
                            
**4. Executando o etl** 

* Para executar o etl é necessário entrar no diretório raiz do projeto e executar: 
      
```
#!shell
python3.5 etl/advwin_ezl/luigi_jobs.py -p='senha do usuário que esta chamando o comando'

```
      
* É necessário que este comando seja executado por um usuário que esteja no grupo sudoers (Com permissões de root). Isto é necessário, pois o script executa comandos que necessitam deste previlégio
      
* Ao realizar este procedimento automáticamente ficará disponível um dashboard fornecido pelo luigi para acompanhamento dos processos (para acesso é necessário informar http://host:LUIGI_PORT).

![luigid.png](https://bitbucket.org/repo/4ppXxLL/images/2057876133-luigid.png)
          
* Caso seja necessário reiniciar o processo de importação. É necessário matar o processos luigid antes de executar o arquivo luigi_jobs novamente.

* Ex: 
```
#!shell

sudo killall luigid
```