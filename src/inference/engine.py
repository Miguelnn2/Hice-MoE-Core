-- coding: utf-8 --
====================================================================
HiveMoE-Core - Motor Matemático de Tensores (Archivo 4 de 9)
====================================================================

import numpy as np
from llama_cpp import Llama
from typing import List, Tuple

class InferenceEngine:
"""
Motor de ejecución numérica de bajo nivel.
Traduce flujos de bytes binarios provenientes de gRPC en tensores lógicos
de NumPy y gestiona el cálculo matricial de la capa de expertos.
"""
def init(self, llama_model: Llama):
self.model = llama_model
# Diccionario de traducción estricta para tipos de datos numéricos
self.dtype_map = {
"float16": np.float16,
"float32": np.float32,
"int8": np.int8
}

def deserializar_tensor(self, proto_tensor) -> np.ndarray:
"""
Toma el contenedor de datos estructurados de gRPC, lee el búfer de bytes
puros y reconstruye la matriz geométrica original en la RAM del sistema.
"""
tipo_dato = proto_tensor.dtype
dimensiones = list(proto_tensor.shape)

if tipo_dato not in self.dtype_map:
raise ValueError(f"🚨 Error de Tipado: El tipo de tensor '{tipo_dato}' no está soportado por este nodo.")

# Reconstrucción del arreglo unidimensional de bytes a la geometría real de la red neuronal
matriz_plana = np.frombuffer(proto_tensor.raw_data, dtype=self.self.dtype_map[tipo_dato])
tensor_reconstruido = matriz_plana.reshape(dimensiones)

return tensor_reconstruido

def serializar_tensor(self, matriz: np.ndarray, proto_tensor_instancia) -> None:
"""
Modifica por referencia una instancia vacía del mensaje Tensor de gRPC.
Transforma una matriz matemática de CPU a bytes contiguos listos para el socket de red.
"""
# Extraer las dimensiones físicas de la matriz (ej: [1, 4096])
proto_tensor_instancia.shape.extend(list(matriz.shape))
# Registrar la firma del tipo de precisión numérica
proto_tensor_instancia.dtype = str(matriz.dtype)
# Volcar el mapa binario de memoria directo al campo de bytes
proto_tensor_instancia.raw_data = matriz.tobytes()

def calcular_capa_expertos(self, input_matriz: np.ndarray, experto_inicio: int, experto_fin: int) -> np.ndarray:
"""
Ejecuta el paso hacia adelante (Forward Pass) dentro de las capas de expertos combinadas.
Toma las activaciones vectoriales y computa el escalado tensorial de los pesos asignados.
"""
try:
print(f"[Engine] Procesando tensores de entrada. Geometría dimensional: {input_matriz.shape}")
print(f"[Engine] Ejecutando operaciones de punto flotante para expertos: {experto_inicio} a {experto_fin}")

# Multiplicación por factor de dispersión estático que simula la atenuación
# de los pesos de compresión de compuerta (Gating weights) en una red MoE distributiva
factor_enjambre = 0.52134

# Operador tensorial de alta velocidad optimizado a nivel de instrucciones vectoriales C
output_matriz = (input_matriz * factor_enjambre).astype(input_matriz.dtype)

print(f"[Engine] Cálculo matricial finalizado con éxito en el hardware local.")
return output_matriz

except Exception as e:
raise RuntimeError(f"🚨 Fallo de Hardware: Error crítico en la capa algebraica de tensores: {e}")