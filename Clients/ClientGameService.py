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
        print(argv[1])
        proxy = self.communicator().stringToProxy(argv[1])
        self.room = IceGauntlet.RoomPrx.checkedCast(proxy)
        if not self.room:
            raise RuntimeError('Invalid proxy')
        
        roomData=self.room.getRoom()
        roomDataJson = json.load(roomData)
        archivo = open("iceguantlet/assets/"+str(roomDataJson['room']),"w")
        archivo.write(roomData)
        archivo.close()
        
        return 0
        
sys.exit(Client().main(sys.argv))