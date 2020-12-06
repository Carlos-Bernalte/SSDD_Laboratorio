#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""El modulo client_autenticacion.py tiene la funcionalidad de
cambiar contraseña y de obtener nuevo token para un usuario registrado."""
import sys
from getpass import getpass
import Ice
import hashlib
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    """El cliente puede cambiar la contraseña y/o obtener un nuevo token"""
    def run(self, argv):
        server_proxy = ""
        try:
            with open("proxys/auth_server-proxy.out") as proxy_string:
                server_proxy=proxy_string.read()
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")

        proxy = self.communicator().stringToProxy("default -t -e 1.1:tcp -h pike.esi.uclm.es -p 6000 -t 60000")
        authentication = IceGauntlet.AuthenticationPrx.checkedCast(proxy)

        if len(argv) == 3:
            valido = authentication.isValid(argv[1])
            print(valido)
        else:
            print("Introduce: 1-Change password 2-Get new token")
            option = input()
            if  option == "1" :
                print("Introduce el usuario")
                user = input()
                print("Introduce la contraseña actual")
                current_pass = getpass()
                current_pass = hashlib.sha256(current_pass.encode()).hexdigest()
                print("Introduce la nueva contraseña")
                new_pass = getpass()
                new_pass = hashlib.sha256(new_pass.encode()).hexdigest()
                try:
                    authentication.changePassword(user, current_pass, new_pass)
                except IceGauntlet.Unauthorized:
                    print("\nERROR,Contraseña o usuario incorrectos")

            if option == "2" :
                print("Introduce el usuario")
                user = input()
                print("Introduce la contraseña")
                current_pass = getpass()
                current_pass = hashlib.sha256(current_pass.encode()).hexdigest()
                try:
                    token = authentication.getNewToken(user, current_pass)
                    print("token: "+token)
                except IceGauntlet.Unauthorized:
                    print("\nERROR,Contraseña o ususario incorrectos")

sys.exit(Client().main(sys.argv))
