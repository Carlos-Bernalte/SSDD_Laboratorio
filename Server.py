from os import name
import sys
import Ice
Ice.loadSlice('Slice.ice')
import IceGauntlet


class RoomI(IceGauntlet.Room):
    n = 0

    def getRoom(self, current=None):
        level= open("server_maps/my_map.json", mode='r', encoding='utf-8')
        return level.read()

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