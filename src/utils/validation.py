-- coding: utf-8 --
====================================================================
HiveMoE-Core - Validador de Consenso por Traslape (Archivo 7 de 9)
====================================================================

import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HiveValidation")

class TensorValidator:
"""
Clase encargada de auditar la consistencia analítica de las matrices
calculadas por nodos remotos a través de zonas de solapamiento matemático.
"""
def init(self, tolerancia_absoluta: float = 1e-4, tolerancia_relativa: float = 1e-3):
# Umbrales estrictos de error admisibles para operaciones de precisión float16/float32
self.atol = tolerancia_absoluta
self.rtol = tolerancia_relativa

def verificar_sanidad_basica(self, matriz: np.ndarray) -> bool:
"""
Primer filtro de consistencia: Examina el bloque de memoria para asegurar
que no contenga valores rotos o indeterminados que envenenen la red neuronal.
"""
if not isinstance(matriz, np.ndarray):
logger.error("[Validación] Error: El objeto evaluado no corresponde a una estructura física de NumPy.")
return False

if np.isnan(matriz).any():
logger.error("[Validación] Alerta de Inestabilidad: Se detectaron valores indefinidos (NaN) en los tensores.")
return False

if np.isinf(matriz).any():
logger.error("[Validación] Alerta de Inestabilidad: Se detectaron desbordamientos numéricos (Infinity).")
return False

return True

def verificar_consenso_traslape(self, tensor_a: np.ndarray, tensor_b: np.ndarray, tamano_traslape: int) -> bool:
"""
Inspecciona y compara las fronteras colindantes de dos respuestas de red.
Garantiza que el final del cálculo de un nodo encaje geométricamente con el inicio del siguiente.

:param tensor_a: Matriz de activación devuelta por el Nodo A [Tokens, Dimensiones]
:param tensor_b: Matriz de activación devuelta por el Nodo B [Tokens, Dimensiones]
:param tamano_traslape: Cantidad de filas redundantes configuradas para la auditoría
"""
if not self.verificar_sanidad_basica(tensor_a) or not self.verificar_sanidad_basica(tensor_b):
return False

# Verificar concordancia espacial de los canales ocultos del modelo (hidden_size)
if tensor_a.shape[1] != tensor_b.shape[1]:
logger.error(f"[Validación] Rechazado: Desalineación geométrica de canales. A={tensor_a.shape[1]}, B={tensor_b.shape[1]}")
return False

# Prevenir desbordamientos si el tamaño asignado de ventana supera el bloque de datos
if tensor_a.shape[0] < tamano_traslape or tensor_b.shape[0] < tamano_traslape:
logger.error("[Validación] Rechazado: La ventana de solapamiento es mayor que la longitud del tensor.")
return False

# Aislar las porciones idénticas que debieron procesar ambos nodos
corte_final_a = tensor_a[-tamano_traslape:]
corte_inicial_b = tensor_b[:tamano_traslape]

# Calcular la métrica de desviación de punto flotante real en el hardware
desviacion_maxima = np.max(np.abs(corte_final_a - corte_inicial_b))

# Comparación vectorial de proximidad bajo norma estándar
consenso_valido = np.allclose(corte_final_a, corte_inicial_b, rtol=self.rtol, atol=self.atol)

if consenso_valido:
logger.info(f"[Validación] Consenso Aprobado. Desviación estructural máxima controlada: {desviacion_maxima:.6f}")
return True
else:
logger.error(f"[Validación] CRÍTICO: ¡Discordancia de cómputo detectada! Desviación excesiva: {desviacion_maxima:.6f}")
return False

def fusionar_tensores_traslapados(self, tensor_a: np.ndarray, tensor_b: np.ndarray, tamano_traslape: int) -> np.ndarray:
"""
Une los dos bloques validados en una sola matriz unificada, aplicando una rampa
de atenuación lineal sobre el área de solapamiento para mitigar ruidos de truncamiento.
"""
if tensor_a.shape[1] != tensor_b.shape[1]:
raise ValueError("Incompatibilidad geométrica insalvable entre matrices a fusionar.")

# Segmentar las zonas exclusivas no compartidas
nucleo_limpio_a = tensor_a[:-tamano_traslape]
nucleo_limpio_b = tensor_b[tamano_traslape:]

# Segmentar las zonas compartidas coincidentes
corte_a = tensor_a[-tamano_traslape:]
corte_b = tensor_b[:tamano_traslape]

# Generar vector interpolador balanceado [tamano_traslape, 1]
rampa_interpolacion = np.linspace(0.0, 1.0, num=tamano_traslape, dtype=tensor_a.dtype).reshape(-1, 1)

# Fusión ponderada: Transición suave del flujo del Nodo A hacia el Nodo B
interseccion_suavizada = (corte_a * (1.0 - rampa_interpolacion)) + (corte_b * rampa_interpolacion)

# Ensamble de los bloques de memoria en un único tensor contiguo en RAM
tensor_unificado = np.vstack([nucleo_limpio_a, interseccion_suavizada, nucleo_limpio_b])
return tensor_unificado