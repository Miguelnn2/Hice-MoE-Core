-- coding: utf-8 --
====================================================================
HiveMoE-Core - Servidor y Cliente de Transmisión gRPC (Archivo 6 de 9)
====================================================================

import grpc
import asyncio
import logging

Estos módulos son generados automáticamente al compilar el archivo proto anterior
import inference_pb2 as pb2
import inference_pb2_grpc as pb2_grpc

from src.inference.engine import InferenceEngine

logger = logging.getLogger("HiveProtocol")

class HiveInferenceServicer(pb2_grpc.HiveInferenceServiceServicer):
"""
Servidor gRPC Asíncrono local.
Escucha peticiones de la red y procesa las operaciones matemáticas en la CPU.
"""
def init(self, engine: InferenceEngine, rango_inicio: int, rango_fin: int):
self.engine = engine
self.rango_inicio = rango_inicio
self.rango_fin = rango_fin

async def ProcesarExpertosMoE(self, request: pb2.InferenceRequest, context: grpc.aio.ServicerContext) -> pb2.InferenceResponse:
"""
Punto de entrada de red. Ejecuta la validación de tipo de modelo y
asigna los tensores recibidos al motor matemático de expertos.
"""
# 1. Filtro de Desvío a nivel de Red: Validar que sea arquitectura MoE
if request.model_type != "MoE":
logger.warning(f"[Servidor] Petición rechazada: El tipo de modelo '{request.model_type}' no es válido.")
return pb2.InferenceResponse(
status=pb2.InferenceResponse.Status.RECHAZADO_TIPO_INVALIDO,
mensaje_error="Filtro activado: Este nodo asistente está configurado únicamente para capas distribuidas MoE."
)

# 2. Validación de Frontera/Jurisdicción de Expertos
if request.rango_inicio < self.rango_inicio or request.rango_fin > self.rango_fin:
logger.warning(f"[Servidor] Rango solicitado [{request.rango_inicio}-{request.rango_fin}] fuera de límites locales.")
return pb2.InferenceResponse(
status=pb2.InferenceResponse.Status.ERROR_CALCULO,
mensaje_error=f"Jurisdicción denegada. Este nodo solo procesa el rango [{self.rango_inicio}-{self.rango_fin}]."
)

try:
# 3. Deserialización binaria ultrarrápida del tensor de entrada
matriz_input = self.engine.deserializar_tensor(request.input_tensor)

# 4. Cómputo algebraico real a través de los expertos
matriz_output = self.engine.calcular_capa_expertos(matriz_input, request.rango_inicio, request.rango_fin)

# 5. Serialización del resultado de vuelta al contenedor gRPC
proto_output_tensor = pb2.Tensor()
self.engine.serializar_tensor(matriz_output, proto_output_tensor)

return pb2.InferenceResponse(
status=pb2.InferenceResponse.Status.OK,
output_tensor=proto_output_tensor
)

except Exception as e:
logger.error(f"[Servidor] Error interno en el cálculo matricial: {str(e)}")
return pb2.InferenceResponse(
status=pb2.InferenceResponse.Status.ERROR_CALCULO,
mensaje_error=f"Fallo en la unidad de tensores del nodo asistente: {str(e)}"
)

class P2PClient:
"""
Cliente gRPC Asíncrono de alto rendimiento.
Empuja matrices numéricas a través de internet hacia los nodos colaboradores.
"""
@staticmethod
async def enviar_peticion_calculo(ip_remota: str, puerto_remoto: int, request_proto: pb2.InferenceRequest) -> pb2.InferenceResponse:
"""
Abre un canal inseguro (insecure_channel) optimizado por sockets, transmite la petición
y espera la respuesta de vuelta de manera asíncrona sin bloquear la CPU.
"""
direccion_nodo = f"{ip_remota}:{puerto_remoto}"

# Configuración de canal asíncrono con opciones de compresión y tamaño de paquete optimizados
opciones_canal = [
('grpc.max_send_message_length', 50 * 1024 * 1024), # Soporta tensores de hasta 50MB
('grpc.max_receive_message_length', 50 * 1024 * 1024)
 ]

async with grpc.aio.insecure_channel(direccion_nodo, options=opciones_canal) as channel:
stub = pb2_grpc.HiveInferenceServiceStub(channel)
try:
# Disparar la llamada RPC remota
respuesta = await stub.ProcesarExpertosMoE(request_proto, timeout=10.0)
return respuesta
except grpc.RpcError as e:
logger.error(f"[Cliente] Error de red en el socket conectado a {direccion_nodo}: {e.details()}")
return pb2.InferenceResponse(
status=pb2.InferenceResponse.Status.ERROR_HARDWARE_SATURADO,
mensaje_error=f"El nodo remoto no respondió en el tiempo límite: {e.details()}"
)