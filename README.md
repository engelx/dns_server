# Mini servidor dns

Este es un servidor dns que puede ser usado a nivel de empresas e instituciones para crear dominios internos para los servicios, bloquear accesos a sitios que se deseen restringir y servir como caché para disminuir la carga de la red 

Funciona en python3 y postgres, que facilmente pueden ser integrados en cualquier sevidor linux

Depende de las siguiente librerías
* postgresql 
* libpq-dev 
* postgresql-client 
* postgresql-client-common 
* python3 
* python3-psycopg2

Para instalarlo en servidores Debian-like solo es necesario clonar el repositorio, entrar a la carpeta descargada y ejecutar **./instalar.sh**. El script creará la carpeta del sistema en /etc/minidns, instalará el servicio en init.d y creará el ROLE y DB en postgres para su uso. Así mismo se encuentra ./uninstall.sh que eliminará todo (solo dejando atrás lo instalado por aptitude)

La configuración se divide en 5 secciones 

## blocked
En esta sección se manipulan los hosts a bloquear, 

* ./configure.py blocked add {host} {category}
Agrega un host a bloquear

* ./configure.py blocked rem host {host}
Elimina todos los host de una categoría

* ./configure.py blocked rem cat {category}
Elimina un host bloqueado

* ./configure.py blocked check [category] 
Muestra toda la información sobre los host bloqueados, si no se usa una categoría se imprimirá todo

## user
En esta sección se manipulan los usuarios con excepciones de bloqueo

* ./configure.py user add {username} {group} {ip}  
Agrega un usuario

* ./configure.py user rem user {username}
Elimina un usuario

* ./configure.py user rem group {group}
Elimina todos los usuarios de un grupo y el grupo

* ./configure.py user check [group]
Imprime en un archivo toda la información sobre los usuarios, si grupo no es usado, se mostrarán todos

