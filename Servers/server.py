""" El modulo server.py, establece los sirvientes e imprime los proxys por pantalla
y los guarda en archivos .out. Tambien incorpora las clases y metodos necesarios para
que el cliente pueda jugar un mapa, publicarlo y borrarlo (en caso de que dicho cliente
sea su propietario)"""
import os
import json
import random
import sys
from os import remove
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class RoomManagmentI(IceGauntlet.RoomManager):
    """Incluye los métodos para publicar y eliminar un mapa"""
    n = 0
    def __init__(self, proxy_auth_server):

        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')


    def publish(self, token, room_data="", current=None):
        """Obtiene un mapa en string y lo escribe en un archivo
        con su nombre almacenado en 'room'"""
        if self.auth_server.isValid(token):
            archivo = open("server_maps/"+json.loads(room_data)["room"], "w")
            archivo.write(room_data)
            archivo.close()

        else:
            print("Autenticación incorrecta")

    def remove(self,token, room_name, current=None):
        """Obtiene un nombre de un mapa y si existe en el servidor, lo elimina"""
        if self.auth_server.isValid(token):
            remove("server_maps/"+str(room_name))
        else:
            print("No puedes")

class DungeonI(IceGauntlet.Dungeon):
    """Clase referente a la accion de obtener un mapa"""
    def __init__(self, proxy_auth_server):

        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)
        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def get_room(self, current=None):
        """Devuelve un mapa aleatorio"""
        maps = os.listdir("server_maps/")
        index = random.randrange(0, len(maps))
        level= open("server_maps/"+maps[index], "r")
        data=level.read()
        level.close()
        return data


class Server(Ice.Application):
    """Clase referente a la creacion de los sirvientes de los proxys
    del DungeonI y RoomManagmentI"""
    def run(self, argv):
        broker = self.communicator()
        auth_server_proxy=None
        try:
            auth_server_proxy=open("proxys/auth_server-proxy.out", "r")
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor de autentificación.")

        prox=auth_server_proxy.read()

        adapter_gs = broker.createObjectAdapter("ServerAdapterGS")
        servant_gs = DungeonI(self.communicator().stringToProxy(prox))
        proxy_gs = adapter_gs.add(servant_gs, broker.stringToIdentity("dungeon1"))
        #proxygs = adaptergs.addWithUUID(servantgs)
        adapter_gs.activate()

        self.save_proxy(proxy_gs, "ProxyDungeon.out")

        adapterrm = broker.createObjectAdapter("ServerAdapterRM")
        servantrm = RoomManagmentI(self.communicator().stringToProxy(prox))
        proxyrm = adapterrm.add(servantrm, broker.stringToIdentity("roommanag1"))
        adapterrm.activate()

        self.save_proxy(proxyrm, "ProxyRM.out")


        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0

    def save_proxy(self, proxy, file_name=""):
        """Funcion encargada de guardar el proxy en archivos con el nombre dado"""
        fileproxy = open("proxys/"+file_name, "w")
        fileproxy.write(str(proxy))
        fileproxy.close()
        print(proxy)


server = Server()
sys.exit(server.main(sys.argv))
