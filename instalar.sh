#!/bin/bash
set -e
echo "Instalando archivos necesarios"
#apt-get update
#apt-get install postgresql libpq-dev postgresql-client postgresql-client-common python3 python3-psycopg2 -y

echo "instalando archivos en /etc/minidns"
mkdir /etc/minidns || true
cp configure.py /etc/minidns
cp handler_db.py /etc/minidns
cp handler_db_pg.py /etc/minidns
cp handler_dns_query.py /etc/minidns
cp server.py /etc/minidns/minidns
cp servers.conf /etc/minidns
chmod 755 . -R
chmod 700 *
chmod 755 configure.py
chmod 644 servers.conf

echo "Cargando base de datos"
psql -U postgres < base.sql

echo "Instalando servicio"
cp script_init /etc/init.d/minidns
update-rc.d -f minidns defaults
service minidns start

echo "Probando instalación"
service=minidns

service minidns status

if (( $(ps -ef | grep -v grep | grep $service | wc -l) > 0 ))
then
echo "Instalado correctamente y ejecutandose"
else
echo "No se está ejecutando"
fi
