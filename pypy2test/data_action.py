# _*_ coding: utf-8 _*_
from twisted.internet import defer
from twisted.python import log

from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import Index
from sqlalchemy import text
from sqlalchemy import PassiveDefault
from sqlalchemy import Numeric
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import text
from sqlalchemy import DateTime
from sqlalchemy import MetaData
from sqlalchemy.exc import OperationalError
from sqlalchemy.schema import CreateTable
from sqlalchemy import select

from sqlalchemy.dialects.mysql import TIMESTAMP


metadata = MetaData()


@defer.inlineCallbacks
def setup_tables(reactor, db_engine):
    """
    Create table.

    :return:
    """
    try:
        yield db_engine.execute(CreateTable(bogus_table))
        log.msg("bogus created")
    except OperationalError:
        log.msg("bogus in table exists already")


@defer.inlineCallbacks
def add_fixtures(reactor, db_engine):
    rows = [
        {
            bogus_table.c.name.name: "Hal",
            bogus_table.c.one.name: 4,
        }, {
            bogus_table.c.name.name: "Petra",
            bogus_table.c.one.name: 8,
        },
    ]
    ins = bogus_table.insert()
    yield db_engine.execute(ins, rows)


@defer.inlineCallbacks
def get_data(reactor, db_engine):
    result = yield db_engine.execute(select(bogus_table.c))
    items = yield result.fetchall()
    for item in items:
        log.msg("bogus item: %s" % item.name)
        yield


bogus_table = Table(
    'bogus', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100)),
    Column('one', Integer),
    Column('created', TIMESTAMP),
    Column(
        'modified',
        TIMESTAMP,
        PassiveDefault(text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))),
)
