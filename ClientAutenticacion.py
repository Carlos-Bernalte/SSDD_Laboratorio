#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import Ice
Ice.loadSlice('SliceGauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    def run(self, argv):
        proxy = self.communicator().stringToProxy(argv[1])
        authentication = IceGauntlet.AuthenticationPrx.checkedCast(proxy)

        if len(argv) == 3:
            valido = authentication.isValid(argv[2])
            print(valido)
        else:
            print("Introduce: 1-Change password 2-Get new token") 
            option = input()
            if  option == "1" :
                print("Introduce el usuario") 
                user = input()
                print("Introduce la contraseña actual")
                currentPass = input()
                print("Introduce la nueva contraseña")
                newPass = input()
                authentication.changePassword(user, currentPass, newPass)
            if option == "2" :
                print("Introduce el usuario") 
                user = input()
                print("Introduce la contraseña")
                currentPass = input()
                token = authentication.getNewToken(user, currentPass)
                print(token)            
        
sys.exit(Client().main(sys.argv))

