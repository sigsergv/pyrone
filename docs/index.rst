.. include:: ../README.txt

Installing for nginx in simple proxy mode
=========================================

Prepare runtime directory
-------------------------

You need to prepare directory where your application will be installed, let's assume
it's ``/home/user/pyrone-blog`` (we'll later reference it as ``$BLOG``).

Inside ``$BLOG`` you have to create virtual environment, application directory, configuration
files.

Prepare virtual environment
---------------------------

First install package ``python-virtualenv`` using ``apt-get`` (or whatever you're using for installing
packages):

::

    sudo apt-get install python-virtualenv


Then initialize new virtual environment (remember ``$BLOG`` is pointing to application root
directory):

::

    virtualenv --no-site-packages $BLOG/env

Now you have to *activate* just installed environment:

::

    source $BLOG/env/bin/activate

Before installing Pyrone you have to install binary packages from your distribution that required to
compile binary python packages: ``libxslt1-dev gcc python2.6-dev``. Instead of ``python2.6-dev`` you should
install ``python2.7-dev`` if you're using Python version 2.7.

Download Pyrone distribution package (e.g. ``pyrone-1.0.tar.gz``) and install it, all python packages
Pyrone depends upon will be downloaded and installed automatically:

::

    pip install pyrone-0.1.tar.gz

Or you can install directly from pypi repository:

::

    pip install pyrone

This will install latest pyrone version.

If you are going to use MySQL as the database engine you are need to install ``MySQL-python`` package:

::

    pip install MySQL-python


