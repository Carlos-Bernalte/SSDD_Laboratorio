""" El modulo server.py, establece los sirvientes e imprime los proxys por pantalla
y los guarda en archivos .out. Tambien incorpora las clases y metodos necesarios para
que el cliente pueda jugar un mapa, publicarlo y borrarlo (en caso de que dicho cliente
sea su propietario). Tambien controla expceciones"""
import os
import json
import random
import sys
from os import remove
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
#pylint: enable=E0401
#pylint: enable=C0413

DIR_MAPAS="./Servers/server_maps/"
DIR_DATA="./Servers/data.json"
class RoomManagment(IceGauntlet.RoomManager):
    """Incluye los métodos necesarios para poder publicar y eliminar un mapa"""

    j = {"Autores":{}}
    if os.stat(DIR_DATA).st_size==0:
        with open(DIR_DATA, "w") as file:
            json.dump(j,file)

    def __init__(self, proxy_auth_server):
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)

        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def autoria(self, autorDueno, level_searched):
        """Método para controlar que el cliente esté autorizado"""

        existe_level=False
        existe_pertenece=False
        with open(DIR_DATA, "r") as file:
            j=json.load(file)

        for autor in j["Autores"]:
            for level in j["Autores"][autor]["maps"]:
                if level_searched==level:
                    existe_level=True

        try:
            #pylint: disable=W0104
            j["Autores"][autorDueno]
            #pylint: enable=W0104
            for level in j["Autores"][autorDueno]["maps"]:
                if level_searched==level:
                    existe_pertenece = True

        except KeyError:
            print("Usuario publica por primera vez")

        return existe_level, existe_pertenece

    def publish(self, token, room_data, current=None):
        """
        Obtiene un mapa en string y lo escribe en un archivocon su nombre almacenado en 'room'.
        Comprueba que el token del Cliente sea valido.
        Actualiza el registro de mapas de cada usuario.
        """
        autor = ""
        if not self.auth_server.getOwner(token):
            raise IceGauntlet.Unauthorized
	
        try:
            # pylint: disable=W0106
            json.loads(room_data)["data"]
            json.loads(room_data)["room"]
            # pylint: enable=W0106
        except KeyError:
            raise IceGauntlet.WrongRoomFormat

        existe_level, existe_pertenece = self.autoria(autor, json.loads(room_data)["room"])

        if (not existe_pertenece and not existe_level) or existe_pertenece:
            archivo = open(DIR_MAPAS+str(json.loads(room_data)["room"]), "w")
            archivo.write(room_data)
            archivo.close()
        else:
            raise IceGauntlet.RoomAlreadyExists

        maps = []
        existe = False
        with open(DIR_DATA) as file:
            j = json.load(file)

        try:
            j["Autores"][token]
        except KeyError:
            j["Autores"].update({"{}".format(autor):{"maps":maps}})
            with open(DIR_DATA, "w") as file:
                json.dump(j, file)

        with open(DIR_DATA) as file:
            j = json.load(file)

        maps = j["Autores"][autor]["maps"]
        for i in range(0,len(maps)):
            if maps[i] ==  json.loads(room_data)["room"]:
                existe = True
        if not existe:
            maps.append(json.loads(room_data)["room"])
            j["Autores"].update({"{}".format(autor):{"maps":maps}})
            with open(DIR_DATA, "w") as file:
                json.dump(j, file)

    def remove(self, token, room_name, current=None):
        """
        Obtiene un nombre de un mapa y  lo elimina.
        Comprueba que el token del cliente es un token valido,
        si no salta la expcecion: Unauthorized
        Comprueba que el cliente que solicita su eliminacion sea propieatrio del
        mapa, en caso contrario, salta la excepcion Unauthorized
        Si el mapa no existe, salta la excepcion RoomNotExists
        """
	
        autor = self.auth_server.getOwner(token)
        print("El autor de este mapa es: ",autor)
        if not autor:
            raise IceGauntlet.Unauthorized

        existe_level, existe_pertenece = self.autoria(autor, room_name)

        if not existe_level:
            raise IceGauntlet.RoomNotExists

        if not existe_pertenece:
            raise IceGauntlet.Unauthorized

        if existe_pertenece:
            with open(DIR_DATA) as file:
                j = json.load(file)
            j["Autores"][autor]["maps"].remove(room_name)
            with open(DIR_DATA, "w") as file:
                json.dump(j, file)
            remove(DIR_MAPAS+str(room_name))
            
class RoomManagerSync():
    def __init__(self):
        self.a=0
    
    def newRoom():
        print("New room")

    def removedRoom():
        print("Removed room")

    def hello():
        print("Hellow")

    def announce():
        print("Announce")

class DungeonI(IceGauntlet.Dungeon):
    """Clase referente a la accion de obtener un mapa"""

    def __init__(self, proxy_auth_server):
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(proxy_auth_server)
        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')

    def getRoom(self, current=None):
        """Devuelve un mapa aleatorio"""
        maps = os.listdir("server_maps/")
        index = random.randrange(0, len(maps))
        level= open("server_maps/"+maps[index], "r")
        data=level.read()
        level.close()
        return data


class Server(Ice.Application):
    """
    Clase referente a la creacion de los sirvientes de los proxys
    del DungeonI y RoomManagmentI
    """

    def run(self, argv):

        broker = self.communicator()
        auth_server_proxy=argv[1]

        adapter_gs = broker.createObjectAdapter("ServerAdapterGS")
        servant_gs = DungeonI(broker.stringToProxy(auth_server_proxy))
        proxy_gs = adapter_gs.add(servant_gs, broker.stringToIdentity("dungeon1"))
        adapter_gs.activate()

        self.save_proxy(proxy_gs, "ProxyDungeon.out")

        adapterrm = broker.createObjectAdapter("ServerAdapterRM")
        servantrm = RoomManagment(broker.stringToProxy(auth_server_proxy))
        proxyrm = adapterrm.add(servantrm, broker.stringToIdentity("roommanag1"))
        adapterrm.activate()

        print(proxyrm)

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
