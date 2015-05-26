import os


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

