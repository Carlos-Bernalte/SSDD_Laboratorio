""" El modulo server.py, establece los sirvientes e imprime los proxys por pantalla
y los guarda en archivos .out. Tambien incorpora las clases y metodos necesarios para
que el cliente pueda jugar un mapa, publicarlo y borrarlo (en caso de que dicho cliente
sea su propietario). Tambien controla expceciones"""
import IceGauntlet
import os
import json
from posix import listdir
import random
import sys
from os import name, remove
import uuid
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
import IceStorm
Ice.loadSlice('icegauntlet.ice')
#pylint: enable=E0401
#pylint: enable=C0413

DIR_MAPAS = "./Servers/server_maps/"
DIR_DATA = "./Servers/data.json"


class RoomManagment(IceGauntlet.RoomManager):
    """Incluye los métodos necesarios para poder publicar y eliminar un mapa"""

    def __init__(self, proxy_auth_server, serverSync, almacenMapas):
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(
            proxy_auth_server)
        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')
        self.id = str(uuid.uuid4())
        self.room_manager_sync = serverSync
        self.almacen_mapas = almacenMapas

    def publish(self, token, room_data, current=None):
        """
        Obtiene un mapa en string y lo escribe en un archivocon su nombre almacenado en 'room'.
        Comprueba que el token del Cliente sea valido.
        Actualiza el registro de mapas de cada usuario.
        """
        room = json.loads(room_data)
        usuario = self.auth_server.getOwner(token)
        self.almacen_mapas.evaluar_autoria_publicar(usuario, room)
        self.almacen_mapas.guardar_room(room)
        self.almacen_mapas.guardar()
        self.room_manager_sync._publisher.newRoom(
            room['room'], self.room_manager_sync.id)

    def remove(self, token, room_name, current=None):
        """
        Obtiene un nombre de un mapa y  lo elimina.
        Comprueba que el token del cliente es un token valido,
        si no salta la expcecion: Unauthorized
        Comprueba que el cliente que solicita su eliminacion sea propieatrio del
        mapa, en caso contrario, salta la excepcion Unauthorized
        Si el mapa no existe, salta la excepcion RoomNotExists
        """
        user = self.auth_server.getOwner(token)
        self.almacen_mapas.evaluar_autoria_eliminar(user, room_name)
        remove(DIR_MAPAS+room_name)
        self.almacen_mapas.guardar()
        self.room_manager_sync._publisher.removedRoom(room_name)

    def availableRooms(self, current=None):
        return self.rooms

    def getRoom(self, roomName='', current=None):
        """Devuelve un mapa"""
        level = open(DIR_MAPAS+roomName, "r")
        data = level.read()
        level.close()
        return data


class RoomManagerSyncChannelI(IceGauntlet.RoomManagerSync, Ice.Application):
    def __init__(self):
        self.id = str(uuid.uuid4())
        self._topic_mgr = self.get_topic_manager()
        self._topic = self.get_topic()
        self._publisher = self.get_publisher()
        self._pool_servers = {}
        self.RoomManager = None

    def get_topic_manager(self):
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def get_topic(self):
        if not self._topic_mgr:
            print('Invalid proxy')
            return 2
        try:
            topic = self._topic_mgr.retrieve("RoomManagerSyncChannel")
        except IceStorm.NoSuchTopic:
            topic = self._topic_mgr.create("RoomManagerSyncChannel")
        return topic

    def get_publisher(self):
        publisher = self._topic.getPublisher()
        return IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher)

    def hello(self, manager, managerId, current=None):
        if managerId not in self._pool_servers:
            self._pool_servers[managerId] = manager
            if managerId != self.id:
                print(">>", managerId, ': Hola soy el nuevo')
                self._publisher.announce(self.RoomManager, self.id)

    def announce(self, manager, managerId, current=None):
        print('>>', managerId, ': Bienvenido!!')
        self._pool_servers[managerId] = manager
        self.dar_mapas()

    def removedRoom(self, roomName, current=None):
        if roomName in listdir(DIR_MAPAS):
            print(roomName, " eliminado de ", self.id)
            remove(DIR_MAPAS+roomName)
        print("Mapas restante: ", listdir(DIR_MAPAS))

    def newRoom(self, name_room, managerId, current=None):
        mapas_nuevos = []
        if self.id != managerId:
            print("New Room: ", name_room, " de parte de ", managerId)
            if name_room not in listdir(DIR_MAPAS):
                mapas_nuevos.append(name_room)

    def dar_mapas(self):
        for room in listdir(DIR_MAPAS):
            self._publisher.newRoom(room, self.id)


