"""
El modulo server.py, establece los sirvientes e imprime los proxys por pantalla
y los guarda en archivos .out. Tambien incorpora las clases y metodos necesarios para
que el cliente pueda jugar un mapa, publicarlo y borrarlo (en caso de que dicho cliente
sea su propietario). Tambien controla expceciones
"""

import os
import json
from posix import listdir
import sys
from os import remove, mkdir
from shutil import rmtree
import uuid
#pylint: disable=E0401
#pylint: disable=C0413
import Ice
Ice.loadSlice('icegauntlet.ice')
import IceGauntlet
import IceStorm
#pylint: enable=E0401
#pylint: enable=C0413

DIR_MAPAS = "./Servers/server_maps/"
DIR_DATA = ""

#Desactivamos el W0613 (argumentos no usados) porque ice nos obliga a poner el current
#pylint: disable=W0613
#Desactivamos tambien el C0103 (no snake case para argumentos) ya que el nombre nos viene
#predefinido en el slice
#pylint: disable=C0103

class RoomManagment(IceGauntlet.RoomManager):
    """Incluye los métodos necesarios para poder publicar y eliminar un mapa"""

    def __init__(self, proxy_auth_server, server_sync, almacen_mapas):
        self.auth_server = IceGauntlet.AuthenticationPrx.checkedCast(
            proxy_auth_server)
        if not self.auth_server:
            raise RuntimeError('Invalid proxy for authentification server')
        self.id = str(uuid.uuid4())
        self.room_manager_sync = server_sync
        self.almacen_mapas = almacen_mapas
        self.almacen_mapas.crear_dir(self.id)

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
        self.almacen_mapas.actualizar_autores()
        self.room_manager_sync.publisher.newRoom(room['room'], self.room_manager_sync.id)

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
        self.almacen_mapas.actualizar_autores()
        self.room_manager_sync.publisher.removedRoom(room_name)

    def available_rooms(self, current=None):
        """Devuelve los mapas disponibles del servidor"""
        return self.rooms

    def getRoom(self, roomName='', current=None):
        """Devuelve un mapa"""
        level = open(DIR_MAPAS+roomName, "r")
        data = level.read()
        level.close()
        return data


class RoomManagerSyncChannelI(IceGauntlet.RoomManagerSync, Ice.Application):
    """
    Clase encargada de sincronizar todos los servidores ejecutados
    sincronizando sus listas de servidores al conectarse y mapas al publicar y eliminar estos
    """
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.topic_mgr = self.get_topic_manager()
        self.topic = self.get_topic()
        self.publisher = self.get_publisher()
        self.pool_servers = {}
        self.RoomManager = None

    def get_topic_manager(self):
        """Devuelve el manager del topico"""
        key = 'IceStorm.TopicManager.Proxy'
        proxy = self.communicator().propertyToProxy(key)
        if proxy is None:
            print("property {} not set".format(key))
            return None
        return IceStorm.TopicManagerPrx.checkedCast(proxy)

    def get_topic(self):
        """Devuelve el tópico"""
        if not self.topic_mgr:
            print('Invalid proxy')
            return 2
        try:
            topic = self.topic_mgr.retrieve("RoomManagerSyncChannel")
        except IceStorm.NoSuchTopic:
            topic = self.topic_mgr.create("RoomManagerSyncChannel")
        return topic

    def get_publisher(self):
        """Obtiene el publicador"""
        publisher = self.topic.getPublisher()
        return IceGauntlet.RoomManagerSyncPrx.uncheckedCast(publisher)

    def hello(self, manager, managerId, current=None):
        """Cuando un nuevo servidor se conecta, anuncia su presencia mediante
        este método y añade su id a su propia lista de servidores"""
        if managerId not in self.pool_servers:
            self.pool_servers[managerId] = {'manager':manager}
            if managerId != self.id:
                print(">>", managerId, ': Hello!!')
                self.publisher.announce(self.RoomManager, self.id)

    def announce(self, manager, managerId, current=None):
        """Los servidores que ya se encontraban conecados saludan al nuevo y lo añaden
        a sus respectivas listas de servidores"""
        print('>>', managerId, ': Welcome, I am ', self.id)
        self.pool_servers[managerId] = {'manager':manager}
        self.dar_mapas()

    def removedRoom(self, roomName, current=None):
        """Cuando un servidor elimina un mapa, se elimina el nombre mapa de la lista
        de mapas de cada servidor"""
        if roomName in listdir(DIR_MAPAS):
            print(roomName, " eliminado de ", self.id)
            remove(DIR_MAPAS+roomName)

    def newRoom(self, name_room, managerId, current=None):
        """Cuando un servidor añade un nuevo mapa, se añade el nombre mapa de la lista
        de mapas de cada servidor"""
        if self.id != managerId:
            if name_room not in listdir(DIR_MAPAS):
                if managerId in self.pool_servers:
                    print("New Room: ", name_room, " de parte de ", managerId)
                    room=json.loads(self.pool_servers[managerId]['manager'].getRoom(name_room))
                    with open(DIR_MAPAS+str(room['room']), 'w') as file:
                        json.dump(room, file)

    def dar_mapas(self):
        """Cuando un servidor nuevo se conecta, recibe los nombres de los mapas contenidos
        en cada servidor"""
        for room in listdir(DIR_MAPAS):
            self.publisher.newRoom(room, self.id)


