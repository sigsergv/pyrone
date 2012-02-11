import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    # binary packages require some additional packages installed on your system like gcc
    'PIL',
    'lxml',
    'pyramid',
    'pyramid_beaker',
    'pytz',
    'tweepy',
    'markdown',
    'decorator',
    'hurry.filesize',
    'TurboMail',
    'SQLAlchemy',
    'PyMySQL',
    'transaction',
    'repoze.tm2>=1.0b1', # default_commit_veto
    'zope.sqlalchemy',
    'WebError',
    'WebHelpers',
    'Babel'
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup_cmdclass = {}

try:
    import babel
    from setupcommands import ExtractMessagesJs, CompileCatalogJs
    from babel.messages.frontend import init_catalog as babel_init_catalog, update_catalog as babel_update_catalog
    setup_cmdclass = {
        'extract_messages_js': ExtractMessagesJs,
        'init_catalog_js': babel_init_catalog,
        'update_catalog_js': babel_update_catalog,
        'compile_catalog_js': CompileCatalogJs
    }
except ImportError:
    pass

setup(name='pyrone',
      version='0.2.8',
      license='New BSD License',
      description='pyrone',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pylons",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
        ],
      author='Sergei Stolyarov',
      author_email='sergei.stolyarov@regolit.com',
      url='https://bitbucket.org/cancel/pyrone',
      data_files=[
        ('share/pyrone/sample-config', ['production.ini', 'supervisord.conf', 
            'pyrone-blog-nginx.conf', 'supervisord-pyrone', 'uwsgi-pyrone',
            'pyrone-blog-nginx-uwsgi.conf'])
      ],
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyrone',
      install_requires = requires,
      message_extractors = {'pyrone': [
        ('**.py', 'python', None),
        ('templates/**.mako', 'mako', {'input_encoding': 'utf-8'})
        ]},
      entry_points = """\
      [paste.app_factory]
      main = pyrone:main
      """,
      cmdclass = setup_cmdclass,
      paster_plugins=['pyramid'],
      )