class RoomCoordinator():
    def __init__(self):
        self._available_rooms_ = os.listdir(DIR_MAPAS)
        self._autores_ = json.load(open(DIR_DATA, 'r'))

    def evaluar_autoria_publicar(self, usuario, room):

        if not usuario:
            raise IceGauntlet.Unauthorized
        if not self.formato_room(room):
            raise IceGauntlet.WrongRoomFormat

        existe = self.existe_room(room['room'])
        pertenece = self.pertenece_room(usuario, room['room'])
        user = self.existe_usuario(usuario)
        if existe and not pertenece:
            raise IceGauntlet.RoomAlreadyExists
        elif not existe and not pertenece and not user:
            self._autores_[usuario] = {'maps': []}
            self._autores_[usuario]["maps"].append(room['room'])
        elif not existe and not pertenece and user:
            self._autores_[usuario]["maps"].append(room['room'])

    def evaluar_autoria_eliminar(self, usuario, room):
        if not usuario:
            raise IceGauntlet.Unauthorized
        if not self.existe_room(room):
            raise IceGauntlet.WrongRoomFormat

        existe = self.existe_room(room)
        pertenece = self.pertenece_room(usuario, room)

        if existe and not pertenece:
            raise IceGauntlet.RoomAlreadyExists
        elif not existe:
            raise IceGauntlet.RoomNotExists
        elif existe and pertenece:
            self._autores_[usuario]["maps"].remove(room)

    def guardar_room(self, room):
        with open(DIR_MAPAS+str(room['room']), 'w') as file:
            json.dump(room, file)

    def existe_room(self, room):
        for autor in self._autores_:
            for mapa in self._autores_[autor]['maps']:
                if mapa == room:
                    return True
        return False

    def existe_usuario(self, usuario):
        try:
            self._autores_[usuario]
            return True
        except KeyError:
            return False

    def pertenece_room(self, user, room):
        try:
            self._autores_[user]
            for mapa in self._autores_[user]["maps"]:
                if room == mapa:
                    return True
        except KeyError:
            pass
        return False

    def formato_room(self, room_data):
        try:
            # pylint: disable=W0106
            room_data["data"]
            room_data["room"]
            # pylint: enable=W0106
        except KeyError:
            return False
        return True

    def guardar(self):
        with open(DIR_DATA, 'w') as file:
            json.dump(self._autores_, file)


class Server(Ice.Application):
    """
    Clase referente a la creacion de los sirvientes de los proxys
    del DungeonI y RoomManagmentI
    """

    def run(self, argv):
        broker = self.communicator()
        auth_server_proxy = argv[1]

        adapterrm = broker.createObjectAdapter("ServerAdapterRM")

        servantRoomSync = RoomManagerSyncChannelI()
        almacenRoom = RoomCoordinator()
        servantrm = RoomManagment(broker.stringToProxy(
            auth_server_proxy), servantRoomSync, almacenRoom)

        proxySync = adapterrm.add(
            servantRoomSync, broker.stringToIdentity(servantRoomSync.id))
        proxyrm = adapterrm.add(
            servantrm, broker.stringToIdentity(servantrm.id))

        adapterrm.activate()

        servantRoomSync.RoomManager = IceGauntlet.RoomManagerPrx.uncheckedCast(
            proxyrm)
        print(proxyrm)

        servantrm.room_manager_sync._topic.subscribeAndGetPublisher(
            {}, proxySync)
        servantRoomSync._publisher.hello(
            servantRoomSync.RoomManager, servantrm.room_manager_sync.id)

        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0


server = Server()
sys.exit(server.main(sys.argv))
