#!/usr/bin/make -f
# -*- mode:makefile -*-

all:

clean:
	$(RM) -r /tmp/db
	$(RM) -r /tmp/icegauntlet

run: app-workspace
	$(MAKE) run-node1 &
	sleep 1
	$(MAKE) run-node2

run-node1: /tmp/db/registry /tmp/db/node1/servers 
	icegridnode --Ice.Config=node1.config

run-node2: /tmp/db/node2/servers
	icegridnode --Ice.Config=node2.config

#run-client:
	#./Client.py --Ice.Config=locator.config "printer1 -t -e 1.1 @ PrinterServer$(SERVER).PrinterAdapter"

app-workspace: /tmp/icegauntlet
	cp server.py /tmp/icegauntlet
	cp server.conf /tmp/icegauntlet
	cp auth_server /tmp/icegauntlet
	cp auth_server.conf /tmp/icegauntlet
	cp reload_users /tmp/icegauntlet
	cp users.json /tmp/icegauntlet
	cp auth_server /tmp/icegauntlet
	cp -r server_maps /tmp/icegauntlet
	cp data.json /tmp/icegauntlet
	cp icegauntlet.ice /tmp/icegauntlet

	icepatch2calc /tmp/icegauntlet

/tmp/%:
	mkdir -p $@