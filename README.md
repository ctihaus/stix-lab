# STIX Lab

Aplicación educativa desarrollada en **Streamlit** para **aprender, convertir, generar y validar STIX 2.1**, incorporando herramientas de conversión tradicional, construcción manual y análisis asistido por Inteligencia Artificial.

## Funciones

- **Wiki STIX 2.1:** documentación de 41 objetos STIX organizados en cinco familias, con propiedades comunes y específicas, campos requeridos, recomendaciones de calidad y ejemplos JSON.
- **Log → STIX:** extracción básica mediante reglas de IPs, dominios, URLs, correos electrónicos y hashes desde logs o texto.
- **Constructor manual:** creación guiada de indicadores STIX con detección automática del tipo, severidad, confidence, nombre y descripción.
- **AI Converter:** análisis de logs mediante un modelo de lenguaje de pesos abiertos ejecutado en **Cloudflare Workers AI** para identificar y contextualizar indicadores antes de generar STIX.
- **Validador:** validación de conformidad con `stix2-validator` de OASIS y una segunda capa de reglas de calidad institucionales.
- **Control global de uso de IA:** contador persistente diario almacenado en **Cloudflare D1** para limitar la cantidad total de solicitudes realizadas por la aplicación.

## Arquitectura

```text
Usuario
   │
   ▼
Streamlit Community Cloud
   │
   ├── Wiki STIX 2.1
   ├── Log → STIX
   ├── Constructor manual
   ├── Validador STIX
   │
   └── AI Converter
           │
           ▼
     Cloudflare Worker
       │          │
       │          └── Cloudflare D1
       │               └── Contador global diario
       │
       └── Workers AI
            └── Modelo open-weight
```

El modelo de IA **no genera directamente el STIX final**. Su función es analizar el contenido y devolver información estructurada sobre indicadores, severidad, confidence y contexto.

La generación final del objeto STIX se realiza mediante las funciones determinísticas del proyecto, como `make_indicator()` y `make_bundle()`, lo que reduce el riesgo de que el modelo produzca estructuras STIX inválidas.

## Estructura del proyecto

```text
stix-lab/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   ├── wiki_content.py
│   └── ai_sample_log.txt
└── services/
    ├── __init__.py
    ├── converter.py
    ├── ai_converter.py
    ├── quality.py
    └── validator.py
```

### `data/ai_sample_log.txt`

Contiene una muestra extensa de eventos de seguridad utilizada por el **AI Converter**.

Mantener el ejemplo en un archivo separado permite modificar o sustituir la muestra sin agregar bloques extensos de texto dentro de `app.py`.

El archivo puede contener, por ejemplo:

- eventos de firewall;
- DNS;
- proxy;
- EDR;
- correo electrónico;
- hashes;
- URLs defanged;
- dominios;
- IPs internas y externas;
- eventos de correlación SIEM;
- acciones de respuesta.

La aplicación carga este archivo y lo presenta automáticamente como muestra en el campo de entrada del AI Converter.

## Wiki STIX 2.1 ampliada

La pestaña **Wiki** documenta 41 objetos organizados en cinco familias:

- **19 STIX Domain Objects (SDO)**
- **18 STIX Cyber-observable Objects (SCO)**
- **2 STIX Relationship Objects (SRO)**
- **1 Language Content Object**
- **1 Marking Definition Object**

Cada ficha incluye:

- explicación sencilla del objeto;
- cuándo utilizarlo;
- propiedades comunes;
- propiedades específicas;
- propiedades requeridas;
- recomendaciones de calidad;
- ejemplo JSON;
- descarga del ejemplo;
- opción para enviar el ejemplo directamente al **Validador**.

> Los ejemplos de la Wiki son educativos y están diseñados para mostrar la estructura de STIX 2.1 de forma comprensible. Antes de utilizarlos en producción, valide el contenido y adapte valores, referencias, IDs y extensiones al caso real.

## Convertidor STIX

La pestaña **Convertidor** incluye tres modos.

### 1. Log → STIX

Utiliza reglas y expresiones regulares para identificar indicadores presentes directamente en logs o texto.

Actualmente puede detectar:

- IPv4
- IPv6
- dominios
- URLs
- correos electrónicos
- MD5
- SHA-1
- SHA-256
- SHA-512

Los indicadores seleccionados pueden convertirse en un `Bundle` STIX 2.1.

### 2. Constructor manual

Permite construir un indicador manualmente seleccionando el tipo e introduciendo su valor.

El formulario adapta automáticamente:

- nombre;
- descripción;
- placeholder;
- severidad;
- confidence.

