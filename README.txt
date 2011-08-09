Required packages
=================

The following packages are required, install the using ``easy_install``:

    pyramid SQLAlchemy markdown pytz hurry.filesize tweepy
    
The following packages are required for development:

    nose coverage
    
Development
===========

Virtual environment
-------------------

It's strongly recommended to use virtual python environment with locally 
installed ``pyramid`` and other required packages. Further in this README.txt
it's assumed that ``python`` binary is located in your virtual environment.
The same thing for ``easy_install`` executable.

To make your life easy use script ``bin/activate`` from virtual environment to 
update local environment variables (``PATH`` etc), in that case you can run executables
like ``python`` and ``easy_install`` without using full paths to them.

Tests and coverage
------------------

Running the tests:

    python setup.py test -q
    
Collecting coverage information:

    nosetests --cover-package=pyrone --cover-erase --with-coverage
    
Running application
-------------------

To start development server use the following command:

    paster serve --reload development.ini
    