Now create mysql database (if you've chosen mysql and not sqlite database engine driver), type in 
mysql root console:

::

    CREATE DATABASE pyrone_blog;
    GRANT ALL ON pyrone_blog.* TO 'pyrone_blog_user'@'localhost' IDENTIFIED BY 'pbpass';

Also you have to configure encoding issues for the mysql server.

Now prepare the application configuration files:

::

   cd $BLOG
   cp ./env/share/pyrone/examples/production.ini .

Open file ``production.ini`` in your favourite text editor and change default database connection
parameters to yours.

Now check that you've configured application properly, for that execute the following command inside
the directory ``$BLOG``:

::

    ./env/bin/pserve production.ini

If configuration steps were performed correctly you should see somethign like this:

::

    Starting server in PID 5712.
    serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

Prepare nginx site
------------------

You need to create nginx config file (e.g. ``pyrone-blog.conf``) for your site. Sample config is included into 
the distribution package and could be found by the path ``$BLOG/env/share/pyrone/examples/pyrone-blog-nginx.conf``.

::

    upstream pyrone-blog {
            server 127.0.0.1:5000;
            #server 127.0.0.1:5001;
    }

    server {
            listen   81; ## listen for ipv4; this line is default and implied
            #listen   [::]:80 default ipv6only=on; ## listen for ipv6

            server_name blog.example.com;
            access_log /home/user/pyrone-blog/nginx-access.log;

            location / {
                    proxy_set_header        Host $host:$server_port;
                    proxy_set_header        X-Real-IP $remote_addr;
                    proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
                    proxy_set_header        X-Forwarded-Proto $scheme;

                    client_max_body_size    10m;
                    client_body_buffer_size 128k;
                    proxy_connect_timeout   60s;
                    proxy_send_timeout      90s;
                    proxy_read_timeout      90s;
                    proxy_buffering         off;
                    proxy_temp_file_write_size 64k;
                    proxy_pass http://pyrone-blog;
                    proxy_redirect          off;
            }

            # uncomment if you want nginx to serve static files
            #location /static {
            ## uncoment either 2.6 OR 2.7, not both!
            #    root                    /home/user/pyrone-blog/env/lib/python2.7/site-packages/pyrone/static;
            #    root                    /home/user/pyrone-blog/env/lib/python2.6/site-packages/pyrone/static;
            #    expires                 30d;
            #    add_header              Cache-Control public;
            #    #access_log              off;
            #}

    }

Edit the file using real data (your path instead of ``/home/user/pyrone-blog`` etc) and put it into the nginx sites directory.

Using supervisord to automate application execution
---------------------------------------------------

Sample ``supervisord.conf`` is provided in the distribution package, find in at 
``$BLOG/env/share/pyrone/examples/supervisord.conf``. Just copy to the directory
``$BLOG``. You have to edit this file and set valid system user name there.

Sample init.d script you'll find at the path ``$BLOG/env/share/pyrone/examples/supervisord-pyrone``.
Copy it to the directory ``/etc/init.d`` and reconfigure init procedure.

Installing on nginx+uWSGI (ububtu/debian only)
===============================================

First you need to install ``uWSGI`` packages:

::

    sudo apt-get install uwsgi uwsgi-plugin-python

Then you have to create nginx configuration file, something like this:

::

    server {
            listen 80;
            server_name blog.example.com;
            access_log /home/user/pyrone-blog/nginx-access.log;

            location / {
                    include uwsgi_params;
                    uwsgi_pass 127.0.0.1:5000;
            }
            
            # uncomment lines below to allow processing of static files by nginx 
            #location /static {
            #    root                    /home/user/pyrone-blog/env/lib/python2.6/site-packages/pyrone/;
            #    expires                 30d;
            #    add_header              Cache-Control public;
            #    #access_log              off;
            #}

    }



Now create uwsgi config file for the blog application, it looks like::

    [uwsgi]
    uid = user
    gid = usergroup
    socket = 127.0.0.1:5000
    home = /home/user/pyrone-blog/env/
    plugins = python
    paste = config:/home/user/pyrone-blog/production.ini
    # uncomment line below (and comment line above) to include debug logging output from the application
    #ini-paste-logged = /home/user/pyrone-blog/production.ini
    post-buffering = 8192 # this is workaround for files upload issue ( https://bitbucket.org/cancel/pyrone/issue/23 )
    # uncomment to enable web debugger
    # processes = 1
    cache = 1000

Don't forget to edit this file and replace default values (user, usergroup) with real ones. Place file to the
directory ``/etc/uwsgi/apps-available`` and create symlink to this file in the directory ``/etc/uwsgi/apps-enabled``::

    sudo ln -s /etc/uwsgi/apps-available/blog.ini /etc/uwsgi/apps-enabled

Pyrone uses ``cache`` plugin of uWSGI.


Sample configuration files
==========================

You can find up-to-date samples of various configuration files in the directory ``examples``.

Some other installation issues
==============================

Site icons (favicons)
---------------------

Pyrone package doesn't contain site icons, so you have to configure them separately. By default
pyrone looks for files ``favicon.png`` and ``favicon.ico`` in the same directory where
your production.ini file is placed. But you can change paths manually, just open file ``production.ini``
in the text editor, then find keys ``pyrone.favicon_ico`` and ``pyrone.favicon_ico`` (in 
the section ``[app:pyrone]``), and change values from default to actual paths to these icons.

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
need python package ``virtualenv``, you can install them using command

::

    sudo apt-get install python2.7 python2.7-dev python-virtualenv
    
Now you have to choose directory where you'll install virtual environment for ``pyramid``,
it should be somewhere in your home directory, don't install it in the system directories. 
Package ``python2.7-dev`` is required to compile some modules to increase performance.

Go to selected directory (create it if required) and issue the following command:

::

    virtualenv --no-site-packages ./env

You'll get directory ``env`` with new virtual environment, now you should *activate* it, after 
activation all required commands will be executed from your virtual environment, not from the
system. Required commands are: ``python``, ``pip`` etc. So activate:

::

    source ./env/bin/activate

Install packages required for the application (there are three separate commands, it's because of some bug
in pip dependencies resolver):

::

    pip install paste
    pip install pastescript
    pip install pyramid SQLAlchemy markdown pytz hurry.filesize tweepy zope.sqlalchemy pyramid_beaker decorator nose coverage Babel
    
Wait until it finish downloading and installing the packages.

Also you'll need to install additional binary packages:

::

    sudo apt-get install gcc libxml2-dev libxslt1-dev libjpeg8-dev libfreetype6-dev zlib1g-dev
    pip install lxml

Pyrone also requires PIL imaging library, in this document we install it into our virtualenv
environment, and for Debian/Ubuntu there is a problem: PIL compiles without some necessary
features. Unfortunately there is no fix to that problem so you need the workaround
described below.

::

    ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libz.so $VIRTUAL_ENV/lib/
    ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libfreetype.so $VIRTUAL_ENV/lib/
    ln -s /usr/lib/`dpkg-architecture -qDEB_HOST_MULTIARCH`/libjpeg.so $VIRTUAL_ENV/lib/

After that you can install PIL:

::

    pip install PIL


If you are planning to use mysql driver I'd recommend you also install package ``MySQL-python``:

::

    pip install MySQL-python

Now install *development* version of pyrone, to do so switch to the directory with the source code and execute this
comman (stay in the same terminal, in the virtualenv activated session!):

::

    python setup.py develop

Copy configuration script ``development.ini`` from the directory ``examples`` to the same directory where ``setup.py`` is located, edit ``development.ini`` appropriately, but default preferences are just fine. By default pyrone development config uses sqlite database
engine.

Running application
-------------------

To start development server use the following command:

::

    pserve --reload development.ini
    
Tests and coverage
------------------

Running the tests:

::

    python setup.py test -q
    
Collecting coverage information:

::

    nosetests --cover-package=pyrone --cover-erase --with-coverage
   
Localization and internationalization
-------------------------------------

Pyrone uses ``Babel`` package to maintain ``gettext``-translation file. Here are the most used
commands.

Collect messages from source files:

::

    python setup.py extract_messages

Update messages (using .pot-file created by ``extract_messages`` command):

::

    python setup.py update_catalog
    python setup.py update_catalog_js

Or collect and update in one step:

::

    python setup.py extract_messages update_catalog extract_messages_js update_catalog_js

Compile translation files (for python code):

::

    python setup.py compile_catalog

JavaScript code a bit tricky, compiled js files are immediately placed into the 
``pyrone/static/lang`` directory so after compiling these files have to be
commited:

::

    python setup.py compile_catalog_js

Start new language ("es", Spanish in this example, both for python and javascript code, do this ONCE for one language):

::

    python setup.py init_catalog -l es
    python setup.py init_catalog_js -l es

Code syntax highlight in the articles
-------------------------------------

Pyrone uses Markdown extension `codehilite` and to work properly it requires corresponding
css file, currently it's commited as static resource `static/styles/pygments.css` and
generated by the following python code

::

    from pygments.formatters import HtmlFormatter
    print HtmlFormatter().get_style_defs('.codehilite')


Building documentation
----------------------

In order to build project documentation switch to the directory `doc` and execute command `make build-html` there.

This command requires system package `python-docutils`, so install it first:

::

    sudo apt-get install python-docutils

Release and packaging
---------------------

Prepare and upload source package to pypi:

::

    python setup.py clean sdist upload