También intenta detectar el tipo real del valor introducido y muestra una advertencia cuando no coincide con el tipo seleccionado.

### 3. AI Converter

El **AI Converter** utiliza Cloudflare Workers AI para interpretar logs y eventos de seguridad con mayor contexto que una extracción basada únicamente en expresiones regulares.

El flujo es:

```text
Log
 ↓
Cloudflare Worker
 ↓
Workers AI
 ↓
Extracción estructurada
 ↓
Validación local del indicador
 ↓
Generación determinística de STIX
 ↓
Validador
```

El modelo puede devolver:

- resumen del evento;
- severidad sugerida;
- confidence;
- indicadores encontrados;
- tipo de cada indicador;
- descripción contextual.

Los tipos de indicadores admitidos actualmente son:

- IPv4
- IPv6
- Domain
- URL
- Email
- MD5
- SHA-1
- SHA-256
- SHA-512

Antes de generar el STIX final, la aplicación utiliza `detect_indicator()` para comprobar nuevamente los indicadores propuestos por la IA.

Esto permite detectar discrepancias entre el tipo sugerido por el modelo y el tipo determinado mediante reglas.

## Límite global diario de IA

El uso del AI Converter se controla mediante un contador global almacenado en **Cloudflare D1**.

La aplicación muestra:

- solicitudes utilizadas;
- solicitudes restantes;
- límite diario;
- barra de progreso.

Ejemplo:

```text
Solicitudes utilizadas: 37
Solicitudes restantes: 63
Límite diario: 100
```

El límite se aplica globalmente a todos los usuarios de la aplicación.

El valor puede configurarse en el Cloudflare Worker mediante la variable:

```text
DAILY_LIMIT
```

Por ejemplo:

```text
DAILY_LIMIT = 100
```

### Reinicio diario

No se utiliza una tarea programada para reiniciar el contador.

La tabla utiliza la fecha UTC como clave:

```text
2026-10-22
2026-10-23
2026-10-24
```

Cuando comienza un nuevo día, el Worker crea automáticamente una nueva fila con contador `0`.

Esto también permite conservar un historial básico del uso diario.

## Cloudflare D1

Crear una base de datos D1, por ejemplo:

```text
stix-ai-usage
```

Crear la tabla:

