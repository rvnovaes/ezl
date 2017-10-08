from fabric.api import env, task, local, run
from fabric.contrib.project import rsync_project
import tempfile


env.hosts = ['sinova@13.68.213.60']
PROJECT_PATH = '/home/sinova/ezl_demo'


@task
def deploy():
    tmp_dir = tempfile.mkdtemp()
    local("hg clone . {}".format(tmp_dir))
    rsync_project(local_dir="{}/.".format(tmp_dir),
                  remote_dir=PROJECT_PATH,
                  exclude=['.hg', 'staticfiles', 'media', 'pyc', '.orig'])
    local("rm -rf {}".format(tmp_dir))
    run("make deploy")
