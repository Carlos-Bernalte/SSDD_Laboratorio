#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""El modulo client_room_managment.py incorpora los metodos necesarios para
publicar y borrar un mapa en el servidor"""
import sys
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
#pylint: enable=E0401
#pylint: enable=C0413

class Client(Ice.Application):
    """Se conecta con el servidor y contiene los métodos para publicar
    y borrar un mapa del servidor"""
    def publish_map(self, token="", map_name=""):
        """Publica un mapa en el servidor"""
        try:
            new_room=open("icegauntlet/editor/maps/"+map_name, "r")
            self.room.publish(token,new_room.read())
            new_room.close()
        except IceGauntlet.WrongRoomFormat:
            print("Formato mapa incorrecto")
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

        if len(argv) == 5:
            proxy = self.communicator().stringToProxy(argv[2])
            self.room = IceGauntlet.RoomManagerPrx.checkedCast(proxy)
            if not self.room:
                raise RuntimeError('Invalid proxy')
            if argv[1]=="-p":
                self.publish_map(argv[3],argv[4])
            elif argv[1]=="-r":
                self.remove_map(argv[3],argv[4])
            else:
                print("Opción no disponible.")
                return 1

        return 0

sys.exit(Client().main(sys.argv))
