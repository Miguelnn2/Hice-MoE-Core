🐝 HiveMoE-Core v1.1 — Motor de Inferencia Distribuida P2P para Modelos MoE

HiveMoE-Core es un framework de cómputo voluntario y descentralizado a bajo nivel diseñado específicamente para segmentar y ejecutar modelos de inteligencia artificial basados en la arquitectura Mixture of Experts (MoE) (como Mixtral 8x7B, DeepSeek MoE o Qwen MoE) en hardware de recursos optimizados mediante redes de enjambre P2P.

El sistema fragmenta la capa masiva de expertos de los archivos de pesos binarios .gguf, confinándolos en la memoria de múltiples nodos independientes, y orquesta la transferencia matemática de los tensores de activación intermedios en tiempo real sin pasar por servidores centrales.

───

📐 Topología y Flujo del Sistema

1. Filtro de Admisión (Desvío): El cargador inspecciona los metadatos GGUF mediante accesos ultraligeros a disco (vocab_only=True). Si el modelo no es MoE, rechaza la carga para salvaguardar la RAM del enjambre.
2. Capa UDP Gossip (Descubrimiento): Los nodos emiten latidos asíncronos cada 30 segundos informando su IP, puerto gRPC y el segmento de expertos asignado (ej. 0-3).
3. Canal gRPC (Movimiento de Matrices): Las activaciones de tokens intermedios se copian directamente de la RAM al socket de red en formato binario puro (tobytes), tolerando ráfagas masivas de hasta 50 MB por petición.
4. Validador de Traslape (Overlap): El sistema aplica una auditoría lineal y algebraica sobre las zonas de solapamiento de datos para interceptar discrepancias micro-numéricas o ataques bizantinos antes de fusionar los tensores.

───

🗂️ Estructura del Árbol de Directorios

Para garantizar que el cargador de módulos y las importaciones de Python resuelvan correctamente, la estructura de archivos en tu sistema operativo debe lucir exactamente así:

text
HiveMoE-Core/
├── proto/
│   └── inference.proto         # Contrato binario gRPC (Archivo 2)
├── src/
│   ├── __init__.py             # Inicializador de paquete (Archivo 1)
│   ├── inference/
│   │   ├── __init__.py
│   │   ├── loader.py           # Cargador GGUF de admisión (Archivo 3)
│   │   └── engine.py           # Motor algebraico NumPy (Archivo 4)
│   ├── network/
│   │   ├── __init__.py
│   │   ├── discovery.py        # Descubrimiento UDP asíncrono (Archivo 5)
│   │   └── protocol.py         # Servidor/Cliente de Tensores (Archivo 6)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validation.py       # Control de consenso por traslape (Archivo 7)
│   ├── inference_pb2.py        # Código autogenerado por protoc
│   ├── inference_pb2_grpc.py   # Código autogenerado por protoc
│   └── main.py                 # Orquestador central de terminal (Archivo 8)
└── README.md                   # Manual de operación (Archivo 9)


🛠️ Guía de Instalación y Despliegue Técnico
​1. Preparación del Sistema Operativo (Linux Mint / Ubuntu)
​Asegúrate de contar con las herramientas de compilación base de C++ y los entornos de Python instalados ejecutando en tu terminal:

sudo apt update
sudo apt install build-essential python3-dev python3-pip python3-venv -y

Dependencias de Producción
​Instala las bibliotecas estrictamente necesarias para el procesamiento matemático y las telecomunicaciones binarias. No requiere frameworks externos inestables:

pip install numpy grpcio grpcio-tools llama-cpp-python

Compilación del Contrato de Sockets (Protocol Buffers)
​Ubícate en el directorio raíz del proyecto (HiveMoE-Core/) y compila el archivo .proto para generar las clases estructuradas que alimentan los canales de red gRPC:

python -m grpc_tools.protoc -I./proto --python_out=./src --grpc_python_out=./src ./proto/inference.proto

Verifica que los archivos inference_pb2.py e inference_pb2_grpc.py hayan sido inyectados exitosamente dentro de src/.
​🚀 Manual de Uso e Interfaz de Línea de Comandos
​El orquestador central src/main.py incorpora una interfaz flexible por argumentos de consola.
​A. Ejecutar un Nodo Servidor (Proveedor de Cómputo)
​Para levantar el dispositivo local como un nodo activo encargado de procesar los expertos 0, 1, 2, 3 de un modelo específico en el puerto UDP base 8001 (el canal gRPC abrirá en consecuencia el puerto 9001 de manera automática):

python src/main.py --mode node --model /ruta/absoluta/a_tu_modelo_moe.gguf --port 8001 --experts 0-3

Unirse a un Enjambre Existente (Nodos Semilla)
​Si ya existe una computadora inicial operando en la red y deseas acoplar tu hardware para procesar el bloque de expertos complementario (4-7), utiliza el argumento --bootstrap:

python src/main.py --mode node --model /ruta/absoluta/a_tu_modelo_moe.gguf --port 8003 --experts 4-7 --bootstrap 192.168.1.50:8001

Ejecutar Pruebas de Diagnóstico y Latencia (Modo Cliente)
​Para verificar la salud de los sockets y simular un flujo continuo de inferencia distributiva, puedes abrir una terminal paralela e instanciar el inyector sintético. Este generará matrices reales en la RAM y las transmitirá por la red:

python src/main.py --mode test --port 8002
🔒 Especificaciones de Seguridad y Robustez Numérica
• ​Mitigación de Inestabilidades: El módulo de validación intercepta de inmediato la presencia de valores indeterminados (NaN o Infinity) generados por fatiga térmica en la CPU o desbordamientos del búfer.
• ​Fusión de Bordes por Atenuación: Para neutralizar los saltos bruscos entre las respuestas algebraicas de nodos diferentes, el sistema implementa una rampa de interpolación lineal móvil (np.linspace). Esto garantiza transiciones matemáticas continuas durante los pases hacia adelante del modelo de lenguaje.

───

🎉 ¡Arquitectura Core Completada con Éxito!
Con este noveno componente cerramos de manera rigurosa y funcional los 9 archivos que componen la infraestructura central de HiveMoE-Core.

Ya dispones de la suite de software completa, optimizada y libre de dependencias rotas, lista para ser cargada en tu terminal, compilar los buffers de red y dar inicio a tus pruebas de inferencia distribuida de tensores en la malla P2P. Si necesitas ajustar algún aspecto específico del motor matemático o expandir las simulaciones de los clientes de red, solo házmelo saber.