from os import name
from os import remove
import os
import sys
import Ice
Ice.loadSlice('SliceGauntlet.ice')
import IceGauntlet


class RoomI(IceGauntlet.Room):
    n = 0
    def __init__(self, proxy_auth_server):
        
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def getRoom(self, current=None):
        level= open("server_maps/my_map.json", mode='r', encoding='utf-8')
        return level.read()

    def publish(self,token, new_room, current=None):
        
        if self.auth_server.isValid(token):
            archivo = open("server_maps/mapa_nuevo.json","w")
            archivo.write(new_room)
            print("Mapa publicado")
            archivo.close()
        else:
            print("RoomAlreadyExists")

    def remove(self,token, room_name, current=None):
        if self.auth_server.isValid(token):
            remove(os.path.join("{0}/server_maps/{1}".format(os.getcwd(), room_name)))
        else:
            print("No puedes")


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()

        servant = RoomI(self.communicator().stringToProxy(argv[1]))

        adapter = broker.createObjectAdapter("ServerAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("room1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))