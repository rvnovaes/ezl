# -*- coding: utf-8 -*-
from getpass import getpass
from fabric.api import env, task, local, run, sudo, roles, put, cd
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists
from fabric.operations import prompt
import tempfile


USER = 'ezl'
REPO_PATH = "/home/{user}/ezl-{env}/"
REPO_URL = "ssh://bitbucket.org/marcelotostes/easy_lawyer_django"

env.roledefs = {
    'production': {
        'hosts': ['{}@189.43.93.151'.format(USER)],
    },
    'demo': {
        'hosts': ['{}@13.68.213.60'.format(USER)],
    },
    'teste': {
        'hosts': ['{}@13.68.213.60'.format(USER)],
    }
}


@task
def production():
    env.hosts = env.roledefs["production"]["hosts"]
    env["NAME"] = "production"


@task
def teste():
    env.hosts = env.roledefs["teste"]["hosts"]
    env["NAME"] = "teste"


@task
def psql(revision=None, rsync=False):
    with cd(get_repo_path()):
        run("make psql")


@task
def deploy(revision=None, rsync=False):
    setup_ssh()
    if rsync:
        rsync_repo()
    else:
        update_repo(revision)
    with cd(get_repo_path()):
        run("make deploy")


@task
def luigi_logs():
    with cd(get_repo_path()):
        run("docker-compose logs --follow --tail=10 luigi")


@task
def mount_ecm_dir():
    """Monta a pasta do ECM/GED dentro do servidor"""
    username = prompt("Informe o nome do usuário do servidor Windows: ")
    password = getpass("Informe a senha do usuário: ")
    host = "172.27.155.11"
    local_path = "/mnt/windows_ecm/"
    sudo("mount -t cifs -o username={},domain=mtostes,password={} "
         "//{}/ged_advwin$ {}".format(username, password, host, local_path))


def update_repo(revision="default"):
    if not exists(get_repo_path()):
        run("hg clone {} {}".format(REPO_URL, get_repo_path()))

    with cd(get_repo_path()):
        run("hg pull -u")
        run("hg update {} -C".format(revision))


def rsync_repo(revision=None):
    tmp_dir = tempfile.mkdtemp()
    local("cp -r ../. {}".format(tmp_dir))
    rsync_project(local_dir="{}/.".format(tmp_dir),
                  remote_dir=get_repo_path(),
                  exclude=['.hg', 'staticfiles', 'media', 'pyc', '.orig', '__pycache__'])
    local("rm -rf {}".format(tmp_dir))


@task
def install():
    # Adiciona permissão de sudo sem pedir senha
    sudo('echo "{} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/no-password'
         .format(USER))
    install_docker()
    with cd(get_repo_path()):
        run("make set_env_{}".format(env["NAME"]))
        run("make deploy")

    deploy()
    with cd(get_repo_path()):
        run("make create_certificate")


@task
def install_docker():
    # Install Docker
    sudo("curl -fsSL get.docker.com | sudo sh")
    sudo("curl -L https://github.com/docker/compose/releases/download/"
         "1.16.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/"
         "bin/docker-compose")
    sudo("chmod +x /usr/local/"
         "bin/docker-compose")
    sudo("usermod -aG docker {}".format(USER))


@task
def setup_cron():
    cron = 'PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"\n'\
           '0 0,19 * * * cd {} && sh scripts/db_backup.sh >> /tmp/backup.log'.format(get_repo_path())
    run('echo "{}" | crontab -'.format(cron))


def setup_ssh():
    put('authorized_keys', '/home/{}/.ssh/authorized_keys'.format(USER))
    put('deploy_key', '/home/{}/.ssh/id_rsa'.format(USER))
    run('chmod 600 /home/{}/.ssh/id_rsa'.format(USER))


def get_repo_path():
    return REPO_PATH.format(user=USER, env=env["NAME"])
