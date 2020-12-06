#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""El modulo client_game_service.py incorpora la funcionalidad de optener un mapa
para poder jugarlo"""
import sys
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet

class Client(Ice.Application):
    """Obtiene un mapa aleatorio del servidor"""
    def run(self, argv):
        """Establece conexion mediante el proxy guardado en 'ProxyDungeon.out
        y el servidor le devuelve un mapa aleatorio'"""
        server_proxy=""
        try:
            with open("proxys/ProxyDungeon.out") as proxy_string:
                server_proxy=proxy_string.read()
        except FileNotFoundError:
            print("No se encuentra el proxy del servidor.")
        proxy = self.communicator().stringToProxy(server_proxy)
        print(">>>: "+str(proxy))
        self.game = IceGauntlet.DungeonPrx.checkedCast(proxy)
        if not self.game:
            raise RuntimeError('Invalid proxy')
        try:
            room_data=self.game.get_room()
            archivo = open("icegauntlet/assets/map.json","w")
            archivo.write(room_data)
            archivo.close()
        except IceGauntlet.RoomNotExists:
            print("El servidor no contiene mapas")



        return 0

sys.exit(Client().main(sys.argv))
    