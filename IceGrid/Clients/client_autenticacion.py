#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""El modulo client_autenticacion.py tiene la funcionalidad de
cambiar contraseña y de obtener nuevo token para un usuario registrado."""
import sys
from getpass import getpass
import hashlib
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
#pylint: enable=E0401
#pylint: enable=C0413

class Client(Ice.Application):
    """El cliente puede cambiar la contraseña y/o obtener un nuevo token"""
    def run(self, argv):
        if len(argv) != 2:
            print("Error en el numero de argumentos. Argumentos: nombre + proxy.")
            sys.exit(1)

        proxy = self.communicator().stringToProxy(argv[1])
        authentication = IceGauntlet.AuthenticationPrx.checkedCast(proxy)
        if not authentication:
            raise RuntimeError('Invalid proxy')

        print("Introduce: \n1-Change password \n2-Get new token")
        option = input()
        if  option == "1" :
            print("Introduce el usuario")
            user = input()
            print("Introduce la contraseña actual")
            current_pass = getpass()
            #current_pass = hashlib.sha256(current_pass.encode()).hexdigest()
            print("Introduce la nueva contraseña")
            new_pass = getpass()
            #new_pass = hashlib.sha256(new_pass.encode()).hexdigest()
            try:
                authentication.changePassword(user, current_pass, new_pass)
            except IceGauntlet.Unauthorized:
                print("\nERROR,Contraseña o usuario incorrectos")

        if option == "2" :
            print("Introduce el usuario")
            user = input()
            print("Introduce la contraseña")
            current_pass = getpass()
            #current_pass = hashlib.sha256(current_pass.encode()).hexdigest()
            try:
                token = authentication.getNewToken(user, current_pass)
                print("token: "+token)
            except IceGauntlet.Unauthorized:
                print("\nERROR,Contraseña o ususario incorrectos")

sys.exit(Client().main(sys.argv))
