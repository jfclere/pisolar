install grafana:
```
yum install grafana
```
start it:
```
sudo systemctl start grafana-server.service
```
test it:
```
http://localhost:3000/login admin/admin
```
install postgres:
```
yum install postgres
```
start it:
```
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl start postgresql.service
```
Add data sources / postgreSQL
1 - user postgres for granafa
```
sudo su - postgres
createuser grafana
```
2 -database bme280
In psql:
```
CREATE USER jfclere;
CREATE DATABASE bme280 OWNER jfclere;
```
In psql -d bme280 (still as postgres create the table measurements too!):
```
CREATE ROLE  grafana;
GRANT CONNECT ON DATABASE bme280 to grafana;
GRANT USAGE ON SCHEMA public TO grafana;
GRANT SELECT ON TABLE measurements to grafana;
ALTER USER  grafana  WITH PASSWORD 'the_password_word';
```
make sure to have in /var/lib/pgsql/data/pg_hba.conf:
```
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```
create a dash board with the information you want to display.

create a user with viewer permission and use this one for demos.

use https in grafana: /etc/grafana/grafana.ini

may be anonymous access:
```
[auth.anonymous]
enabled = true
...
```
