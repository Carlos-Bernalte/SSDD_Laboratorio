#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    
    def publishMap(self, token="", map_name=""):

        try:
            new_room=open("icegauntlet/editor/maps/"+map_name, "r")
            self.room.publish(token,new_room.read())
            new_room.close()
            
        except FileNotFoundError:
            print("Archivo no encontrado en el directo")

        

    def removeMap(self, token="", map_name=""):   
        self.room.remove(token,map_name)

    def run(self, argv):
        server_proxy=""
        try:
            with open("proxys/ProxyRM.out") as proxyString:
                server_proxy=proxyString.read()
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")

        proxy = self.communicator().stringToProxy(server_proxy)
        self.room = IceGauntlet.RoomManagerPrx.checkedCast(proxy)
        if not self.room:
            raise RuntimeError('Invalid proxy')

        if len(argv) == 4:
            if argv[1]=="-p":
                self.publishMap(argv[2],argv[3])
            elif argv[1]=="-r":
                self.removeMap(argv[2],argv[3])
            else:
                print("Opción no disponible.")
                return 1
        
        return 0
        

        
sys.exit(Client().main(sys.argv))