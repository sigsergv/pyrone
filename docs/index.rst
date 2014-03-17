.. include:: ../README.txt

Installing in production mode
=============================

Pyrone is a standard WSGI application so you can use any method for provisioning WSGI 
apps. However in this instruction only one method is covered: Debian/Ubuntu + nginx 
+ uwsgi + mysql. Application requires Python version 3.3 or greater, python 
version 2 is not supported. 

I recommend you (for security reasons) to create separate system user for the application. In this
manual all instructions assume system user ``blog`` with home directory ``/home/blog``, it's a regular
non-privileged user.

All linux shell commands in this manual have prefixes, if prefix is ``$`` then command must be executed
using user ``blog`` shell session, and commands with the prefix ``#`` must be executed in root shell session.


MySQL setup
-----------

Install MySQL (you need to choose password for user ``root``, you may skip this step if you have installed
and configured MySQL server already)::

    # apt-get install mysql-server

Now create database and database user for Pyrone, use the following commands in the mysql root console::

    CREATE DATABASE pyrone_blog;
    GRANT ALL ON pyrone_blog.* TO 'pyrone_blog_user'@'localhost' IDENTIFIED BY 'pbpass';

Choose another password instead of ``pbpass`` (and remember it).


Install pyrone in virtual environment
-------------------------------------

We use virtualenv to install Pyrone runtime.

You need to prepare directory where your application should be installed, let's assume
it's ``/home/blog/pyrone3-blog``.

Inside this directory you need to create virtual environment, application directory, configuration
files, so let's begin.


Prepare virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install package ``python-virtualenv`` and other required packages::

    # apt-get install python-virtualenv dpkg-dev python3 python3-dev gcc libxml2-dev libxslt1-dev libjpeg8-dev libfreetype6-dev zlib1g-dev libmysqlclient-dev

Then initialize new virtual environment::

    $ mkdir /home/blog/pyrone3-blog/
    $ virtualenv -p python3 --no-site-packages /home/blog/pyrone3-blog/env

Now you have to *activate* just installed environment::

    $ source /home/blog/pyrone3-blog/env/bin/activate

After this command your shell session is slightly modified and almost all python-related command
will be executed in just created virtual environment. And you are *required* to stay in this session
and execute all remaining commands there!

Now install Pyrone from python packages repository::

    $ pip install pyrone

This will install latest stable version of Pyrone along with all required packages.

Alternatively you can install it from local package file (it will automatically install 
all dependencies too)::

    $ pip install pyrone-1.0.0.tar.gz

We are using MySQL so install proper mysql connector::

    $ pip install --allow-external mysql-connector-python mysql-connector-python

Now prepare the application configuration files::

   $ cd /home/blog/pyrone3-blog/
   $ cp ./env/share/pyrone/examples/production.ini .

Open file ``production.ini`` in any text editor and change default database connection
parameters to yours. If you've followed this instruction from the beginning you'll need to change
database password only: find the string ``pbpass`` and replace it with the actual password.

Now we need to setup the database, to do this execute the following command::

    $ cd /home/blog/pyrone3-blog
    $ pyronedbinit --sample-data --sample-data-file=env/share/pyrone/sample-data.json production.ini

Check that application is configured properly, to do that just execute the following command inside
the directory ``/home/blog/pyrone3-blog``::

    $ /home/blog/pyrone3-blog/env/bin/pserve production.ini

If configuration steps were performed correctly you should see something like this::

    Starting server in PID 5712.
    serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

Now press Ctrl+C to terminate server.

Congratulation! You've just installed pyrone application server, so you can proceed to next steps: 
installing/configuring web server (nginx) and installing/configuring middle layer between pyrone 
runtime and web server (uWSGI).

Configuring uWSGI
-----------------

First install uWSGI::

    # apt-get install uwsgi uwsgi-plugin-python3

