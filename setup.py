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
    'Babel'
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='pyrone',
      version='0.1',
      description='pyrone',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Sergei Stolyarov',
      author_email='sergei.stolyarov@regolit.com',
      url='https://bitbucket.org/cancel/pyrone',
      data_files=[
        ('share/pyrone/sample-config', ['production.ini', 'supervisord.conf'])
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
      paster_plugins=['pyramid'],
      )

