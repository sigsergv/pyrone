"""Script for database initialization"""

import argparse
import os
import json
import codecs
from sys import exit
import re

from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy import engine_from_config
#from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
import transaction
from sqlalchemy import engine_from_config

from ..models import Base, DBSession, initialize_sql
from ..models import (
    User,
    Role,
    VerifiedEmail,
    Config,
    Article,
    Comment,
    Tag,
    File
)


class Data:
    def __init__(self, dbsession):
        self.dbsession = dbsession

    def flush(self):
        self.dbsession.flush()

    def init_config(self, data):
        for r in data:
            config = self.dbsession.query(Config).get(r[0])
            if config is None:
                config = Config(id=r[0], value=r[1])
                self.dbsession.add(config)

    def init_user(self, data):
        for r in data:
            user = self.dbsession.query(User).get(r[0])
            if user is None:
                user = User(id=r[0], login=r[1], password=r[2], display_name=r[3], email=r[4],
                    kind=r[5])
                self.dbsession.add(user)

            for p in r[6]:
                role = self.dbsession.query(Role).filter(Role.user_id==r[0], Role.name==p).first()
                if role is None:
                    role = Role(id=None, user_id=r[0], name=p)
                    self.dbsession.add(role)


def main():
    parser = argparse.ArgumentParser(description='Initialize pyrone database')
    parser.add_argument('config_ini', metavar='<config.ini>',
        help='Project config file (e.g. development.ini)')
    parser.add_argument('--sample-data', dest='sample_data',
        default=False, action='store_true',
        help='Also populate database with the sample data')
    parser.add_argument('--sample-data-file', dest='sample_data_file',
        default='sample-data.json',
        help='JSON file with the sample data')
    args = parser.parse_args()

    print(args)

    ini_path = os.path.realpath(args.config_ini)
    if not os.path.isfile(ini_path):
        print('Config file `{0}` not found!'.format(args.config_ini))
        exit(1)

    print('Initialize database')
    # initialize db engine
    setup_logging(ini_path)
    settings = get_appsettings(ini_path)
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    dbsession = DBSession()
    dh = Data(dbsession)

    # create tables
    Base.metadata.create_all(engine)
    if args.sample_data:
        # import sample data from json file
        raw = codecs.open(args.sample_data_file, encoding='utf-8').read()
        raw = re.sub('^\s*//.+\n', '', raw, flags=re.MULTILINE)
        #raw = re.sub('//.*$', '', raw, flags=re.MULTILINE)
        sample_data = json.loads(raw, encoding='utf-8')

        dh.init_config(sample_data['config'])
        dh.init_user(sample_data['user'])
        dh.flush()

        transaction.commit()


if __name__ == '__main__':
    main()