Then create configuration file for the application::

    # cp /home/blog/pyrone3-blog/env/share/pyrone/examples/pyrone-uwsgi.ini /etc/uwsgi/apps-available/
    # ln -s /etc/uwsgi/apps-available/pyrone-uwsgi.ini /etc/uwsgi/apps-enabled

And restart uWSGI::

    # service uwsgi restart


Nginx setup
-----------

Install nginx::

    # apt-get install nginx

Then  create nginx configuration file for Pyrone's site::

    # cp /home/blog/pyrone3-blog/env/share/pyrone/examples/pyrone-blog-nginx-uwsgi.conf /etc/nginx/sites-available/

In this file you need to change hostname (default value is ``blog.example.com``).

After that create symlink to enable nginx site and restart it::

    # ln -s /etc/nginx/sites-available/pyrone-blog-nginx-uwsgi.conf /etc/nginx/sites-enabled/
    # service nginx restart

If you want to serve HTTPS requests too you need to copy another sample file: 
``/home/blog/pyrone3-blog/env/share/pyrone/examples/pyrone3-blog-nginx-uwsgi-ssl.conf``, in that case you must
create proper ssl certificates and other related stuff I don't want to describe here.

That's all! Open your site in the browser and enjoy blogging. Default local login credentials (username/password): ``admin/setup``,
don't forget to change it.


Some post-install stuff
-----------------------

Access
~~~~~~

Default administrator login is ``admin``, password is ``setup``.

Site icons (favicons)
~~~~~~~~~~~~~~~~~~~~~

Pyrone package doesn't contain site icons, so you have to configure them separately. By default
pyrone looks for files ``favicon.png`` and ``favicon.ico`` in the same directory where
your production.ini file is placed. But you can change paths manually, just open file ``production.ini``
in the text editor, then find keys ``pyrone.favicon_ico`` and ``pyrone.favicon_png`` (in 
the section ``[app:pyrone]``), and change values from default to real paths to these icons.

Backup and restore
~~~~~~~~~~~~~~~~~~

For security reasons you cannot upload backup files using web interface. You must upload it into special
directory using scp or ssh. This special directory is ``/home/blog/pyrone3-blog/storage/backups``.

Serving static files
~~~~~~~~~~~~~~~~~~~~

By default Pyrone handles its static files (scrits, styles etc), if you want to pass static files processing
to nginx you should edit nginx site configuration file and uncomment static files section.

Sample configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~

You will find up-to-date samples of various configuration files in the directory ``examples`` (in the source tree)
or in the directory ``/home/blog/pyrone3-blog/env/share/pyrone/examples`` (on production server after Pyrone install).


Some other installation issues
==============================

If you find some obstacles using this manual in practice feel free to submit issue to our issue tracker: 
https://github.com/sigsergv/pyrone/issues.



Development
===========

In this section I will describe in details how to prepare development environment for pyrone.

Virtual environment
-------------------

It's strongly recommended to use virtual python environment with locally 
installed ``pyramid`` and other required packages. In this document
it's assumed that ``python`` binary is located in your virtual environment.
The same thing for ``easy_install`` or ``pip`` executables.

To make your life easier use script ``bin/activate`` from virtual environment to 
update local environment variables (``PATH`` etc), in that case you will be able
to execute binaries like ``python`` and ``easy_install`` without specifying full path
to them.

Preparing virtual environment (macos x/brew)
--------------------------------------------

