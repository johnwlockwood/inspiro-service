# inspiro-service

## Define database password

`echo "MYSQL_ROOT_PASSWORD=mysecretpassword" > pypy2test/.env`

## Initialize the database containers

`docker-compose -f pypy2test/compose-db-only.yml up -d`

## Start up service

`docker-compose -f pypy2test/compose-app-ext.yml up`

