from os import name, read, removedirs
from os import remove
import os
import json
import random
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class RoomManagmentI(IceGauntlet.RoomManager):
    n = 0
    def __init__(self, proxy_auth_server):
        
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')


    def publish(self,token, roomData="", current=None):

        if self.auth_server.isValid(token):
            archivo = open("server_maps/"+json.loads(roomData)["room"], "w")
            archivo.write(roomData)
            archivo.close()

        else:
            print("Autenticación incorrecta")

    def remove(self,token, room_name, current=None):
        if self.auth_server.isValid(token):
            remove("server_maps/"+str(room_name))
        else:
            print("No puedes")

class DungeonI(IceGauntlet.Dungeon):

    def __init__(self, proxy_auth_server):
        
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)
        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def getRoom(self, current=None):
        maps = os.listdir("server_maps/")
        index = random.randrange(0, len(maps))
        level= open("server_maps/"+maps[index], "r")
        data=level.read()
        level.close()
        return data


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        auth_server_proxy=None
        try:
            auth_server_proxy=open("proxys/auth_server-proxy.out", "r")
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor de autentificación.")

        prox=auth_server_proxy.read()
        
        adapterGS = broker.createObjectAdapter("ServerAdapterGS")
        servantGS = DungeonI(self.communicator().stringToProxy(prox))
        proxyGS = adapterGS.add(servantGS, broker.stringToIdentity("dungeon1"))
        #proxyGS = adapterGS.addWithUUID(servantGS)
        adapterGS.activate()

        self.saveProxy(proxyGS, "ProxyDungeon.out")

        adapterRM = broker.createObjectAdapter("ServerAdapterRM")
        servantRM = RoomManagmentI(self.communicator().stringToProxy(prox))
        proxyRM = adapterRM.add(servantRM, broker.stringToIdentity("roommanag1"))
        adapterRM.activate()

        self.saveProxy(proxyRM, "ProxyRM.out")
        
        
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0
    def saveProxy(self, proxy, fileName=""):
        fileProxyGS = open("proxys/"+fileName, "w")
        fileProxyGS.write(str(proxy))
        fileProxyGS.close()
        print(proxy)


server = Server()
sys.exit(server.main(sys.argv))