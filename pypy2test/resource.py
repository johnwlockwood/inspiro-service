# -*- coding: utf-8 -*-
from twisted.internet.task import LoopingCall
from twisted.web.resource import Resource
from twisted.internet import defer
from twisted.python import log
from twisted.web.server import NOT_DONE_YET

from async_utils import AsyncJSON

from data_action import setup_tables
from data_action import add_fixtures


class MainResource(object, Resource):
    interval = 60
    call_count = 0

    def __init__(self, own_reactor, cooperator, db_engine):
        """
        Set reactor and database engines.

        :param own_reactor: A Reactor.
        :param cooperator: A Cooperator instance or None to use the
         global instance.
        :param db_engine: A sqlAlchemy engine

        """
        self.children = {}

        self.reactor = own_reactor
        self.cooperator = cooperator
        self.db_engine = db_engine
        self.tables_setup = False

        # goals
        self.ticks_active = 0
        self.tick_loop = LoopingCall(self.tick)
        self.tick_loop.clock = self.reactor

    @defer.inlineCallbacks
    def tick(self, ignore=None):
        """
        tick

        :param ignore: An ignored argument to allow to work as a callback.
        """
        if not self.tables_setup:
            yield setup_tables(self.reactor, self.db_engine)
            self.tables_setup = True
        yield add_fixtures(self.reactor, self.db_engine)

        self.call_count += 1
        yield

    def stop(self):
        """
        Stop this miner from incrementing anymore.

        """
        if self.tick_loop.running:
            self.tick_loop.stop()

        if self.ticks_active:
            self.ticks_active -= 1

    def start(self):
        """
        Start this miner incrementing on an interval.

        """
        self.tick_loop.start(self.interval, now=True)

        log.msg("Start Ticks")
        if not self.ticks_active:
            self.ticks_active += 1

    def getChild(self, name, request):
        if name in ['', 'm']:
            return self
        return Resource.getChild(self, name, request)

    @defer.inlineCallbacks
    def do_get(self, request):

        data = [1, 2, 3, 4, self.call_count]
        try:
            yield AsyncJSON(data, self.cooperator).begin_producing(request)
        except ValueError:
            request.write("ERROR")

        request.write("\n")
        request.finish()

    def render_GET(self, request):
        """
        Handle web requests for this resource.
        If the first path element is in or out, respond
        asynchronously.

        """
        request.setHeader("content-type", "application/json")

        self.do_get(request)
        return NOT_DONE_YET
