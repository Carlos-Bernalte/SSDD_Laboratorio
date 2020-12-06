# ICEGAUNTLET

Miembros del equipo:

- Carlos Bernalte García-Junco <carlos.bernalte@alu.uclm.es>
- Juan Muñoz Calvo <Juan.Munoz7@alu.uclm.es>
- Julio Molina Díaz <Julio.Molina@alu.uclm.es>

REPOSITORIO: <https://github.com/Carlos-Bernalte/SSDD_MunozMolinaBernalte>
##Ejecución de los scripts:
Gestion de mapas:

Los mapas que se deseen subir al servidor se encuentran el la carpeta icegauntlet\editor\maps.
```sh
./delete_map.sh proxy_servicio_de_mapas token nombre_del_archivo
./upload_map.sh proxy_servicio_de_mapas token nombre_del_mapa
```
Ejecución de servidor de mapas:
```sh
./run_map_server.sh proxy_servicio_autentifición
```
Ejecución del juego:
```sh
./run_game.sh proxy_servicio_de_juego
```
Ejecución de servidor de autentificación en local:
```sh
./run_auth_server.sh
```
Ejecución del cliente de autentificación:
```sh
./run_auth_client.sh
```
