all:
	$(MAKE) run_auth_server
	sleep 2
	$(MAKE) run_map_server

run_auth_server:
	gnome-terminal -- bash -c \
	"echo "Ejecutando Servidor de autentificación en local..."; bash"
	#./Servers/auth_server --Ice.Config=Servers/auth_server.conf | tee proxys/auth_server-proxy.out

run_map_server:
	gnome-terminal -- bash -c \
	"echo "Ejecutando Servidor de mapas..."; bash"
	#python3 Servers/server.py --Ice.Config=Servers/server.conf "$1"
hola:
	echo "Esta mierda funciona?"