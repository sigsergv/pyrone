.. include:: ../README.txt

Installing in production mode
=============================

Pyrone is a standard WSGI application so you can use any method for provisioning WSGI 
apps. In this instruction we describe installing process using Ubuntu/Debian OS with python version 2.7,
web server nginx, WSGI container server uWSGI and MySQL database engine.

I recommend you to create separate system user for the application, it's secure and simple. In this
manual all instructions assume system user ``blog`` with home directory ``/home/blog``, it's regular
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

You need to prepare directory where your application will be installed, let's assume
it's ``/home/blog/pyrone-blog``.

Inside this directory you need to create virtual environment, application directory, configuration
files, so let's begin.


Prepare virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

First install package ``python-virtualenv`` and other required packages::

    # apt-get install python-virtualenv dpkg-dev python2.7-dev gcc libxml2-dev libxslt1-dev libjpeg8-dev libfreetype6-dev zlib1g-dev libmysqlclient-dev

Then initialize new virtual environment::

    $ virtualenv --no-site-packages /home/blog/pyrone-blog/env

Now you have to *activate* just installed environment::

    $ source /home/blog/pyrone-blog/env/bin/activate

After this command your shell session is slightly modified and almost all python-related command
will be executed in just created virtual environment. And you are *required* to stay in this session
and execute all remaining commands there!

Unfortunately there is a bug in some of required 3rd party packages, so in order to install pyrone properly 
you should execute the following “magic”::

    $ ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libz.so $VIRTUAL_ENV/lib/
    $ ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libfreetype.so $VIRTUAL_ENV/lib/
    $ ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libjpeg.so $VIRTUAL_ENV/lib/

Now install Pyrone::

    $ pip install pyrone

This will install latest stable version of Pyrone all required packages.

As we are planning to use MySQL install also MySQL driver::

    $ pip install MySQL-python

Now prepare the application configuration files::

   $ cd /home/blog/pyrone-blog/
   $ cp ./env/share/pyrone/examples/production.ini .

Open file ``production.ini`` in any text editor and change default database connection
parameters to yours. If follow this instruction from the beginning you'll need to change
database password only: find the string ``pbpass`` and replace it with actual password.

Check that application is configured properly, to do that just execute the following command inside
the directory ``/home/blog/pyrone-blog``::

    $ /home/blog/pyrone-blog/env/bin/pserve production.ini

If configuration steps were performed correctly you should see something like this::

    Starting server in PID 5712.
    serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

Now press Ctrl+C to terminate server.

Congratulation! You've just installed pyrone runtime, so you can proceed to next steps: installing/configuring web server
(nginx) and installing/configuring middle layer between pyrone runtime and web server (uWSGI).

Configuring uWSGI
-----------------

First install uWSGI::

    # apt-get install uwsgi uwsgi-plugin-python

Then create configuration file for the application::

    # cp /home/blog/pyrone-blog/env/share/pyrone/examples/pyrone-uwsgi.ini /etc/uwsgi/apps-available/
    # ln -s /etc/uwsgi/apps-available/pyrone-uwsgi.ini /etc/uwsgi/apps-enabled

And restart uWSGI::

    # service uwsgi restart


Nginx setup
-----------

Install nginx::

    # apt-get install nginx

Then  create nginx configuration file for Pyrone's site::

    # cp /home/blog/pyrone-blog/env/share/pyrone/examples/pyrone-blog-nginx-uwsgi.conf /etc/nginx/sites-available/

In this file you need to change hostname (default value is ``blog.example.com``).

After that create symlink to enable nginx site::

    # ln -s /etc/nginx/sites-available/pyrone-blog-nginx-uwsgi.conf /etc/nginx/sites-enabled/
    # service nginx restart

If you want to serve HTTPS requests too you need to copy another sample file: 
``/home/blog/pyrone-blog/env/share/pyrone/examples/pyrone-blog-nginx-uwsgi-ssl.conf``, in that case you must
create proper ssl certificates and other related stuff I don't want to describe here.

That's all! Open your site in the browser and enjoy blogging. Default local login credentials (username/password): ``admin/setup``,
don't forget to change it.


Some post-install stuff
-----------------------

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
directory using scp or ssh. This special directory is ``/home/blog/pyrone-blog/storage/backups``.

Serving static files
~~~~~~~~~~~~~~~~~~~~

By default Pyrone handles its static files (scrits, styles etc), if you want to pass static files processing
to nginx you should edit nginx site configuration file and uncomment static files section.

Sample configuration files
~~~~~~~~~~~~~~~~~~~~~~~~~~

