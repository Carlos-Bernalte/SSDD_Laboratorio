#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import os
import Ice
import json
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    
    def publishMap(self, token="", map_name=""):

        try:
            new_room=open("iceguantlet/assets/"+map_name, "r")
            self.room.publish(token,new_room.read())
            new_room.close()
            
        except FileNotFoundError:
            print("Archivo no encontrado en el directo")

        

    def removeMap(self, token="", map_name=""):

        room_name=input("Escribe el nombre del mapa que desees eliminar: ")        
        self.room.remove(token,room_name)

    def run(self, argv):
        if len(argv) == 4:
            if argv[2]=="-p":
                self.publish(argv[3],argv[4])
            elif argv[2]=="-r":
                self.removeMap(argv[3],argv[4])
            else:
                print("Opción no disponible.")
                return 1
        
        print(argv[1])
        proxy = self.communicator().stringToProxy(argv[1])
        self.room = IceGauntlet.RoomPrx.checkedCast(proxy)
        if not self.room:
            raise RuntimeError('Invalid proxy')

        return 0
        

        
sys.exit(Client().main(sys.argv))