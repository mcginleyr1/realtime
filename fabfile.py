import os.path

import fabric.api as api
import fabric.context_managers
import fabric.operations as ops

#Run example fab -H root@dev-rmcginley-1.monetate.net -i ~/.ssh/id_rsa -u root install

DEPLOY_PATH = os.path.join('/', 'root', 'realtime')

YUM_DEPENDENCIES = [
    'readline',
    'readline-devel',
    ]

def install():
    install_python_27()
    install_postgres()
    install_pip()
    install_python_deps()

def install_pip():
    api.sudo('easy_install-2.7 pip')

def install_prereqs():
    api.sudo('yum install %s' % ' '.join(YUM_DEPENDENCIES))

def install_postgres():
    install_prereqs()

    api.run('wget http://ftp.postgresql.org/pub/source/v9.1.2/postgresql-9.1.2.tar.gz')
    api.run('tar xvf postgresql-9.1.2.tar.gz')
    api.run('cd postgresql-9.1.2 && ./configure')
    api.run('cd postgresql-9.1.2 && make')
    api.sudo('cd postgresql-9.1.2 && make install')

def install_python_27():
    api.run('wget http://python.org/ftp/python/2.7.2/Python-2.7.2.tgz')
    api.run('tar xvf Python-2.7.2.tgz')
    api.run('cd Python-2.7.2/ && sh configure')
    api.run('cd Python-2.7.2/ && make')
    api.sudo('cd Python-2.7.2/ && make install')
    api.run('wget http://pypi.python.org/packages/2.7/s/setuptools/' \
            'setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea')
    api.sudo('sh setuptools-0.6c11-py2.7.egg')

def install_python_deps():
    with fabric.context_managers.cd(DEPLOY_PATH):
        api.sudo('pip-2.7 install -r requirements.txt')

def deploy():
    with fabric.context_managers.cd(DEPLOY_PATH):
        api.run('git checkout master')
        api.run('git pull')

    install_python_deps()

def transfer_app():
    api.sudo('mkdir realtime')
    ops.put('css', '~/realtime/.')
    ops.put('html', '~/realtime/.')
    ops.put('javascript', '~/realtime/.')
    ops.put('monetate', '~/realtime/.')
    ops.put('requirements.txt', '~/realtime/.')
