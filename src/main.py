-- coding: utf-8 --
====================================================================
HiveMoE-Core - Orquestador Central del Enjambre (Archivo 8 de 9)
====================================================================

import os
import sys
import argparse
import asyncio
import logging
import numpy as np
import grpc

Configuración estricta de rutas para resolución de módulos locales
directorio_raiz = os.path.dirname(os.path.abspath(file))
sys.path.insert(0, directorio_raiz)
sys.path.insert(0, os.path.join(directorio_raiz, "src"))

try:
from src.inference.loader import MoELoader
from src.inference.engine import InferenceEngine
from src.network.discovery import P2PDiscoveryManager
from src.network.protocol import HiveInferenceServicer, P2PClient
from src.utils.validation import TensorValidator
import inference_pb2 as pb2
import inference_pb2_grpc as pb2_grpc
except ImportError as e:
print(f"🚨 Error de importación de módulos internos: {e}")
print("Asegúrate de haber compilado previamente el archivo proto ejecutando el comando indicado en el Archivo 2.")
sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HiveOrchestrator")

async def anunciar_nodo_periodicamente(discovery_manager, model_hash, rango_expertos):
"""
Bucle asíncrono persistente encargado de emitir pulsos de telemetría (Gossip)
hacia la red P2P para informar que este nodo sigue activo y listo para computar.
"""
while True:
try:
await discovery_manager.registrar_mis_expertos(model_hash, rango_expertos)
except Exception as e:
logger.error(f"[Loop Anuncio] Fallo al publicar telemetría de expertos: {e}")
await asyncio.sleep(30) # Emitir latido de presencia estrictamente cada 30 segundos

async def run_node(args):
"""
Inicializa el dispositivo local como un nodo proveedor activo de cómputo MoE.
Levanta el servidor gRPC de tensores y el socket UDP de descubrimiento de red.
"""
logger.info("=== INICIALIZANDO NODO DE PRODUCCIÓN HIVEMOE-CORE ===")

# 1. Validar la integridad y estructura del archivo de pesos GGUF
loader = MoELoader(args.model)
try:
metadatos = loader.verificar_admision_moe()
logger.info(f"[Loader] Archivo GGUF Validado con éxito. Tamaño en disco: {metadatos['tamano_en_disco_gb']} GB")
except Exception as e:
logger.error(f"[Loader] {e}")
return

# Extraer el rango numérico de expertos asignados a este hardware de forma segura
try:
inicio, fin = map(int, args.experts.split("-"))
except ValueError:
logger.error("🚨 Formato de rango de expertos inválido. Use la convención 'inicio-fin' (ej: '0-3')")
return

# 2. Inicializar el motor computacional enlazado a C++
llama_engine = loader.inicializar_bloque_expertos(inicio, fin)
math_engine = InferenceEngine(llama_engine)

# 3. Configurar e instanciar el servidor de sockets binarios gRPC
puerto_grpc = args.port + 1000
servidor_grpc = grpc.aio.server(options=[
('grpc.max_send_message_length', 50 * 1024 * 1024), # Límite expandido a 50MB para tensores densos
('grpc.max_receive_message_length', 50 * 1024 * 1024)
 ])

servicer_logico = HiveInferenceServicer(math_engine, inicio, fin)
pb2_grpc.add_HiveInferenceServiceServicer_to_server(servicer_logico, servidor_grpc)
servidor_grpc.add_insecure_port(f"0.0.0.0:{puerto_grpc}")

# 4. Levantar la capa de red descentralizada UDP
discovery_manager = P2PDiscoveryManager(host_ip="0.0.0.0", port=args.port)
await discovery_manager.arrancar_nodo_p2p()

# Acoplar el nodo a la red si se especifican computadoras semilla
if args.bootstrap:
nodos_semilla = args.bootstrap.split(",")
await discovery_manager.unirse_a_dht_global(nodos_semilla)

# 5. Activación de servicios en paralelo
await servidor_grpc.start()
logger.info(f"[gRPC] Servidor de transferencia de tensores activo en puerto {puerto_grpc}")

# Enlazar la tarea en segundo plano de anuncios periódicos
model_hash_simulado = "hash_gguf_moe_production_v1"
asyncio.create_task(anunciar_nodo_periodicamente(discovery_manager, model_hash_simulado, args.experts))

try:
# Bloquear el hilo principal manteniendo el nodo en escucha permanente
await asyncio.Event().wait()
except asyncio.CancelledError:
logger.info("Recibida señal de parada. Apagando sockets de red de forma segura...")
finally:
await servidor_grpc.stop(0)
logger.info("Nodo HiveMoE-Core detenido limpiamente.")