class RoomCoordinator():
    """
    Clase auxiliar con métodos para la gestion de directorios particulares
    de los servidores, evaluacion de permisos, etc...
    """
    def __init__(self):
        self.available_rooms = []
        self.autores={}

    def crear_dir(self, id_mapa):
        """Crea un directorio en el que se almacenan los mapas de un servidor particular"""
        global DIR_MAPAS
        global DIR_DATA
        DIR_MAPAS=DIR_MAPAS+'Server-'+id_mapa+'/'
        mkdir(DIR_MAPAS)
        DIR_DATA=DIR_MAPAS+'autores.json'
        with open(DIR_DATA, 'w') as file:
            json.dump({}, file)
        self.available_rooms = os.listdir(DIR_MAPAS)
        self.autores = json.load(open(DIR_DATA, 'r'))

    def evaluar_autoria_publicar(self, usuario, room):
        """Evalua que un usuario pueda publicar un mapa"""
        if not usuario:
            raise IceGauntlet.Unauthorized
        if not self.formato_room(room):
            raise IceGauntlet.WrongRoomFormat

        existe = self.existe_room(room['room'])
        pertenece = self.pertenece_room(usuario, room['room'])
        user = self.existe_usuario(usuario)
        if existe and not pertenece:
            raise IceGauntlet.RoomAlreadyExists
        if not existe and not pertenece and not user:
            self.autores[usuario] = {'maps': []}
            self.autores[usuario]["maps"].append(room['room'])
        elif not existe and not pertenece and user:
            self.autores[usuario]["maps"].append(room['room'])

    def evaluar_autoria_eliminar(self, usuario, room):
        """Evalua que un usuario pueda eliminar un mapa"""
        if not usuario:
            raise IceGauntlet.Unauthorized
        if not self.existe_room(room):
            raise IceGauntlet.WrongRoomFormat

        existe = self.existe_room(room)
        pertenece = self.pertenece_room(usuario, room)

        if existe and not pertenece:
            raise IceGauntlet.RoomAlreadyExists
        if not existe:
            raise IceGauntlet.RoomNotExists
        elif existe and pertenece:
            self.autores[usuario]["maps"].remove(room)

    def guardar_room(self, room):
        """Guarda un mapa en el directorio particular de dicho servidor"""
        with open(DIR_MAPAS+str(room['room']), 'w') as file:
            json.dump(room, file)

    def existe_room(self, room):
        """Comprueba si existe un mapa en el directorio con el nombre pasado como argumento"""
        for autor in self.autores:
            for mapa in self.autores[autor]['maps']:
                if mapa == room:
                    return True
        return False

    def existe_usuario(self, usuario):
        """Comprueba si existe un usuario"""
        try:
            # pylint: disable=W0104
            self.autores[usuario]
            # pylint: enable=W0104
            return True
        except KeyError:
            return False

    def pertenece_room(self, user, room):
        """Comprueba si un mapa pertenece a un usuario"""
        try:
            # pylint: disable=W0104
            self.autores[user]
            # pylint: enable=W0104
            for mapa in self.autores[user]["maps"]:
                if room == mapa:
                    return True
        except KeyError:
            pass
        return False

    def formato_room(self, room_data):
        """Comprueba que el formato de un mapa.json sea correcto"""
        try:
            # pylint: disable=W0106
            # pylint: disable=W0104
            room_data["data"]
            room_data["room"]
            # pylint: enable=W0106
            # pylint: enable=W0104
        except KeyError:
            return False
        return True

    def actualizar_autores(self):
        """Actualiza los autores cuando se realiza un publish"""
        with open(DIR_DATA, 'w') as file:
            json.dump(self.autores, file)


class Server(Ice.Application):
    """
    Clase referente a la creacion de los sirvientes de los proxys
    del DungeonI y RoomManagmentI
    """

    def run(self, argv):
        """Ejecuta el servidor"""
        broker = self.communicator()
        auth_server_proxy = argv[1]

        adapterrm = broker.createObjectAdapter("ServerAdapterRM")

        servantRoomSync = RoomManagerSyncChannelI()
        almacenRoom = RoomCoordinator()
        servantrm = RoomManagment(broker.stringToProxy(auth_server_proxy),
        servantRoomSync, almacenRoom)

        proxyrm = adapterrm.add(servantrm, broker.stringToIdentity(servantrm.id))
        proxySync = adapterrm.add(servantRoomSync, broker.stringToIdentity(servantRoomSync.id))

        adapterrm.activate()

        servantRoomSync.RoomManager = IceGauntlet.RoomManagerPrx.checkedCast(proxyrm)
        print(proxyrm)

        servantrm.room_manager_sync.topic.subscribeAndGetPublisher({}, proxySync)
        servantRoomSync.publisher.hello(servantRoomSync.RoomManager,
        servantrm.room_manager_sync.id)

        self.shutdownOnInterrupt()
        broker.waitForShutdown()
        return 0

if Server().main(sys.argv) == 0:
    rmtree(DIR_MAPAS)
    sys.exit()

#pylint: enable=W0613
#pylint: enable=C0103