You will find up-to-date samples of various configuration files in the directory ``examples`` (in the source tree)
or in the directory ``/home/blog/pyrone-blog/env/share/pyrone/examples`` (on production server after Pyrone install).

Some other installation issues
==============================

If you find some obstacles using this manual in practice feel free to submit issue to our issue tracker: 
https://bitbucket.org/cancel/pyrone/issues.


Development
===========

Virtual environment
-------------------

It's strongly recommended to use virtual python environment with locally 
installed ``pyramid`` and other required packages. Further in this README.txt
it's assumed that ``python`` binary is located in your virtual environment.
The same thing for ``easy_install`` and ``pip`` executables.

To make your life easier use script ``bin/activate`` from virtual environment to 
update local environment variables (``PATH`` etc), in that case you will be able
to execute binaries like ``python`` and ``easy_install`` without specifying full path.

Preparing virtual environment
-----------------------------

It's assumed here and later that you're using Debian/Ubuntu linux distribution. So open
terminal now and proceed.

First you need to install ``python`` (version 2.7 is highly recommended), you'll also
need python package ``virtualenv``, you can install them using command::

    # apt-get install python2.7 python2.7-dev python-virtualenv
    
Now you have to choose directory where you'll install virtual environment for ``pyramid``,
it should be somewhere in your home directory, don't install it in the system directories. 
Package ``python2.7-dev`` is required to compile some modules to increase performance.

Go to selected directory (create it if required) and issue the following command::

    $ virtualenv --no-site-packages ./env

You'll get directory ``env`` with new virtual environment, now you should *activate* it, after 
activation all required commands will be executed from your virtual environment, not from the
system. Required commands are: ``python``, ``pip`` etc. So activate::

    $ source ./env/bin/activate

Install packages required for the application (there are three separate commands, it's because of some bug
in pip dependencies resolver)::

    $ pip install paste
    $ pip install pastescript
    $ pip install pyramid SQLAlchemy markdown pytz hurry.filesize tweepy zope.sqlalchemy pyramid_beaker decorator nose coverage Babel
    
Wait until it finish downloading and installing the packages.

Also you'll need to install additional binary packages::

    # apt-get install gcc libxml2-dev libxslt1-dev libjpeg8-dev libfreetype6-dev zlib1g-dev
    $ pip install lxml

Pyrone also requires PIL imaging library, in this document we install it into our virtualenv
environment, and for Debian/Ubuntu there is a problem: PIL compiles without some necessary
features. Unfortunately there is no fix to that problem so you need the workaround
described below.

::

    $ ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libz.so $VIRTUAL_ENV/lib/
    $ ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libfreetype.so $VIRTUAL_ENV/lib/
    $ ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libjpeg.so $VIRTUAL_ENV/lib/

After that you can install PIL::

    $ pip install PIL


If you are planning to use mysql driver I'd recommend you also install package ``MySQL-python``::

    $ pip install MySQL-python

Now install *development* version of pyrone, to do so switch to the directory with the source code and execute this
comman (stay in the same terminal, in the virtualenv activated session!)::

    $ python setup.py develop

Copy configuration script ``development.ini`` from the directory ``examples`` to the same directory where ``setup.py`` is located, edit ``development.ini`` appropriately, but default preferences are just fine. By default pyrone development config uses sqlite database
engine.

Running application
-------------------

To start development server use the following command::

    $ pserve --reload development.ini
    
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
css file, currently it's commited as static resource `static/styles/pygments.css` which
generated by the following python code::

    from pygments.formatters import HtmlFormatter
    print HtmlFormatter().get_style_defs('.codehilite')


Building documentation
----------------------

In order to build project documentation switch to the directory `doc` and issue command `make build-html` there.

This command requires system package `python-docutils`, so install it first::

    # apt-get install python-docutils

Release and packaging
---------------------

Prepare and upload source package to pypi::

    $ python setup.py clean sdist upload

Alternatively you could use the following command, it will ask you for password.

::

    $ python setup.py clean sdist upload






    
Outdated and not supported stuff
================================

``$BLOG`` is referred to `/home/blog/pyrone-blog`.

Using supervisord to automate application execution
---------------------------------------------------

Sample ``supervisord.conf`` is provided in the distribution package, find in at 
``$BLOG/env/share/pyrone/examples/supervisord.conf``. Just copy to the directory
``$BLOG``. You have to edit this file and set valid system user name there.

Sample init.d script you'll find at the path ``$BLOG/env/share/pyrone/examples/supervisord-pyrone``.
Copy it to the directory ``/etc/init.d`` and reconfigure init procedure.
