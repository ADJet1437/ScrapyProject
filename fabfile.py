from fabric.api import env, put, sudo, run
from fabric.context_managers import cd, settings, hide
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.colors import green, yellow
#from deploy import setup_folder

USER='alascrapy'
GROUP='alatest'
GECKODRIVER_URL = "https://github.com/mozilla/geckodriver/releases/download/v0.11.1/geckodriver-v0.11.1-linux64.tar.gz"
GECKODRIVER_ARCHIVE = "geckodriver-v0.11.1-linux64.tar.gz"
CHROMEDRIVER_URL = "https://chromedriver.storage.googleapis.com/2.34/chromedriver_linux64.zip"
CHROMEDRIVER_ARCHIVE = "chromedriver_linux64.zip"

env.project = 'alascrapy'
env.install_root = '/home/alascrapy/alaScrapy/'
env.user = USER
env.group = GROUP
env.dev = False

def wget(url):
    run('wget %s' % url)

def untar(filename):
    run('tar -xzf %s' % filename)

def unzip(filename):
    run('unzip -o {}'.format(filename))

def live():
    env.hosts = ['alascrapy901.office.alatest.se',
                 'alascrapy902.office.alatest.se',
                 'alascrapy903.office.alatest.se'
                ]

def dev():
    env.dev = True

def setup_folder(path, owner="", mode="", group=""):
    """  Create folders missing for :path to exist, using sudo,
    setting owner and permissions as specified
    @param owner: the owner of the folder
    @param mode: mode of the folder
    @param group: group of the folder
    """
    group = env.group if not group else group

    with settings():
        if not exists(path, use_sudo=True):
            sudo("mkdir -p %s" % path)
    if mode:
        sudo("chmod %(mode)s %(path)s" % locals())
    sudo("chown %(owner)s:%(group)s %(path)s" % locals())

def deploy():
    rsync_project(remote_dir=env.install_root, local_dir=".", delete=True,
                  exclude=['build', 'dist', '*.pyc', '.hg', '.git', '.tox', 'alascrapy.egg-info'])
    if not env.dev:
        run("mv %s/alascrapy/conf/alascrapy.conf.live %s/alascrapy/conf/alascrapy.conf" % (env.install_root, env.install_root))

    with cd(env.install_root):
        sudo("pip install --upgrade .")

    if env.dev:
        return

    #setup amazon review publisher
    run("crontab -l | sed '/amazon_reviews_publisher.py/d' > /tmp/crontab")
    run('echo "30 * * * * %s/scripts/amazon_reviews_publisher.py" '
        '>> /tmp/crontab' %
        env.install_root) # Capture crontab; delete old entry
    run('crontab /tmp/crontab')
    run('rm -f /tmp/crontab')

def setup_gecko_driver():
    with cd("/tmp"):
        wget(GECKODRIVER_URL)
        untar(GECKODRIVER_ARCHIVE)
        run("rm %s" % GECKODRIVER_ARCHIVE)
        run("chmod +x geckodriver")
        sudo("mv geckodriver /usr/local/bin")

def setup_chrome_driver():
    with cd("/tmp"):
        wget(CHROMEDRIVER_URL)
        unzip(CHROMEDRIVER_ARCHIVE)
        run("rm %s" % CHROMEDRIVER_ARCHIVE)
        run("chmod +x chromedriver")
        sudo("mv chromedriver /usr/local/bin")

def setup_project():
    sudo("mkdir -p /var/log/alaScrapy")
    sudo("chown alascrapy:alatest /var/log/alaScrapy")
    sudo("mkdir -p /var/local/load/running/")
    sudo("chown alascrapy:alatest /var/local/load/running/")
    sudo("mkdir -p /var/local/load/finished/")
    sudo("chown alascrapy:alatest /var/local/load/finished/")
    sudo("mkdir -p /var/local/load/amazon/")
    sudo("chown alascrapy:alatest /var/local/load/amazon/")
    sudo("mkdir -p /var/log/load/")
    sudo("chown alascrapy:alatest /var/log/load/")
    sudo("chown -R root:alatest /var/www/html")
    sudo("chmod -R g+w /var/www/html")

    setup_folder(env.install_root, mode="2774")
    #cleanser:  python-amqplib
    sudo("""apt-get install python-setuptools \
                            python-dev \
                            python-mock \
                            python-amqplib \
                            libmysqlclient-dev \
                            libxml2-dev \
                            libxslt1-dev \
                            xvfb \
                            apache2 \
                            libtiff5-dev \
                            libjpeg8-dev \
                            zlib1g-dev \
                            libfreetype6-dev \
                            liblcms2-dev \
                            libgconf-2-4 \
                            libwebp-dev \
                            libxi6 \
                            tcl8.6-dev \
                            tk8.6-dev \
                            python-tk \
                            python-requests \
                            chromium-browser=63.0.* \
                            unzip""")
    sudo("chown -R %s:%s %s " % (USER, GROUP, env.install_root))

    setup_gecko_driver()
    setup_chrome_driver()

def setup_scheduler():
    run("crontab -l | sed '/scheduler.py/d' > /tmp/crontab")
    run('echo "5 * * * * %s/alascrapy/scheduler.py" >> /tmp/crontab' % env.install_root) # Capture crontab; delete old entry
    run('crontab /tmp/crontab')
    run('rm -f /tmp/crontab')

def setup_listener():
    install = confirm("Warning: All spiders currently running will be stopped. Do you wish to continue?")
    if not install:
        return

    sudo("stop alascrapy", warn_only=True)
    sudo("cp %s/alascrapy/conf/upstart/alascrapy.conf /etc/init/" %
         (env.install_root))
    sudo("initctl reload-configuration")
    sudo("start alascrapy")

def deploy_tool_service():
    service_root = env.install_root
    sudo("chmod a+rwx " + service_root + "alascrapy/spiders")
    sudo("chmod a+rwx " + service_root + "auto_generate_scripts/server/script_generator")
    sudo("chmod a+rwx " + "/var/log/alaScrapy/spiders.log")
    sudo("sudo rm -rf /usr/local/lib/python2.7/dist-packages/alascrapy-1.0-py2.7.egg/")
