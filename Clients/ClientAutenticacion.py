#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import Ice
from getpass import getpass
Ice.loadSlice('icegauntlet.ice')
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
                currentPass = getpass()
                currentPass = hashlib.sha256(currentPass.encode()).hexdigest()
                print(currentPass)
                print("Introduce la nueva contraseña")                    
                newPass = getpass()
                newPass = hashlib.sha256(newPass.encode()).hexdigest()
                print(newPass)
                try:
                    authentication.changePassword(user, currentPass, newPass)
                except IceGauntlet.Unauthorized:
                    print("\nERROR,Contraseña o usuario incorrectos")   

            if option == "2" :
                print("Introduce el usuario") 
                user = input()
                print("Introduce la contraseña")                
                currentPass = getpass()
                try:
                    token = authentication.getNewToken(user, currentPass)
                    print("token: "+token)     
                except IceGauntlet.Unauthorized:
                    print("\nERROR,Contraseña o ususario incorrectos")
             
        
sys.exit(Client().main(sys.argv))

