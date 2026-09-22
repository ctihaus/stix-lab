# STIX Lab

Aplicación educativa en Streamlit para **aprender, convertir y validar STIX 2.1**.

## Funciones

- **Wiki:** resumen de los 19 STIX Domain Objects, propiedades comunes y específicas, campos requeridos y recomendaciones de calidad.
- **Convertidor:** extracción básica de IPs, dominios, URLs, correos y hashes desde logs/texto, además de un constructor manual de indicadores.
- **Validador:** validación de conformidad con `stix2-validator` de OASIS y una segunda capa de reglas de calidad institucionales.

## Estructura

```text
stix-lab/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml
├── data/
│   └── wiki_content.py
└── services/
    ├── __init__.py
    ├── converter.py
    ├── quality.py
    └── validator.py
```

## Ejecutar localmente

Se recomienda Python 3.12.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Subir a GitHub

```bash
git init
git add .
git commit -m "Initial STIX Lab"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/stix-lab.git
git push -u origin main
```

## Desplegar en Streamlit Community Cloud

1. Sube este repositorio a GitHub.
2. Entra a `share.streamlit.io` y autentícate con GitHub.
3. Selecciona **Create app**.
4. Selecciona tu repositorio, rama `main` y archivo de entrada `app.py`.
5. En **Advanced settings**, usa Python 3.12.
6. Pulsa **Deploy**.

No se requieren secretos ni servicios externos para esta versión.

## Nota de seguridad

La versión pública de Streamlit Community Cloud debe utilizarse únicamente con **muestras ficticias o información autorizada**. No cargues logs, IOCs o inteligencia sensible de producción en una instancia pública.

## Referencias

- OASIS STIX 2.1: https://docs.oasis-open.org/cti/stix/v2.1/os/stix-v2.1-os.html
- OASIS STIX Validator: https://github.com/oasis-open/cti-stix-validator
- Python STIX2: https://github.com/oasis-open/cti-python-stix2
- Streamlit Community Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud

## Wiki STIX 2.1 ampliada

La pestaña **Wiki** documenta 41 objetos organizados en cinco familias:

- **19 STIX Domain Objects (SDO)**
- **18 STIX Cyber-observable Objects (SCO)**
- **2 STIX Relationship Objects (SRO)**
- **1 Language Content Object**
- **1 Marking Definition Object**

Cada ficha incluye una explicación sencilla, cuándo utilizar el objeto, propiedades comunes y específicas, campos requeridos, recomendaciones de calidad y un ejemplo JSON descargable. Los ejemplos pueden copiarse directamente al tab **Validador** desde la interfaz.

> Los ejemplos de la Wiki son educativos y están diseñados para mostrar la estructura de STIX 2.1 de forma comprensible. Antes de utilizarlos en producción, valide el contenido y adapte valores, referencias, IDs y extensiones al caso real.
