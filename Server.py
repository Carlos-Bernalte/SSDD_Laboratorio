from os import name
from os import remove
import os
import sys
import Ice
Ice.loadSlice('SliceGauntlet.ice')
import IceGauntlet


class RoomI(IceGauntlet.Room):
    n = 0

    def getRoom(self, current=None):
        level= open("server_maps/my_map.json", mode='r', encoding='utf-8')
        return level.read()

    def publish(self,token, new_room, current=None):
        archivo = open("server_maps/mapa_nuevo.json","w")
        archivo.write(new_room)
        print("Mapa publicado")
        archivo.close()

    def remove(self,token, room_name, current=None):
        remove(os.path.join("{0}/server_maps/{1}".format(os.getcwd(), room_name)))


class Server(Ice.Application):
    def run(self, argv):
        broker = self.communicator()
        servant = RoomI()

        adapter = broker.createObjectAdapter("ServerAdapter")
        proxy = adapter.add(servant, broker.stringToIdentity("room1"))

        print(proxy, flush=True)

        adapter.activate()
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0


server = Server()
sys.exit(server.main(sys.argv))