You need to install ``brew`` (http://brew.sh/) first, that topic is not covered in this document.

When ``brew`` is installed you need to install required packages::

    $ brew install python3

You also need to install some additional packages required for python modules compiling::

    $ brew install

Then install ``virtualenv``::

    $ pip install virtualenv

Now create directory for virtual environments and init virtualenv there::

    $ mkdir -p ~/python-ves/pyrone
    $ virtualenv -p python3 --no-site-packages ~/python-ves/pyrone

And activate it::

    $ source ~/python-ves/pyrone/bin/activate

And install all required packages (execute this command in the activated 
environment and from project directory)::

    $ python setup.py develop

And some additional developer packages::

    $ pip install waitress

Copy configuration script ``development.ini`` from the directory ``examples`` to the same directory 
where ``setup.py`` is located, edit ``development.ini`` appropriately, but default preferences are 
just fine. By default pyrone development config uses sqlite database
engine.


Preparing virtual environment (debian/ubuntu)
---------------------------------------------

It's assumed here and later that you're using Debian/Ubuntu linux distribution. So open
terminal now and proceed.

First you need to install ``python`` (version 3.3 or greater), you'll also
need python package ``virtualenv``, you can install them using following command::

    # apt-get install python3 python3-pip python-virtualenv

Also you'll need to install additional binary packages::

    # apt-get install gcc libxml2-dev libxslt1-dev libjpeg8-dev libfreetype6-dev zlib1g-dev
    
Now you have to choose directory where to install virtual environment for ``pyramid``,
it should be somewhere in your home directory, don't install it in the system directories.
Let's assume this directory is `~/python-ves/pyrone` (it's a recommended path)::

    $ mkdir -p ~/python-ves/pyrone

And create virtual environment in there::

    $ virtualenv -p python3 --no-site-packages ~/python-ves/pyrone

You now have the directory with new virtual environment, now you should *activate* it, after 
activation all required commands will be executed from your virtual environment, not from the
system. Required commands are: ``python``, ``pip`` etc. So activate::

    $ source ~/python-ves/pyrone/bin/activate

And install now all required python packages (execute this command in the activated 
environment and from project directory)::

    $ python setup.py develop

And install some additional packages required for development::

    $ pip install waitress

Copy configuration script ``development.ini`` from the directory ``examples`` to the same directory 
where ``setup.py`` is located, edit ``development.ini`` appropriately, but default preferences are 
just fine. By default pyrone development config uses sqlite database
engine.

Working with development server
-------------------------------

To start development server use the following command::

    $ pserve --reload development.ini

On first run or after database destroy you need to initialize database::

    $ python -m pyrone.scripts.pyronedbinit development.ini --sample-data

Tests and coverage
------------------

Running the tests (there are no tests yet though)::

    $ python setup.py test -q
    
Collecting coverage information::

    $ nosetests --cover-package=pyrone --cover-erase --with-coverage
   
Localization and internationalization
-------------------------------------

Pyrone uses ``Babel`` package to maintain ``gettext``-translation file. Here are the most used
commands.

Collect messages from source files (python only)::

    $ python setup.py extract_messages

Collect messages from source files (javascript only)::

    $ python setup.py extract_messages_js

Update messages (using .pot-file created by ``extract_messages`` command)::

    $ python setup.py update_catalog
    $ python setup.py update_catalog_js

Or collect and update in one step::

    $ python setup.py extract_messages update_catalog extract_messages_js update_catalog_js

Compile translation files (for python code)::

    $ python setup.py compile_catalog

JavaScript code a bit tricky, compiled js files are immediately placed into the 
``pyrone/static/lang`` directory so after compiling these files have to be
commited::

    $ python setup.py compile_catalog_js

Start new language ("es", Spanish in this example, both for python and javascript code, do this ONCE for one language)::

    $ python setup.py init_catalog -l es
    $ python setup.py init_catalog_js -l es

Code syntax highlight in the articles
-------------------------------------

Pyrone uses Markdown extension `codehilite` and to work properly it requires corresponding
css, currently it's commited as part of each style (in the file `blog.css`), and this css code
is generated by the following python code::

    from pygments.formatters import HtmlFormatter
    print(HtmlFormatter().get_style_defs('.codehilite'))


Building documentation
----------------------

In order to build project documentation switch to the directory `doc` and issue command `make build-html` there.

This command requires system package `python-docutils`, so install it first::

    # apt-get install python-docutils

As for macos you need to install docutils manually via pip command, for example::

    # pip install docutils

Release and packaging
---------------------

Prepare and upload source package to pypi::

    $ python setup.py clean sdist upload

Alternatively you could use the following command, it will ask you for password::

    $ python setup.py clean sdist upload
