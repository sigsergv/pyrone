.. include:: ../README.txt

Installing for nginx uWSGI
==========================

Prepare nginx site
------------------

You need to create nginx config file for your site.

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

    sudo apt-get install python-virtualenv


Then initialize new virtual environment (remember ``$BLOG`` is pointing to application root
directory):

    virtualenv --no-site-packages $BLOG/env

Now you have to *activate* just installed environment:

    source $BLOG/env/bin/activate

Before installing Pyrone you have to install binary packages from your distribution that required to
compile binary python packages: ``libxslt1-dev gcc python2.6-dev``. Instead of ``python2.6-dev`` you should
install ``python2.7-dev`` if you're using Python version 2.7.

Download Pyrone distribution package (e.g. ``pyrone-1.0.tar.gz``) and install it, all python packages
Pyrone depends upon will be downloaded and installed automatically:

    pip install pyrone-0.1.tar.gz

Now create mysql database (if you've chosen mysql and not sqlite database engine driver), type in 
mysql root console:

    CREATE DATABASE pyrone_blog;
    CREATE USER 'pyrone_blog_user'@'localhost' IDENTIFIED BY 'pbpass';
    GRANT ALL ON pyrone_blog.* TO 'pyrone_blog_user'@'localhost';

Also you have to configure encoding issues for the mysql server.

Now prepare the application configuration files:

   cd $BLOG
   cp ./env/share/pyrone/sample-config/production.ini .

Open file ``production.ini`` in your favourite text editor and change default database connection
parameters to yours.

Now check that you've configured application properly, for that execute the following command inside
the directory ``$BLOG``:

    ./env/bin/paster serve production.ini

If configuration steps were performed correctly you should see somethign like this:

    Starting server in PID 5712.
    serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

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

First you need to install ``python`` (version 2.6 is recommended), you'll also
need python package ``virtualenv``, you can install them using command

    sudo apt-get install python2.6 python-virtualenv
    
Now you have to choose directory where you'll install virtual environment for ``pyramid``,
it should be somewhere in your home directory, don't install it in the system directories.

Go to selected directory (create it if required) and issue the following command:

    virtualenv --no-site-packages ./env

You'll get directory ``env`` with new virtual environment, now you should *activate* it, after 
activation all required commands will be executed from your virtual environment, not from the
system. Required commands are: ``python``, ``pip`` etc. So activate:

    source ./env/bin/activate

Install packages required for the application:

    pip install pyramid SQLAlchemy markdown pytz hurry.filesize tweepy zope.sqlalchemy pyramid_beaker decorator nose coverage Babel
    
Wait until it finish downloading and installing the packages.

Also you'll need to install additional binary packages:

    pip install lxml PIL

The require install ``gcc`` and other stuff like ``libxml2-dev``.

Tests and coverage
------------------

Running the tests:

    python setup.py test -q
    
Collecting coverage information:

    nosetests --cover-package=pyrone --cover-erase --with-coverage
   
Localization and internationalization
-------------------------------------

Pyrone uses ``Babel`` package to maintain ``gettext``-translation file. Here are the most used
commands.

Collect messages from source files:

    python setup.py extract_messages

Start new language ("es", Spanish in this case):

    python setup.py init_catalog -l es

Update messages (using .pot-file created by ``extract_messages`` command):

    python setup.py update_catalog

Or collect and update in one step:

    python setup.py extract_messages update_catalog

Compile translation files:

    python setup.py compile_catalog

Running application
-------------------

To start development server use the following command:

    paster serve --reload development.ini
    
Release and packaging
---------------------

Prepare nginx runtime environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need ``supervisord`` package:

    pip install supervisor

Prepare application package
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* https://docs.pylonsproject.org/projects/pyramid_cookbook/dev/deployment.html

