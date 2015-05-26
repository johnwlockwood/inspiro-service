# inspiro-service

## Define database password

`echo "MYSQL_ROOT_PASSWORD=mysecretpassword" > pypy2test/.env`

## Initialize the database containers

`docker-compose -f pypy2test/db_dev.yml up -d`

## Start up service

`docker-compose -f pypy2test/development.yml up`

