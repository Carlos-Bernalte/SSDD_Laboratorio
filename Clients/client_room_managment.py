#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""El modulo client_room_managment.py incorpora los metodos necesarios para
publicar y borrar un mapa en el servidor"""
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    """Se conecta con el servidor y contiene los métodos para publicar
    y borrar un mapa del servidor"""
    def publish_map(self, token="", map_name=""):
        """Publica un mapa en el servidor"""
        try:
            new_room=open("icegauntlet/editor/maps/"+map_name, "r")
            self.room.publish(token,new_room.read())
            new_room.close()

        except IceGauntlet.Unauthorized:
            print("TOKEN INCORRECTO")
        except IceGauntlet.RoomAlreadyExists:
            print("El mapa exite, pero no es tuyo")
        except FileNotFoundError:
            print("Archivo no encontrado en el directorio 'Maps'")


    def remove_map(self, token="", map_name=""):
        """Elimina un mapa del servidor dado un nombre"""
        try:
            self.room.remove(token,map_name)
        except IceGauntlet.Unauthorized:
            print("No estas autorizado para realizar la operación")
        except IceGauntlet.RoomNotExists:
            print("El mapa que se esta intentando borrar no existe")

    def run(self, argv):
        server_proxy=""
        try:
            with open("proxys/ProxyRM.out") as proxy_string:
                server_proxy=proxy_string.read()
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")

        proxy = self.communicator().stringToProxy(server_proxy)
        self.room = IceGauntlet.RoomManagerPrx.checkedCast(proxy)
        if not self.room:
            raise RuntimeError('Invalid proxy')

        if len(argv) == 4:
            if argv[1]=="-p":
                self.publish_map(argv[2],argv[3])
            elif argv[1]=="-r":
                self.remove_map(argv[2],argv[3])
            else:
                print("Opción no disponible.")
                return 1

        return 0

sys.exit(Client().main(sys.argv))