async def run_client_test(args):
"""
Simula la ejecución completa de una consulta distribuida.
Genera tensores sintéticos reales en la memoria del sistema y los transmite por red.
"""
logger.info("=== INICIALIZANDO CLIENTE DE INFERENCIA DISTRIBUIDA ===")
discovery_manager = P2PDiscoveryManager(host_ip="0.0.0.0", port=args.port)
await discovery_manager.arrancar_nodo_p2p()

model_hash_meta = "hash_gguf_moe_production_v1"

if args.bootstrap:
await discovery_manager.unirse_a_dht_global(args.bootstrap.split(","))
await asyncio.sleep(2.0) # Ventana de espera prudencial para sincronización UDP
else:
logger.info("[Test] Entorno aislado detectado. Inicializando topología de enrutamiento local automatizada...")
discovery_manager.registrar_en_tabla("127.0.0.1", {
"tipo": "ANUNCIO_EXPERTOS",
"puerto_origen": args.port,
"puerto_grpc": args.port + 1000,
"model_hash": model_hash_meta,
"rango_expertos": "0-7"
})

# Intentar localizar dinámicamente un nodo proveedor para el Experto N° 2
experto_objetivo = 2
proveedores = await discovery_manager.buscar_proveedores_expertos(model_hash_meta, experto_objetivo)

if not proveedores:
logger.error(f"🚨 Error de Topología: No se encontraron nodos asistentes en la malla para el experto {experto_objetivo}")
return

nodo_asistente = proveedores[0]
logger.info(f"[Test] Par óptimo localizado en la tabla de rutas: {nodo_asistente['ip']}:{nodo_asistente['puerto_grpc']}")

# Fabricar una matriz matemática real de activaciones vectoriales (Tokens x Hidden Size)
# Geometría estándar de producción MoE: [1 Token, 4096 Canales Ocultos]
logger.info("[Test] Generando matriz de activaciones en memoria RAM [1, 4096]...")
matriz_origen = np.random.rand(1, 4096).astype(np.float32)

# Construcción de la envoltura binaria gRPC
proto_tensor = pb2.Tensor()
engine_aux = InferenceEngine(None) # Instancia auxiliar liviana dedicada únicamente a serializar
engine_aux.serializar_tensor(matriz_origen, proto_tensor)

peticion = pb2.InferenceRequest(
model_hash=model_hash_meta,
model_type="MoE",
rango_inicio=0,
rango_fin=7,
input_tensor=proto_tensor
)

# Despachar solicitud a través del socket de red conectado al nodo asistente
logger.info(f"[Test] Transmitiendo paquete de tensores hacia {nodo_asistente['ip']}...")
respuesta = await P2PClient.enviar_peticion_calculo(
nodo_asistente['ip'],
nodo_asistente['puerto_grpc'],
peticion
)

# Procesamiento y auditoría de la respuesta de red
if respuesta.status == pb2.InferenceResponse.Status.OK:
matriz_calculada = engine_aux.deserializar_tensor(respuesta.output_tensor)
logger.info(f"✨ ¡Transmisión Completa! Matriz devuelta exitosamente. Dimensiones físicas: {matriz_calculada.shape}")

# Validar consistencia matemática elemental para mitigar inestabilidades
validador = TensorValidator()
if validador.verificar_sanidad_basica(matriz_calculada):
logger.info("✅ Control de Calidad Exitoso: El flujo de datos es estable y apto para capas de decodificación.")
else:
logger.error(f"🚨 Error en Inferencia Distribuida. Código: {respuesta.status}. Causa: {respuesta.mensaje_error}")

def main():
parser = argparse.ArgumentParser(description="Orquestador de Producción Central HiveMoE-Core")
parser.add_argument("--mode", type=str, required=True, choices=["node", "test"], help="Modo operativo: 'node' (Servidor/Proveedor) o 'test' (Cliente/Simulador)")
parser.add_argument("--model", type=str, default="", help="Ruta absoluta al archivo de pesos del modelo .gguf (Obligatorio en modo node)")
parser.add_argument("--port", type=int, default=8001, help="Puerto base UDP para descubrimiento P2P (gRPC utilizará de forma nativa puerto+1000)")
parser.add_argument("--experts", type=str, default="0-3", help="Rango cerrado de expertos asignados a este hardware (ejemplo: '0-3', '4-7')")
parser.add_argument("--bootstrap", type=str, default="", help="Lista opcional de nodos semilla IP:PUERTO para engancharse a la red de forma directa")

args = parser.parse_args()

if args.mode == "node" and not args.model:
parser.error("🚨 Error de Entrada: El parámetro '--model' es estrictamente obligatorio para inicializar el modo 'node'.")

try:
if args.mode == "node":
asyncio.run(run_node(args))
elif args.mode == "test":
asyncio.run(run_client_test(args))
except KeyboardInterrupt:
print("\nTerminación forzada por el usuario.")

if name == "main":
main()