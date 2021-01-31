""" El modulo server.py, establece los sirvientes e imprime los proxys por pantalla
y los guarda en archivos .out. Tambien incorpora las clases y metodos necesarios para
que el cliente pueda jugar un mapa, publicarlo y borrarlo (en caso de que dicho cliente
sea su propietario). Tambien controla expceciones"""

import os
import json
from posix import listdir
import random
import sys
from os import remove, mkdir
from shutil import rmtree
import uuid
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
import IceStorm
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
#pylint: enable=E0401
#pylint: enable=C0413

DIR_MAPAS = "./Servers/server_maps/"
DIR_DATA = ""


class RoomManagment(IceGauntlet.RoomManager):
    """Incluye los métodos necesarios para poder publicar y eliminar un mapa"""

    def __init__(self, proxy_auth_server, serverSync, almacenMapas):
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(
            proxy_auth_server) 
        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')
        self._id_ = str(uuid.uuid4())
        self.room_manager_sync = serverSync
        self.almacen_mapas = almacenMapas
        self.almacen_mapas.crear_dir(self._id_)

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
        self.room_manager_sync._publisher.newRoom(room['room'], self.room_manager_sync._id_)

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


class RoomManagerSyncChannelI(IceGauntlet.RoomManagerSync, Ice.Application, RoomManagment):
    def __init__(self):
        self._id_ = str(uuid.uuid4())
        self._topic_mgr = self.get_topic_manager()
        self._topic = self.get_topic()
        self._publisher = self.get_publisher()
        self._pool_servers_ = {}
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
        if managerId not in self._pool_servers_:
            self._pool_servers_[managerId] = {'manager':manager}
            if managerId != self._id_:
                print(">>", managerId, ': Hello!!')
                self._publisher.announce(self.RoomManager, self._id_)

    def announce(self, manager, managerId, current=None):
        print('>>', managerId, ': Welcome, I am ', self._id_)
        self._pool_servers_[managerId] = {'manager':manager}
        self.dar_mapas()

    def removedRoom(self, roomName, current=None):

        if roomName in listdir(DIR_MAPAS):
            print(roomName, " eliminado de ", self._id_)
            remove(DIR_MAPAS+roomName)

    def newRoom(self, name_room, managerId, current=None):
        if self._id_ != managerId:
            if name_room not in listdir(DIR_MAPAS):
                if managerId in self._pool_servers_:
                    print("New Room: ", name_room, " de parte de ", managerId)
                    room=json.loads(self._pool_servers_[managerId]['manager'].getRoom(name_room))
                    with open(DIR_MAPAS+str(room['room']), 'w') as file:
                        json.dump(room, file)
            
    def dar_mapas(self):
        for room in listdir(DIR_MAPAS):
            self._publisher.newRoom(room, self._id_)


class RoomCoordinator():      

    def crear_dir(self,_id_):
        global DIR_MAPAS
        global DIR_DATA
        DIR_MAPAS=DIR_MAPAS+'Server-'+_id_+'/'
        mkdir(DIR_MAPAS)
        DIR_DATA=DIR_MAPAS+'autores.json'
        with open(DIR_DATA, 'w') as file:
            json.dump({}, file)
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
        servantrm = RoomManagment(broker.stringToProxy(auth_server_proxy), servantRoomSync, almacenRoom)
        
        proxyrm = adapterrm.add(servantrm, broker.stringToIdentity(servantrm._id_))
        proxySync = adapterrm.add(servantRoomSync, broker.stringToIdentity(servantRoomSync._id_))
        
        adapterrm.activate()

        servantRoomSync.RoomManager = IceGauntlet.RoomManagerPrx.checkedCast(proxyrm)
        print(proxyrm)

        servantrm.room_manager_sync._topic.subscribeAndGetPublisher({}, proxySync)
        servantRoomSync._publisher.hello(servantRoomSync.RoomManager, servantrm.room_manager_sync._id_)

        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

if Server().main(sys.argv) == 0:
    rmtree(DIR_MAPAS)
    sys.exit()


