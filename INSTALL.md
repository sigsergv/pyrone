Installation in production mode
===============================


Foreword
--------

This document describes how to install Pyrone in the production environment.

Pyrone is a standard WSGI application so you can use any method for provisioning WSGI 
apps. However in this instruction only one method is covered: Debian/Ubuntu + nginx + 
uwsgi + postgresql. Application requires Python version 3.5 or 3.6. Python 2 is not supported.

I recommend you (for security reasons) to create separate system user for the application. In this
manual all instructions assume there is a system user `blog` with home directory `/home/blog`, 
it's a regular non-privileged user.

All linux shell commands in this manual have prefixes, if prefix is `$` then command must be executed
using user `blog` shell session, and commands with the prefix `#` must be executed in root shell session.

This instruction is written for Debian 9 "Stretch", python 3.5 and postgresql 9.6.


Postgresql setup
----------------

Install Postgresql:

    # apt-get install postgresql

Now create database and database user for Pyrone, use the following commands from your shell:

    # sudo -u postgres createdb pyrone_blog
    # sudo -u postgres createuser pyrone_blog_user -P

Choose and enter password.

You can also update files `/etc/postgresql/9.6/main/pg_hba.conf` and
`/etc/postgresql/9.6/main/postgresql.conf` if you want to set special permissions for that user.

Prepare virtual environment
---------------------------

We use pyvenv to install Pyrone runtime.

You need to prepare directory where your application should be installed, e.g.: 
`/home/blog/pyrone-blog`.

Inside this directory you need to create virtual environment, application directory, configuration
files, so let's begin.

First install package `python-virtualenv` and other required packages:

    # apt-get update
    # apt-get install dh-exec python3 python3-venv dpkg-dev python3-dev gcc libxml2-dev libxslt1-dev libjpeg62-turbo-dev libfreetype6-dev zlib1g-dev libpq-dev

Login as a `blog` user:

    # sudo -u blog -i

Then initialize new virtual environment:

    $ mkdir /home/blog/pyrone-blog/
    $ python3 -m venv /home/blog/pyrone-blog/env

Now you have to *activate* just installed environment:

    $ source /home/blog/pyrone-blog/env/bin/activate

That command modifies your shell session and almost all python-related command are now
executed in just created virtual environment. And you are *required* to stay in this session
to execute all remaining commands!

You need to install some additional packages first:

    $ pip3 install wheel

Now install Pyrone from python packages repository:

    $ pip3 install pyrone

This will install latest stable version of Pyrone and all needed packages.

Alternatively you can install it from local package file (it will automatically install 
all dependencies too):

    $ pip3 install pyrone-1.4.5.tar.gz

Now prepare the application configuration files:

   $ cd /home/blog/pyrone-blog/
   $ cp ./env/share/pyrone/examples/production.ini .

Open file `production.ini` in any text editor and change default database connection
parameters to yours. If you've followed this instruction from the beginning you'll need to change
database password only: find the string `pbpass` and replace it with the actual password.

Now we need to setup the database, to do this execute the following command:

    $ cd /home/blog/pyrone-blog
    $ pyronedbinit --sample-data --sample-data-file=./env/share/pyrone/sample-data.json production.ini

Check that application is configured properly, to do that just execute the following command inside
the directory `/home/blog/pyrone-blog`:

    $ /home/blog/pyrone-blog/env/bin/pserve production.ini

If configuration steps were performed correctly you should see something like this:

    Starting server in PID 5712.
    serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

Now press Ctrl+C to terminate server.

Congratulation! You've just installed pyrone application server, so you can proceed to next steps: 
installing/configuring web server (nginx) and installing/configuring middle layer between Pyrone 
runtime and web server (uWSGI).


Installing and configuring uWSGI
--------------------------------

Install required OS packages:

    # apt-get install uwsgi uwsgi-plugin-python3

Then create configuration file for the application:

    # cp /home/blog/pyrone-blog/env/share/pyrone/examples/pyrone-uwsgi.ini /etc/uwsgi/apps-available/
    # ln -s /etc/uwsgi/apps-available/pyrone-uwsgi.ini /etc/uwsgi/apps-enabled

And restart uWSGI:

    # service uwsgi restart

Error log for the application: /var/log/uwsgi/app/pyrone-uwsgi.log


Installing and configuring nginx
--------------------------------

Install nginx:

    # apt-get install nginx

Then create nginx configuration file for Pyrone's site:

    # cp /home/blog/pyrone-blog/env/lib/python3.5/site-packages/pyrone-1.4.5-py3.5.egg/share/pyrone/examples/pyrone-blog-nginx-uwsgi.conf /etc/nginx/sites-available/

In this file you need to change hostname (default value is `blog.example.com`).

After that create symlink to enable nginx site and restart it:

    # ln -s /etc/nginx/sites-available/pyrone-blog-nginx-uwsgi.conf /etc/nginx/sites-enabled/
    # service nginx restart

If you want to serve HTTPS requests too you need to copy another sample file: 
`/home/blog/pyrone-blog/env/share/pyrone/examples/pyrone-blog-nginx-uwsgi-ssl.conf`, in that case you must
create proper ssl certificates and other related stuff I don't describe here.

That's all! Open your site in the browser and enjoy blogging. Default local login credentials (username/password): `admin/setup`,
don't forget to change password.


Some post-install stuff
=======================


Default login/password
----------------------

Default administrator login is `admin` and password is `setup`.


Site icons (favicons)
---------------------

Pyrone package doesn't contain site icons, so you have to configure them separately. By default
pyrone looks for files `favicon.png` and `favicon.ico` in the same directory where
your production.ini file is placed. But you can change paths manually, just open file `production.ini`
in the text editor, then find keys `pyrone.favicon_ico` and `pyrone.favicon_png` (in 
the section `[app:pyrone]`), and change values from default to actual paths to these icons.


Backup and restore
------------------

For security reasons you cannot upload backup files using web interface. You must upload it into special
directory using scp or ssh. This special directory is `/home/blog/pyrone-blog/storage/backups`.

After that you can restore backup using admin web-interface.


Serving static files
--------------------

By default Pyrone handles static files (scrits, styles etc) by itself, if you want to pass static files processing
to nginx (much more effective way) you should edit nginx site configuration file 
and uncomment static files section.


Sample configuration files
--------------------------

You will find up-to-date samples of various configuration files in the directory `examples` (in the source tree)
or in the directory `/home/blog/pyrone-blog/env/share/pyrone/examples` (on production server after Pyrone install).


Feedback and support
--------------------

Main project hosting site is https://github.com/sigsergv/pyrone , feel free to leave comments, feedback
and issues there.


Upgrade
=======

Backup, uninstall old version, install new version, restore.
