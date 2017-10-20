# Servidor DNS minidns

para instalar ejecutar (como root)
./instalar

este se instalará como un servicio llamado minidns
por defecto se iniciar con el sistema 

para iniciar manualmente (como root)
service minidns start

para detener 
service minidns stop

si se quieren configurar más servidores se pueden agregar a server.conf (experimental)

para configurar el servidor ejecutar 
etc/minidns/configure.py

si no se pasan parametros, mostrará toda la ayuda
