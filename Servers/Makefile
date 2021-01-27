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
	cp icegauntlet.ice server.py /tmp/icegauntlet
	icepatch2calc /tmp/icegauntlet

/tmp/%:
	mkdir -p $@