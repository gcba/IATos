# Tos.IA API

## Introducción

TBD

## Capas del Proyecto

Para satisfacer los requerimientos de los distintos equipos involucrados en el proyecto, este repositorio plantea una organizacion en "capas". Cada capa provee un nivel de especificidad distinto, permitiendo a cada desarrollador consumir directamente la capa que mejor responda a la ejecución de su disciplina.

- `algos`: contiene algoritmos independientes que resuelvan dominios particulares y acotados (eg: segmentacion, normalización, clasificación, etc). Los desarrolladores pueden utilizar esta capa para desarrollar u optimizar procesos  de forma aislada.
- `runtime`: capa encargada de integrar los distintas algoritmos involucrados en la ejecucion de una solicitud de diagnóstico particular. Depende exclusivamente de la capa de `algos`. Es agnóstica del consumidor (o canal) que solicita la ejecucíon. Los desarrolladores pueden utilizar esta capa para procesos de entrenamiento, testing o ejecución de forma programática.
- `server`: capa encarga de traducir llamadas realizadas a traves al API REST en instancias de ejecución del pipeline de diagnóstico. Depende exclusivamente de la capa de `runtime`. Esta capa es la que se disponibiliza en la infraestructura del entorno productivo, no está pensada para ser consumida directamente por el equipo de desarrollo.

## Estructura del proyecto

```
.
├── .devcontainer/
│   └── Configuration del VSCode dev container.
├── models/
│   └── Archivos con los pesos de las redes ya entrenadas.
├── samples/
│   └── Muestras de audio para testear el pipeline.
├── algos/
│   └── Los distintos algoritmo involucrados en el proceso de inferencia.
├── runtime/
│   └── Paquete python encargado conectar las distintas etapas del proceso.
├── server/
│   └── Paquete python encargado de exponer los endpoints http.
├── tests/
│   └── testing.
├── requirements.txt --> Dependencias de python
├── Dockerfile       --> Definicion de la imagen del build para utilizar durante runtime
├── Makefile         --> Comandos
├── README.md        --> Documentacion
├── pytest.ini       --> .ini para pytest
├── config.yml       --> Contiene los valores de los parametros del pipeline 
└── example.py       --> Ejemplo de como ejecutar el runtime de inferencia programaticamente
```

## Entorno de Desarrollo

Se recomiendo utilizar VSCode como IDE de trabajo. El repositorio esta preparado para utilizar la funcionalidad de [dev container](https://code.visualstudio.com/docs/remote/containers), la cual permite levantar un entorno de desarrollo dentro de un container de docker, donde ya se encuentran instaladas las dependencias del proyecto. La especificación del container se encuentra en la carpeta `.devcontainer`. 

## Ejecucion Prográmatica del Pipeline

El siguiente ejemplo explica como ejecutar el proceso completo de inferencia en esta etapa inicial de desarrollo. Este mecanismo puede ser utilizado como punto de partida para adaptar el proceso de entrenamiento de la red a partir de audios "crudos" (sin procesamiento previo).


```python
# importamos los puntos de entrada del paquete de runtime
from runtime import load_config, execute, WorkUnit

# cargamos la configuracion desde el archivo yaml
segmentation_params, mel_spec_params, colos_spec_params = load_config()

# instanciamos la unidad de trabajo que define, de forma autónoma, todos los parametros requeridos para ejecutar una solicitud de diagnostico particular
work = WorkUnit(
    source_file = 'samples/preprocessing/benchmark_1/raw.ogg',
    segmentation_params = segmentation_params,
    mel_spec_params = mel_spec_params,
    color_spec_params = colos_spec_params,
)

# ejecutamos el pipeline completo, pasando la unidad de trabajo como unico argumento requerido
execute(work)
```

El archivo `example.py` permite correr de forma directa el ejemplo detallado anteriormente.

## Ejecución del Servidor API

El servidor web que responde a las consultas de inferencia se inicializa corriendo el siguente comando:

```sh
python -m server
```

Es necesario que las siguiente variables de entorno esten definidas:

- `API_KEY`: valor que sera requerido para autenticar llamadas externas
- `BLOB_CONNECTION`: connection string al Storage Account de Azure donde se almacenan los audios de las llamadas
- `BLOB_CONTAINER`: nombre del container dentro del Storage Account donde se almacenann los audios de las llamadas
- `COSMO_ENDPOINT`: endpoint de la base de CosmoDB donde se registran los datos de las llamadas
- `COSMO_KEY`: key de autenticación a la base de CosmoDB donde se registran los datos de las llamadas.

## CI Pipeline

El proyecto posee un pipeline de integracion continua utilizando infraestructura de Azure. El repositorio git conectado al pipeline es el siguiente:

```
https://tosiadev@dev.azure.com/tosiadev/api/_git/api
```

Un _push_ a la rama `master` de dicho repositorio dispara el pipeline. El mismo consiste en ejecutar el build de la imagen de docker a partir del `Dockerfile` que se encuentra en la raiz del repo.

A la imagen resultante se le aplica el tag correspondiente el "build number" (numero entero secuencial que se incrementa con cada ejecución del pipeline) y se envia al siguiente _docker registry_ en Azure:

```
tosia.azurecr.io
```

Todos los recursos asociados con el pipeline de integración pueden ser configurados desde la sección de "Dev Space" en la cuenta de Azure.

## Deployment

El entorno de ejeución se encuentra en un cluster de Kuberentes corriendo mediante el servicio AKS de Azure. El nombre del cluster es `tosia`.

Para ejecutar el proceso de deployment, es necesario poder acceder via CLI utilizando `kubectl`. Los datos necesarios para acceder al cluster se encuentran detalladas en la consola web de Azure para dicho cluster.

Los recursos de Kuberentes requeridos para el proyecto se encuentran definidos en los archivo yaml dentro de la carpet `provision`.

Los pasos para realizar el deployment son los siguientes:

1. Realizar el push a master y esperar a que la nueva imagen este disponible en el registry (utilizar la consola web de Dev Spaces para visualizar el estado)
2. Asegurarse que las variables de entorno detalladas en el seccion [Ejecución del Servidor API](#Ejecucion_del_Servidor_API) se encuentran inicializadas con los valores correctos en la sesión de _shell_ local desde donde se realizara el deployment.
3. Exportar la variable de entorno `BUILD_NUMBER` asignandole el valor del número de build (tag de la imagen de docker asignado por el build pipeline) que se desea correr.
4. Correr el comando `cd provision && make all`