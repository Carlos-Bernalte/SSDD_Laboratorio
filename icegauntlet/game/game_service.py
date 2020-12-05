#!/usr/bin/python3
# -*- coding: utf-8 -*-

import Ice
import json
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    def __init__(self, proxy_string=""):
        print(">>>>> ", proxy_string)
        proxy = self.communicator().stringToProxy(proxy_string)
        self.game = IceGauntlet.DungeonPrx.checkedCast(proxy)
        if not self.game:
            raise RuntimeError('Invalid proxy')
        
    def next_room(self):
        return self.game.get_room()
        
    