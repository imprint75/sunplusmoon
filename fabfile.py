from fabric.api import env, run, prompt, warn, settings, hide
from fabric.colors import green, blue
from fabric.context_managers import cd
from fabric.operations import sudo
from fabric.contrib.files import exists

WORKING_DIR = '/srv/sunplusmoon'
PROJECT_NAME = 'sunplusmoon'
VENV_DIR = 'sunplusmoon_env'
GIT_REPO = 'git@github.com:imprint75/sunplusmoon.git'


def vagrant():
    env.hosts = ['192.168.33.102']
    env.user = 'vagrant'
    env.password = 'vagrant'


def prod():
    env.hosts = ['sunplusmoon.com']
    env.user = 'sean'


def testing():
    run('ls -lah')


def build():
    make_directory()
    apt_update()
    add_apt_repo()
    create_log_dirs()
    apt_update()
    install_nginx()
    install_uwsgi()
    install_python()
    install_git()
    mysql_install()
    create_mysql_db()
    create_mysql_user()
    create_env()
    upgrade_distribute()
    install_pip_reqs()
    link_confs()
    restart()


def make_directory(dir_name=PROJECT_NAME):
    with cd('/srv/'):
        if not exists(dir_name):
            sudo('mkdir {}'.format(dir_name))
        sudo('chown {0}:{0} {1}'.format(env.user, dir_name))


def git_clone_repo(dir_name=WORKING_DIR):
    with cd(WORKING_DIR):
        sudo('git clone {} {}'.format(GIT_REPO, PROJECT_NAME))


def create_env(venv=VENV_DIR):
    with cd(WORKING_DIR):
        run('virtualenv {}'.format(venv))


def upgrade_distribute(venv=VENV_DIR):
    command = '{}/{}/bin/pip install --upgrade distribute'
    run(command.format(WORKING_DIR, venv))


def install_pip_reqs(venv=VENV_DIR):
    command = '{0}/{1}/bin/pip install --upgrade -r ' \
              '{0}/{2}/{2}/requirements.txt'
    run(command.format(WORKING_DIR, venv, PROJECT_NAME))


def link_confs(dir_name=WORKING_DIR, file_name=PROJECT_NAME):
    n1 = 'ln -s {0}/{1}/{1}/confs/{1} /etc/nginx/sites-available/{1}'
    sudo(n1.format(dir_name, file_name))
    u1 = 'ln -s {0}/{1}/{1}/confs/{1}.ini /etc/uwsgi/apps-available/{1}.ini'
    sudo(u1.format(dir_name, file_name))
    n2 = 'ln -s /etc/nginx/sites-available/{0} /etc/nginx/sites-enabled/{0}'
    sudo(n2.format(file_name))
    u2 = 'ln -s /etc/uwsgi/apps-available/{0}.ini ' \
         '/etc/uwsgi/apps-enabled/{0}.ini'
    sudo(u2.format(file_name))


def create_log_dirs():
    sudo('mkdir /var/www')
    sudo('mkdir /var/www/logs')
    sudo('touch /var/www/logs/error.log')
    sudo('touch /var/www/logs/access.log')


def fix_la():
    run("sed -i \"/alias la='ls -A'/c\ alias la='ls -lAh'\" /home/{}/.bashrc")


def restart():
    sudo('service nginx restart')
    sudo('service uwsgi restart')


def deploy():
    with cd('/'.join([WORKING_DIR, PROJECT_NAME])):
        sudo('git pull')
        install_pip_reqs()
        #command = '{}/{}/bin/python manage.py migrate'
        #run(command.format(WORKING_DIR, VENV_DIR))
    restart()


### apt-get stuff ###


def add_apt_repo():
    sudo('apt-get install python-software-properties')


def apt_update():
    sudo('apt-get update')


### ssh key stuff ###


def ssh_setup():
    if not exists('~/.ssh/'):
        print "--ssh directory doesnt exist.  creating"
        run('mkdir ~/.ssh')
    if exists('~/.ssh/id_rsa.pub') or exists('~/.ssh/id_rsa'):
        print "--keys exist.  bail"
    else:
        print "--keys dont exist.  copying local keys for github access"
        put('~/.ssh/id_rsa*', '~/.ssh/')
    run('chmod 600 ~/.ssh/id_rsa')


### installs ###


def install_nginx():
    sudo('apt-get install nginx-full')


def install_uwsgi():
    sudo('apt-get install uwsgi uwsgi-plugin-python')


def install_python():
    sudo('apt-get install python-setuptools')
    sudo('apt-get install python-virtualenv')
    sudo('apt-get install python-dev')
    sudo('apt-get install build-essential')


def install_git():
    run('sudo apt-get install git')


def check_for_bin():
    run('cd ~')
    if not exists('bin'):
        print "directory doesn't exist.  creating"
        run('mkdir bin')
    thepath = run('echo $PATH')
    currentdir = run('pwd')
    dir_components = currentdir.split('/')
    filter(None, dir_components)
    dir_components.append('bin')
    newdir = '/'.join(dir_components)
    if newdir not in thepath:
        run('echo PATH=$PATH:{} >> .profile'.format(currentdir))


def install_emacs24():
    sudo('add-apt-repository ppa:cassou/emacs')
    apt_update()
    sudo('apt-get install emacs24 emacs24-el emacs24-common-non-dfsg')


def install_twisted():
    #sudo('add-apt-repository ppa:twisted-dev/ppa')
    #apt_update()
    sudo('apt-get install python-twisted')


def install_node():
    sudo('add-apt-repository ppa:chris-lea/node.js')
    sudo('apt-get update')
    sudo('apt-get install python g++ make nodejs')


def install_mongodb():
    sudo('apt-key adv --keyserver '
         'hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
    run("echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart "
        "dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list")


def install_mysql():
    sudo('apt-get install mysql-server mysql-client')
    sudo('apt-get install libmysqlclient-dev')


def create_mysql_db(password=None):
    user = 'root'
    dbname = PROJECT_NAME
    if password:
        run('mysqladmin -u {} -p{} create {}'.format(user, password, dbname))
    else:
        run('mysqladmin -u {} create {}'.format(user, dbname))


def create_mysql_user():
    run("echo \"CREATE USER 'sunplusmoon'@'localhost' IDENTIFIED BY 'sunplusmoon';\"")
    run("echo "
        "\"GRANT ALL PRIVILEGES ON sunplusmoon.* "
        "  To 'sunplusmoon'@'localhost' "
        "  IDENTIFIED BY 'sunplusmoon';\" | mysql -u root")


def create_django_tables():
    command = '{0}/{1}/bin/python {0}/{2}/manage.py syncdb'
    run(command.format(WORKING_DIR, VENV_DIR, PROJECT_NAME))


def apt_get(*packages):
    sudo('apt-get -y --no-upgrade install %s' % ' '.join(packages),
         shell=False)


def mysql_install():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show mysql-server')
    if result.failed is False:
        warn('MySQL is already installed')
        return
    mysql_password = prompt('Please enter MySQL root password:')
    sudo('echo "mysql-server-5.5 mysql-server/root_password password '
         '%s" | debconf-set-selections' % mysql_password)
    sudo('echo "mysql-server-5.5 mysql-server/root_password_again password '
         '%s" | debconf-set-selections' % mysql_password)
    apt_get('mysql-server')
    sudo('apt-get install libmysqlclient-dev')
