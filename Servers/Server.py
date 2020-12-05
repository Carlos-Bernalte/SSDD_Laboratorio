from os import name, read, removedirs
from os import remove
import os
import json
import random
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet


class RoomManagment(IceGauntlet.RoomManager):
    j = {"Autores":{}}
    n = 0
    with open("Servers/data.json", "w") as file:
        json.dump(j,file)

    def __init__(self, proxy_auth_server):
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def autoria(self, token, levelSearched):
        existe_level=False
        existe_usuario=True
        with open("Servers/data.json", "r") as file:
            j=json.load(file)

        for autor in j["Autores"]:
            for level in j["Autores"][autor]["maps"]:
                if levelSearched==level:
                    existe_level=True
        try:
            j["Autores"][token]
            existe_usuario = True
            for level in j["Autores"][token]["maps"]:
                if levelSearched==level:
                    existe_level=True
        except KeyError:
            print("Usuario no encontrado")
            existe_usuario=False

        return existe_level, existe_usuario

    def publish(self,token, roomData, current=None):
        if not self.auth_server.isValid(token): raise IceGauntlet.Unauthorized()
        existe_level, existe_usuario = self.autoria(token, json.loads(roomData)["room"])
        if existe_level and not existe_usuario: raise IceGauntlet.RoomAlreadyExists()
        try:
            json.loads(roomData)["data"]
            json.loads(roomData)["room"]
        except KeyError:
            raise IceGauntlet.WrongRoomFormat()
        
        maps = []
        existe = False
        with open("Servers/data.json") as file:
            j = json.load(file)
        
        try:
            j["Autores"][token]
        except KeyError:
            j["Autores"].update({"{}".format(token):{"maps":maps}})
            with open("Servers/data.json", "w") as file:
                json.dump(j, file)
        
        with open("Servers/data.json") as file:
            j = json.load(file)
            
        maps = j["Autores"][token]["maps"]
        for i in range(0,len(maps)):
            if maps[i] ==  json.loads(roomData)["room"]:
                existe = True
        if not existe:        
            maps.append(json.loads(roomData)["room"])
            j["Autores"].update({"{}".format(token):{"maps":maps}})
            with open("Servers/data.json", "w") as file:
                json.dump(j, file)
        
        archivo = open("server_maps/"+str(json.loads(roomData)["room"]), "w")
        archivo.write(roomData)
        archivo.close()

    def remove(self, token, room_name, current=None):
        if not self.auth_server.isValid(token): raise IceGauntlet.Unauthorized()
        existe_level, existe_usuario = self.autoria(token, room_name) 
        if existe_level and not existe_usuario: raise IceGauntlet.Unauthorized()
        elif not existe_level: raise IceGauntlet.RoomNotExists()
        elif existe_level and existe_usuario:
            remove("server_maps/"+str(room_name))

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
        servantRM = RoomManagment(self.communicator().stringToProxy(prox))
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
