#Makefile para el trabajo de SSDD

run-auth_server:
	./icegauntlet_auth_server/auth_server --Ice.Config=icegauntlet_auth_server/auth_server.conf | tee auth_server-proxy.out

run-server:
	python3 Server.py --Ice.Config=Server.config "$(shell head -1 auth_server-proxy.out)"| tee server-proxy.out

run-client:
	python3 Client.py "$(shell cat server-proxy.out)"
 prueba:
	$(shell head -1 server-proxy.out)

