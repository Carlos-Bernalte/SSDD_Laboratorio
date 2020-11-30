from os import name, read
from os import remove
import os
import json
import random
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class RoomManagment(IceGauntlet.Room):
    n = 0
    def __init__(self, proxy_auth_server):
        
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')


    def publish(self,token, new_room, current=None):
        
        if self.auth_server.isValid(token):
            archivo = open("server_maps/mapa_nuevo.json", "w")
            archivo.write(new_room)
            print("Mapa publicado")
            archivo.close()

            archivo = open("server_maps/mapa_nuevo.json")
            archivojson = json.load(archivo)
            namemap = archivojson['room']
            os.rename("server_maps/mapa_nuevo.json","server_maps/{}.json".format(namemap))

        else:
            print("Autenticación incorrecta")

    def remove(self,token, room_name, current=None):
        if self.auth_server.isValid(token):
            remove(os.path.join("{0}/server_maps/{1}".format(os.getcwd(), room_name)))
        else:
            print("No puedes")

class GameService(IceGauntlet.GameService):

    def __init__(self, proxy_auth_server):
        
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def getRoom(self, current=None):
        maps = os.listdir("server_maps/")
        index = random.randrange(0, len(maps))
        level= open("server_maps/"+maps[index], mode='r', encoding='utf-8')

        return level.read()


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        auth_server_proxy=None
        try:
            auth_server_proxy=open("proxys/auth_server-proxy.out", "r")
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor de autentificación.")

        prox=auth_server_proxy.read()
        servantRM = RoomManagment(self.communicator().stringToProxy(prox))
        servantGS = GameService(self.communicator().stringToProxy(prox))

        adapterRM = broker.createObjectAdapter("ServerAdapterRM")
        adapterGS = broker.createObjectAdapter("ServerAdapterGS")

        proxyRM = adapterRM.add(servantRM, broker.stringToIdentity("roomRM"))
        proxyGS = adapterGS.add(servantGS, broker.stringToIdentity("roomGS"))

        fileProxyRM = open("proxys/ProxyRM.out", "w")
        fileProxyGS = open("proxys/ProxyGS.out", "w")

        fileProxyRM.write(str(proxyRM))
        fileProxyGS.write(str(proxyGS))

        fileProxyRM.close()
        fileProxyGS.close()

        print("Proxy Room Managment: "+str(proxyRM))
        print("Proxy Game Service: "+str(proxyGS))

        adapterRM.activate()
        adapterGS.activate()

        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))