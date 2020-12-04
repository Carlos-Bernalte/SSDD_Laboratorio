#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import Ice
import json
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    """
    def __init__(self):
        server_proxy=""
        try:
            with open("proxys/ProxyGS.out") as proxyString:
                server_proxy=proxyString.read()
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")

        proxy = self.communicator().stringToProxy(server_proxy)
        print(">>>: "+str(proxy))
        self.game = IceGauntlet.DungeonPrx.checkedCast(proxy)
        if not self.game:
            raise RuntimeError('Invalid proxy')
        
        roomData=self.game.getRoom()
        archivo = open("icegauntlet/assets/map","w")
        archivo.write(roomData)
        archivo.close()
        """
    def run(self, argv):
        server_proxy=""
        try:
            with open("proxys/ProxyDungeon.out") as proxyString:
                server_proxy=proxyString.read()
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")
        proxy = self.communicator().stringToProxy(server_proxy)
        print(">>>: "+str(proxy))
        self.game = IceGauntlet.DungeonPrx.checkedCast(proxy)
        if not self.game:
            raise RuntimeError('Invalid proxy')

        roomData=self.game.getRoom()
        archivo = open("icegauntlet/assets/map.json","w")
        archivo.write(roomData)
        archivo.close()
        
        return 0
        
sys.exit(Client().main(sys.argv))
    