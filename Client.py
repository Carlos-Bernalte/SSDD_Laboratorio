#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('Slice.ice')
import IceGauntlet

class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        print(argv[1])
        room = IceGauntlet.RoomPrx.checkedCast(proxy)

        if not room:
            raise RuntimeError('Invalid proxy')
        
        level=room.getRoom()
        archivo = open('client_maps/mapa_descargado','w')
        archivo.write(level)
        archivo.close()
        return 0


sys.exit(Client().main(sys.argv))