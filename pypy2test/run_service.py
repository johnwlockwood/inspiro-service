#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from twisted.web import server
from twisted.internet import reactor
from twisted.python import log

from build_service import get_main_resource


def main(*args):
    log.startLogging(sys.stdout)

    resource = get_main_resource()

    resource.start()

    reactor.listenTCP(5000, server.Site(resource))
    reactor.run()
    return resource

if __name__ == '__main__':
    resource = main()
