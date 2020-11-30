#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import Ice
import json
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):

    def run(self, argv):
        server_proxy=None
        try:
            server_proxy=open("proxys/ProxyGS.out", "r")
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")
        prox=server_proxy.read()
        print(prox)
        proxy = self.communicator().stringToProxy(prox)
        
        self.room = IceGauntlet.RoomPrx.checkedCast(proxy)
        print(">>> "+str(self.room))
        if not self.room:
            raise RuntimeError('Invalid proxy')
        
        roomData=self.room.getRoom()
        roomDataJson = json.load(roomData)
        archivo = open("iceguantlet/assets/"+str(roomDataJson['room']),"w")
        archivo.write(roomData)
        archivo.close()
        
        return 0
        
sys.exit(Client().main(sys.argv))