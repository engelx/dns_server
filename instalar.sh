apt-get update
apt-get install postgresql libpq-dev postgresql-client postgresql-client-common python3 python3-psycopg2 
mkdir /etc/miniDNS
cp *.py /etc/miniDNS
cp servers.conf /etc/miniDNS
psql -U postgres < base.sql
cp miniDNS /etc/init.d/
update-rc.d miniDNS defaults
service miniDNS start