# -*- coding: utf-8 -*-
import sqlalchemy
from alchimia import TWISTED_STRATEGY
from twisted.internet import reactor

from db_connection import get_mysql_connection_string
from resource import MainResource


def get_main_resource():
    """
    Create the index miner for Prairie Knights.

    :return: An IndexMiner.
    """

    db_engine = sqlalchemy.create_engine(
        get_mysql_connection_string(),
        strategy=TWISTED_STRATEGY,
        reactor=reactor,
        pool_timeout=5)

    main_resource = MainResource(
        reactor,
        cooperator=None,
        db_engine=db_engine)

    return main_resource
