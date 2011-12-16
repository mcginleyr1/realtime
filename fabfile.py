import fabric.api as api
import fabric.operations as ops

#Run example fab -H dev-rmcginley-1.monetate.net -i ~/.ssh/id_rsa -u root install

PYTHON_DEPENDENCIES = [
    'tornado', 
    'psycopg2', 
    'sqlalchemy',
    ]

YUM_DEPENDENCIES = [
    'postgresql',
    'postgresql-contrib',
    'postgresql-devel',
    'postgresql-server',
    ]


def install():
    install_python_27()
    install_postgres()
    install_pip()
    install_python_deps()

def install_pip():
    api.sudo('easy_install pip')

def install_postgres():
    api.sudo('yum install %s' % (' '.join(YUM_DEPENDENCIES)))

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
    api.sudo('pip install %s' %  (' '.join(PYTHON_DEPENDENCIES)))
    transfer_brukva()


def transfer_brukva():
    ops.put('tools/brukva', '~/')
    api.sudo('./brukva/setup.py install')

def transfer_app():
    api.sudo('mkdir realtime')
    ops.put('css', '~/realtime/.')
    ops.put('html', '~/realtime/.')
    ops.put('javascript', '~/realtime/.')
    ops.put('monetate', '~/realtime/.')
