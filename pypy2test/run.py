#!/usr/bin/env python
# _*_ coding: utf-8 _*_
from operator import add

import sys
import os
from twisted.internet import defer
from twisted.internet.task import react
from twisted.python import log

import sqlalchemy
from alchimia import TWISTED_STRATEGY

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

from cooperative import batch_accumulate

metadata = MetaData()


@defer.inlineCallbacks
def add_main_fixture(reactor, db_engine):
    """
    Create table.

    :return:
    """
    try:
        yield db_engine.execute(CreateTable(bogus_table))
        log.msg("bogus created")
    except OperationalError, e:
        log.msg("bogus in table exists already")
    rows = [
        {
            bogus_table.c.name.name: "Hal",
            bogus_table.c.one.name: 4,
        }, {
            bogus_table.c.name.name: "Petra",
            bogus_table.c.one.name: 8,
        },
    ]
    d5 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.5, d5.callback,
                      "########## simulated request 98 ############")
    yield d5
    ins = bogus_table.insert()
    yield db_engine.execute(ins, rows)

    result = yield db_engine.execute(select(bogus_table.c))
    items = yield result.fetchall()
    for item in items:
        print item
        log.msg("bogus item: %s" % item.name)
        yield


def get_mysql_connection_string(
        username="root",
        password=os.environ['MYSQL_ENV_MYSQL_ROOT_PASSWORD'],
        server=os.environ['MYSQL_PORT_3306_TCP_ADDR'],
        port=int(os.environ['MYSQL_PORT_3306_TCP_PORT']),
        database="mytestdb"):
    """
    Make connection string for pymssql.

    :param username:
    :param password:
    :param server:
    :param port:
    :param database:
    :return:
    """
    connection_string = 'mysql://%s:%s@%s:%s/%s' % (
        username,
        password,
        server,
        port,
        database
    )
    return connection_string

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


def expensive(number):
    log.msg("starting {}".format(number))
    for value in range(100000):
        if 25000 == value:
            log.msg("1/4 for {}".format(number))
        if 50000 == value:
            log.msg("1/2 for {}".format(number))
        if 75000 == value:
            log.msg("3/4 for {}".format(number))
        yield number * value / 3.0


def expensive2(number):
    log.msg("starting {}".format(number))
    total = 0
    for value in range(100000):
        if 25000 == value:
            log.msg("1/4 for {}".format(number))
        if 50000 == value:
            log.msg("1/2 for {}".format(number))
        if 75000 == value:
            log.msg("3/4 for {}".format(number))
        total += number * value / 3.0
        yield
    yield total


@defer.inlineCallbacks
def do_some_expensive_things(number):
    """
    Perform one expensive computation cooperatively with any
     other iterator passed into twisted's cooperate, then
     use it's result to pass into the second computation.

    :param number:
    :return:
    """
    result = yield batch_accumulate(1000, expensive(number))
    total = reduce(add, result, 0)
    log.msg("first for {}: {}".format(number, total))

    result = yield batch_accumulate(1000, expensive2(int(total / 1e9)))
    total = reduce(add, result, 0)
    log.msg("second for {}: {}".format(number, total))
    defer.returnValue(total)


@defer.inlineCallbacks
def do_less_expensive_things(number):
    """
    Perform one expensive computation cooperatively with any
     other iterator passed into twisted's cooperate, then
     use it's result to pass into the second computation.

    :param number:
    :return:
    """
    result = yield batch_accumulate(1000, expensive(number))
    total = reduce(add, result, 0)
    log.msg("only for {}: {}".format(number, total))
    defer.returnValue(total)


@defer.inlineCallbacks
def try_db(reactor, db_engine):
    yield add_main_fixture(reactor, db_engine)


def main(reactor):
    db_engine = sqlalchemy.create_engine(
        get_mysql_connection_string(),
        strategy=TWISTED_STRATEGY,
        reactor=reactor,
        pool_timeout=5)
    db1 = try_db(reactor, db_engine)

    d1 = do_some_expensive_things(54.0)
    d2 = do_some_expensive_things(42)
    d3 = do_some_expensive_things(10)
    d4 = do_some_expensive_things(34)

    # Enqueue events to simulate handling external events
    d5 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.3, d5.callback,
                      "########## simulated request 1 ############")

    d6 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(0.5, d6.callback,
                      "########## sim request 2 ############")

    d7 = defer.Deferred().addCallback(log.msg)
    reactor.callLater(1.0, d7.callback,
                      "########## simulated request 3 ############")

    # simulate an external event triggering an expensive computation while
    # other expensive computations are happening.
    d8 = defer.Deferred()
    d8.addCallback(do_less_expensive_things)
    reactor.callLater(0.3, d8.callback, 20001)

    return defer.gatherResults([
        db1, d1, d2, d3, d4, d5, d6, d7, d8]).addCallback(log.msg)

if __name__ == "__main__":
    log.startLogging(sys.stdout)
    react(main, [])