```sql
CREATE TABLE IF NOT EXISTS ai_daily_usage (
    usage_date TEXT PRIMARY KEY,
    requests INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

En el Cloudflare Worker debe existir un binding D1 con:

```text
Variable name: DB
Database: stix-ai-usage
```

## Cloudflare Workers AI

El backend de IA se ejecuta en un **Cloudflare Worker**.

El Worker se encarga de:

1. autenticar las solicitudes provenientes de STIX Lab;
2. consultar el uso diario en D1;
3. verificar si quedan solicitudes disponibles;
4. reservar una solicitud;
5. ejecutar Workers AI;
6. devolver el resultado estructurado;
7. actualizar el contador global.

Se recomienda mantener el modelo configurable mediante una variable del Worker:

```text
AI_MODEL
```

Ejemplo:

```text
@cf/meta/llama-3.1-8b-instruct-fast
```

> La disponibilidad y los identificadores de modelos de Workers AI pueden cambiar. Consulte siempre el catálogo oficial de Cloudflare antes de desplegar o actualizar el Worker.

El Worker debe tener un binding de Workers AI con:

```text
Variable name: AI
```

## Protección del Worker

El endpoint de IA no debe quedar abierto sin autenticación.

El Worker utiliza un secreto compartido:

```text
API_SHARED_SECRET
```

Streamlit lo envía mediante el header:

```text
X-STIXLAB-KEY
```

Esto evita que terceros utilicen directamente el endpoint y consuman la cuota asignada al AI Converter.

## Configuración de Streamlit Secrets

En Streamlit Community Cloud, configure:

```toml
AI_WORKER_URL = "https://stix-ai-api.TU_SUBDOMINIO.workers.dev"
AI_WORKER_SECRET = "TU_SECRETO_COMPARTIDO"
```

No almacene estos valores directamente en `app.py` ni los publique en GitHub.

## Variables del Cloudflare Worker

Configuración recomendada:

```text
AI_MODEL=@cf/meta/llama-3.1-8b-instruct-fast
DAILY_LIMIT=100
```

Secret:

```text
API_SHARED_SECRET=valor-secreto
```

Bindings:

```text
AI = Workers AI
DB = D1 database
```

## Límites de entrada

El AI Converter limita el tamaño de los logs enviados al modelo.

El valor configurado en `app.py` debe coincidir con el valor configurado en el Cloudflare Worker.

Ejemplo:

```python
MAX_AI_LOG_CHARS = 12000
```

Worker:

```javascript
const MAX_LOG_LENGTH = 12000;
```

Mantener ambos valores sincronizados evita que Streamlit permita entradas que posteriormente sean rechazadas por el backend.

## Validación STIX

La pestaña **Validador** ejecuta dos capas de validación.

### Conformidad STIX

Comprueba:

- JSON válido;
- conformidad STIX 2.1;
- errores del validador;
- advertencias del validador.

### Calidad del reporte

Aplica reglas adicionales del proyecto, incluyendo comprobaciones relacionadas con:

- severidad;
- `name`;
- `description`;
- `confidence`, cuando está presente;
- propiedades y valores esperados por las reglas institucionales.

Los resultados se agrupan por regla para evitar mostrar un mensaje independiente por cada objeto afectado.

## Requisitos

Se recomienda:

```text
Python 3.12
```

Dependencias principales:

```text
streamlit
stix2
stix2-validator
requests
```

Instale las versiones definidas actualmente en `requirements.txt`.

## Ejecutar localmente

Crear el entorno:

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux/macOS

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Para utilizar el AI Converter localmente, cree:

```text
.streamlit/secrets.toml
```

con:

```toml
AI_WORKER_URL = "https://stix-ai-api.TU_SUBDOMINIO.workers.dev"
AI_WORKER_SECRET = "TU_SECRETO_COMPARTIDO"
```

No incluya este archivo en GitHub.

## Subir a GitHub

```bash
git init
git add .
git commit -m "Update STIX Lab with AI Converter"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/stix-lab.git
git push -u origin main
```

Para actualizaciones posteriores:

```bash
git add .
git commit -m "Update STIX Lab"
git push
```

## Desplegar en Streamlit Community Cloud

1. Suba el repositorio a GitHub.
2. Entre a `share.streamlit.io` y autentíquese con GitHub.
3. Seleccione **Create app**.
4. Seleccione el repositorio.
5. Seleccione la rama `main`.
6. Seleccione `app.py` como archivo de entrada.
7. Configure Python 3.12.
8. Agregue los secretos del AI Converter.
9. Despliegue la aplicación.

Secrets requeridos:

```toml
AI_WORKER_URL = "https://stix-ai-api.TU_SUBDOMINIO.workers.dev"
AI_WORKER_SECRET = "TU_SECRETO_COMPARTIDO"
```

## Seguridad y privacidad

La versión pública de Streamlit Community Cloud debe utilizarse únicamente con **muestras ficticias, sanitizadas o información autorizada**.

No cargue en una instancia pública:

- credenciales;
- datos personales sensibles;
- secretos;
- logs confidenciales;
- inteligencia clasificada;
- información de producción que no esté autorizada para salir de la organización.

El AI Converter envía el contenido introducido al backend de Cloudflare para procesarlo mediante Workers AI.

Antes de utilizar datos reales, revise las políticas internas de manejo de información y la clasificación aplicable.

## Consideraciones sobre Inteligencia Artificial

La salida del modelo debe considerarse una **asistencia al análisis**, no una fuente de verdad.

El modelo puede:

- interpretar incorrectamente contexto;
- clasificar erróneamente un indicador;
- asignar una severidad diferente a la esperada;
- omitir indicadores;
- generar descripciones imprecisas.

Por este motivo, STIX Lab mantiene la generación final de STIX fuera del modelo y realiza comprobaciones adicionales mediante código determinístico.

El resultado debe ser revisado por un analista antes de utilizarse como inteligencia de producción.

## Referencias

- OASIS STIX 2.1: https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html
- OASIS STIX Validator: https://github.com/oasis-open/cti-stix-validator
- Python STIX2: https://github.com/oasis-open/cti-python-stix2
- Streamlit Community Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Cloudflare Workers AI: https://developers.cloudflare.com/workers-ai/
- Cloudflare Workers AI Model Catalog: https://developers.cloudflare.com/workers-ai/models/
- Cloudflare D1: https://developers.cloudflare.com/d1/

## Propósito

STIX Lab es una herramienta educativa orientada a facilitar el aprendizaje práctico de STIX 2.1 mediante el flujo:

```text
Aprender
   ↓
Identificar
   ↓
Convertir
   ↓
Construir
   ↓
Validar
   ↓
Compartir
```

El objetivo es ayudar a los participantes a comprender cómo transformar datos técnicos y eventos de ciberseguridad en inteligencia estructurada, consistente y validable mediante STIX 2.1.
