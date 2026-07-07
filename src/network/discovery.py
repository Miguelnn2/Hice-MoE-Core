-- coding: utf-8 --
====================================================================
HiveMoE-Core - Gobernador de la Red P2P Automatizado (Archivo 5)
====================================================================

import asyncio
import json
import socket
import logging
import urllib.request
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HiveDiscovery")

class HiveDiscoveryProtocol(asyncio.DatagramProtocol):
def init(self, manager):
self.manager = manager
self.transport = None

def connection_made(self, transport):
self.transport = transport

def datagram_received(self, data: bytes, addr: tuple):
try:
mensaje = json.loads(data.decode('utf-8'))
self.manager.procesar_mensaje_p2p(mensaje, addr)
except Exception:
pass

class P2PDiscoveryManager:
def init(self, host_ip: str = "0.0.0.0", port: int = 8001):
self.host_ip = host_ip
self.port = port
self.tabla_enrutamiento = {}
self.ip_publica_auto = self._obtener_ip_local()
self.puerto_grpc_auto = port + 1000

def _obtener_ip_local(self):
"""Intenta descubrir la IP externa mediante un servicio de terceros."""
try:
with urllib.request.urlopen("https://api.ipify.org", timeout=2) as r:
return r.read().decode('utf-8').strip()
except:
return "127.0.0.1"

async def arrancar_nodo_p2p(self):
loop = asyncio.get_running_loop()
self.transport, self.protocol = await loop.create_datagram_endpoint(
lambda: HiveDiscoveryProtocol(self),
local_addr=(self.host_ip, self.port)
)
logger.info(f"[AutoRed] Nodo activo. IP Detectada: {self.ip_publica_auto} | Puerto: {self.port}")

async def unirse_a_dht_global(self, bootstrap_nodes: List[str]):
for nodo in bootstrap_nodes:
partes = nodo.split(":")
destino = (partes[0], int(partes[1]))
peticion = {
"tipo": "PING_HANDSHAKE",
"ip_externa": self.ip_publica_auto,
"puerto_origen": self.port
}
self.enviar_paquete_directo(peticion, destino)

async def registrar_mis_expertos(self, model_hash: str, rango_expertos: str):
anuncio = {
"tipo": "ANUNCIO_EXPERTOS",
"model_hash": model_hash,
"rango_expertos": rango_expertos,
"puerto_grpc": self.puerto_grpc_auto,
"ip_externa": self.ip_publica_auto,
"puerto_origen": self.port
}
for peer_key, info in list(self.tabla_enrutamiento.items()):
self.enviar_paquete_directo(anuncio, (info["ip"], info["puerto_p2p"]))

def procesar_mensaje_p2p(self, mensaje: Dict[str, Any], addr: tuple):
ip_remota = mensaje.get("ip_externa", addr[0])
tipo = mensaje.get("tipo")

if tipo == "PING_HANDSHAKE":
resp = {"tipo": "PONG_RESPUESTA", "ip_externa": self.ip_publica_auto, "puerto_origen": self.port}
self.enviar_paquete_directo(resp, (addr[0], mensaje["puerto_origen"]))

if tipo in ["PONG_RESPUESTA", "ANUNCIO_EXPERTOS"]:
self.registrar_en_tabla(ip_remota, mensaje)

def registrar_en_tabla(self, ip: str, mensaje: Dict[str, Any]):
key = f"{ip}:{mensaje.get('puerto_origen')}"
self.tabla_enrutamiento[key] = {
"ip": ip,
"puerto_p2p": mensaje.get("puerto_origen"),
"puerto_grpc": mensaje.get("puerto_grpc", mensaje.get("puerto_origen", 8000) + 1000),
"model_hash": mensaje.get("model_hash"),
"rango_expertos": mensaje.get("rango_expertos")
}

def enviar_paquete_directo(self, datos: Dict[str, Any], destino: tuple):
if self.transport:
self.transport.sendto(json.dumps(datos).encode(), destino)

async def buscar_proveedores_expertos(self, model_hash: str, experto: int):
return [{"ip": info["ip"], "puerto_grpc": info["puerto_grpc"]}
for info in self.tabla_enrutamiento.values()
if info["model_hash"] == model_hash]