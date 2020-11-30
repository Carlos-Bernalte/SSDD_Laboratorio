#Makefile para el trabajo de SSDD

run-auth_server:
	./icegauntlet_auth_server/auth_server --Ice.Config=icegauntlet_auth_server/auth_server.conf | tee auth_server-proxy.out

run-server:
	python3 Servers/Server.py --Ice.Config=Server.config "$(shell head -1 Servers/auth_server-proxy.out)"| tee server-proxy.out

run-client:
	python3 Clients/Client.py "$(shell cat Servers/server-proxy.out)"

 prueba:
	$(shell head -1 Servers/server-proxy.out)

