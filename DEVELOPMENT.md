Installation in development mode
================================


Foreword
--------

This document covers all aspects of setting up of Pyrone development environment, supported OSes are
linux (debian/ubuntu) and Mac OS X.


Virtual environment
-------------------

It's strongly recommended to use virtual python environment with locally 
installed `pyramid` and other required packages. In this document
it's assumed that `python` binary is located in your virtual environment.
The same thing for `easy_install` or `pip` executables.

To make your life easier use script `bin/activate` from virtual environment to 
alter local environment variables (`PATH` etc), in that case you will be able
to execute binaries like `python` and `easy_install` without specifying full path.

It's a good idea to place local virtual environment into a project directory and 
call it `.venv`, that name is mentioned in project .gitignore so it won't damage
repository.


Preparing virtual environment (Mac OS X)
----------------------------------------

First you need to install Python 3.4, download it from the official 
site: https://www.python.org/downloads/mac-osx/ . At the moment of this document writing
latest available stable version of Python 3.4 was 3.4.4 
<https://www.python.org/ftp/python/3.4.4/python-3.4.4-macosx10.6.pkg>

You also need to install Postgres.app from <http://postgresapp.com/>.

Then install `venv`:

    $ pyvenv-3.4 --without-pip .venv

And activate it:

    $ source .venv/bin/activate

Now to install setuptools and pip:

    $ curl https://bootstrap.pypa.io/ez_setup.py | python3.4 -
    $ rm setuptools-*.zip

Now you need to create symlink to pg_config binary, replace PG_VERSION with the actual postgres version.

    $ ln -s /Applications/Postgres.app/Contents/Versions/PG_VERSION/bin/pg_config .venv/bin

Then install all required packages (execute this command in the activated 
environment and from project directory):

    $ python3.4 setup.py develop

Copy configuration script `development.ini` from the directory `examples` to the same directory 
where `setup.py` is located, edit `development.ini` appropriately, but default preferences are 
just fine. By default pyrone development config uses sqlite database
engine.

See also `INSTALL.md` for database setup instruction.


Preparing virtual environment (debian/ubuntu)
---------------------------------------------

It's assumed here and later that you're using Debian/Ubuntu linux distribution. So open
terminal now and proceed.

First you need to install `python` (version 3.3 or greater), you'll also
need python package `virtualenv`, you can install them using following command:

    # apt-get install python3.4 python3.4-venv python3.4-dev postgresql-9.4 

Also you'll need to install additional binary packages:

    # apt-get install curl gcc libxml2-dev libxslt1-dev libjpeg62-turbo-dev libfreetype6-dev zlib1g-dev libpq-dev
    
Now we are going to set up development virtual environment in the project directory:

    $ pyvenv-3.4 --without-pip .venv

You now have the directory with new virtual environment, now you should *activate* it, after 
activation all required commands will be executed from your virtual environment, not from the
system. Required commands are: `python`, `pip`, `easy_install` etc. So activate (remember,
we are in the project directory):

    $ source .venv/bin/activate

Install setuptools and pip:

    $ curl https://bootstrap.pypa.io/ez_setup.py | python3.4 -
    $ rm setuptools-*.zip
    $ easy_install-3.4 pip

Make sure that important commands are resolved correctly, if you are using zsh 
execute command `rehash`:

    $ which easy_install-3.4
    /home/user/projects/pyrone/.venv/bin/easy_install-3.4
    $ which python3.4
    /home/user/projects/pyrone/.venv/bin/python3.4

And install now all required python packages (execute this command in the activated 
environment and from project directory):

    $ python3.4 setup.py develop

Also you need to install mysql-connector-python manually (there is not appropriate version
on pypi site yet). Follow instructions on this page: <http://dev.mysql.com/doc/connector-python/en/connector-python-installation-source.html>.

Copy configuration script `development.ini` from the directory `examples` to the same directory 
where `setup.py` is located, edit `development.ini` appropriately, but default preferences are 
just fine. By default pyrone development config uses sqlite database
engine.

See also `INSTALL.md` for database setup instruction.

Working with development server
-------------------------------

To start development server use the following command:

    $ pserve --reload development.ini

On first run or after database destroy you need to initialize database:

    $ pyronedbinit development.ini --sample-data


Localization and internationalization
-------------------------------------

Pyrone uses `Babel` package to maintain `gettext`-translation file. Here are the most used
commands.

Collect messages from source files (python only):

    $ python3.4 setup.py extract_messages extract_messages_js

Update messages (using .pot-file created by `extract_messages` command):

    $ python3.4 setup.py update_catalog update_catalog_js

Or collect and update in one step:

    $ python setup.py extract_messages update_catalog extract_messages_js update_catalog_js

Compile translation files (for python code):

    $ python3.4 setup.py compile_catalog compile_catalog_js

Start new language ("es", Spanish in this example, both for python and javascript code, do this ONCE for one language):

    $ python3.4 setup.py init_catalog -l es
    $ python3.4 setup.py init_catalog_js -l es


Code syntax highlight in the articles
-------------------------------------

Pyrone uses Markdown extension `codehilite` and to work properly it requires corresponding
css, currently it's commited as part of each style (in the file `blog.css`), and this css code
is generated by the following python code:

    from pygments.formatters import HtmlFormatter
    print(HtmlFormatter().get_style_defs('.codehilite'))


Release and packaging
---------------------

You MUST use activated environment for commands below! So first execute:

    $ source .venv/bin/activate

Prepare and upload source package to pypi:

    $ python3.4 setup.py clean compile_catalog compile_catalog_js sdist upload

Alternatively you could use the following command, it will ask you for password:

    $ python3.4 setup.py clean sdist upload

If you want to create source distribution package only (file `pyrone-1.4.0.tar.gz`), use 
the following command:

    $ python3.4 setup.py clean compile_catalog compile_catalog_js sdist


Some additional notes
=====================

Do not use sqlite even for development! Use postgresql only.

Use this command to connect postgres database:

    $ psql -h localhost pyrone_blog pyrone_blog_user