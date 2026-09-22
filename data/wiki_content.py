"""Contenido educativo de la Wiki STIX 2.1.

Los ejemplos son deliberadamente pequeños: muestran la forma típica del objeto sin
pretender cubrir todas las combinaciones permitidas por el estándar.
"""

COMMON_PROPERTIES_BY_FAMILY = {
    "SDO": [
        ("type", "string", "Tipo del objeto STIX."),
        ("spec_version", "string", "Versión de STIX; en esta Wiki se usa 2.1."),
        ("id", "identifier", "Identificador único con formato tipo--UUID."),
        ("created", "timestamp", "Fecha y hora de creación."),
        ("modified", "timestamp", "Fecha y hora de última modificación."),
        ("created_by_ref", "identifier", "Identidad que creó el objeto."),
        ("revoked", "boolean", "Indica si el objeto fue revocado."),
        ("labels", "list[string]", "Etiquetas libres para clasificar el contenido."),
        ("confidence", "integer", "Nivel de confianza entre 0 y 100."),
        ("lang", "string", "Idioma principal del contenido textual."),
        ("external_references", "list", "Referencias externas relacionadas."),
        ("object_marking_refs", "list[identifier]", "Marcas de manejo aplicadas al objeto."),
        ("granular_markings", "list", "Marcas aplicadas a propiedades específicas."),
        ("extensions", "dictionary", "Extensiones STIX aplicadas al objeto."),
    ],
    "SCO": [
        ("type", "string", "Tipo del Cyber-observable."),
        ("spec_version", "string", "Versión de STIX; normalmente 2.1."),
        ("id", "identifier", "Identificador del observable; en STIX 2.1 suele derivarse de propiedades contribuyentes al ID."),
        ("object_marking_refs", "list[identifier]", "Marcas de manejo aplicadas al observable."),
        ("granular_markings", "list", "Marcas aplicadas a propiedades específicas."),
        ("defanged", "boolean", "Indica si los valores fueron modificados para impedir uso accidental."),
        ("extensions", "dictionary", "Extensiones del Cyber-observable."),
    ],
    "SRO": [
        ("type", "string", "Tipo de relación STIX."),
        ("spec_version", "string", "Versión de STIX."),
        ("id", "identifier", "Identificador único de la relación."),
        ("created", "timestamp", "Fecha y hora de creación."),
        ("modified", "timestamp", "Fecha y hora de modificación."),
        ("created_by_ref", "identifier", "Identidad que creó la relación."),
        ("confidence", "integer", "Confianza entre 0 y 100."),
        ("external_references", "list", "Referencias externas relacionadas."),
        ("object_marking_refs", "list[identifier]", "Marcas de manejo aplicadas."),
        ("granular_markings", "list", "Marcas aplicadas a propiedades específicas."),
        ("extensions", "dictionary", "Extensiones STIX."),
    ],
    "Language Content Object": [
        ("type", "string", "Debe ser language-content."),
        ("spec_version", "string", "Versión de STIX."),
        ("id", "identifier", "Identificador único."),
        ("created", "timestamp", "Fecha y hora de creación."),
        ("modified", "timestamp", "Fecha y hora de modificación."),
        ("created_by_ref", "identifier", "Identidad que creó el objeto."),
        ("object_marking_refs", "list[identifier]", "Marcas de manejo aplicadas."),
    ],
    "Marking Definition Object": [
        ("type", "string", "Debe ser marking-definition."),
        ("spec_version", "string", "Versión de STIX."),
        ("id", "identifier", "Identificador de la definición de marcado."),
        ("created", "timestamp", "Fecha y hora de creación; estos objetos no se versionan."),
        ("created_by_ref", "identifier", "Identidad que creó la definición."),
        ("object_marking_refs", "list[identifier]", "Marcas adicionales aplicadas."),
    ],
}

# Compatibilidad con versiones anteriores de app.py
COMMON_PROPERTIES = COMMON_PROPERTIES_BY_FAMILY["SDO"]


def _sdo(type_name, uid, name=None, **extra):
    obj = {
        "type": type_name,
        "spec_version": "2.1",
        "id": f"{type_name}--{uid}",
        "created": "2026-09-22T12:00:00.000Z",
        "modified": "2026-09-22T12:00:00.000Z",
    }
    if name is not None:
        obj["name"] = name
    obj.update(extra)
    return obj


def _sco(type_name, uid, **extra):
    obj = {"type": type_name, "spec_version": "2.1", "id": f"{type_name}--{uid}"}
    obj.update(extra)
    return obj


def _sro(type_name, uid, **extra):
    obj = {
        "type": type_name,
        "spec_version": "2.1",
        "id": f"{type_name}--{uid}",
        "created": "2026-09-22T12:00:00.000Z",
        "modified": "2026-09-22T12:00:00.000Z",
    }
    obj.update(extra)
    return obj


CATEGORIES = [
    "STIX Domain Objects (SDO)",
    "STIX Cyber-observable Objects (SCO)",
    "STIX Relationship Objects (SRO)",
    "Language Content Objects",
    "Marking Definition Objects",
]

WIKI_OBJECTS = {
    # ------------------------------------------------------------------ SDO
    "Attack Pattern": {
        "category": CATEGORIES[0], "family": "SDO", "type": "attack-pattern",
        "summary": "Describe una técnica, comportamiento o patrón utilizado para comprometer sistemas.",
        "use": "Úsalo cuando necesites representar un patrón de ataque identificado o referenciado.",
        "properties": [("name","string","Nombre del patrón."),("description","string","Descripción y contexto."),("aliases","list[string]","Nombres alternativos."),("kill_chain_phases","list","Fases de kill chain relacionadas.")],
        "required": ["type","spec_version","id","created","modified","name"],
        "recommended": ["description","external_references"],
        "example": _sdo("attack-pattern","0c7b5b88-8ff7-4a4d-8c1d-4d38e21d5101","Acceso mediante credenciales válidas",description="Uso de credenciales legítimas para acceder a recursos."),
    },
    "Campaign": {
        "category": CATEGORIES[0], "family": "SDO", "type": "campaign",
        "summary": "Agrupa actividad maliciosa coordinada durante un periodo y con un objetivo común.",
        "use": "Úsalo para describir una campaña de actividad relacionada, no un evento aislado.",
        "properties": [("name","string","Nombre de la campaña."),("description","string","Descripción."),("aliases","list[string]","Alias."),("first_seen","timestamp","Primera vez observada."),("last_seen","timestamp","Última vez observada."),("objective","string","Objetivo de la campaña.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description","first_seen","last_seen"],
        "example": _sdo("campaign","12a111f0-b824-4baf-a224-83b80237a094","Campaña de phishing financiero",description="Actividad coordinada contra usuarios del sector financiero.",first_seen="2026-09-01T00:00:00Z",last_seen="2026-09-20T23:59:59Z"),
    },
    "Course of Action": {
        "category": CATEGORIES[0], "family": "SDO", "type": "course-of-action",
        "summary": "Representa una acción recomendada para prevenir, mitigar o responder a una amenaza.",
        "use": "Úsalo para documentar una medida defensiva o de respuesta.",
        "properties": [("name","string","Nombre de la acción."),("description","string","Descripción de la acción.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description"],
        "example": _sdo("course-of-action","3a345e3a-b1e6-4f3d-9d0d-f52d2d4ec101","Bloquear dominio",description="Bloquear el dominio malicioso en los controles perimetrales y DNS."),
    },
    "Grouping": {
        "category": CATEGORIES[0], "family": "SDO", "type": "grouping",
        "summary": "Agrupa objetos STIX relacionados sin afirmar una relación semántica específica entre ellos.",
        "use": "Úsalo cuando quieras entregar un conjunto de objetos como una colección contextual.",
        "properties": [("name","string","Nombre opcional."),("description","string","Descripción."),("context","open-vocab","Contexto del agrupamiento."),("object_refs","list[identifier]","Objetos agrupados.")],
        "required": ["type","spec_version","id","created","modified","context","object_refs"], "recommended": ["name","description"],
        "example": _sdo("grouping","2f9a1bd0-f7a2-4a3f-b819-9bd8ca3fa101","Indicadores observados",context="suspicious-activity",object_refs=["indicator--11111111-1111-4111-8111-111111111111"]),
    },
    "Identity": {
        "category": CATEGORIES[0], "family": "SDO", "type": "identity",
        "summary": "Representa una persona, organización, grupo, clase o sistema identificable.",
        "use": "Úsalo para identificar quién produce la inteligencia o una entidad mencionada en ella.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("roles","list[string]","Roles."),("identity_class","open-vocab","Clase de identidad."),("sectors","list[open-vocab]","Sectores."),("contact_information","string","Información de contacto.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["identity_class","description"],
        "example": _sdo("identity","f431f809-377b-45e0-aa1c-6a4751cae5ff","Entidad Financiera Ejemplo",identity_class="organization",sectors=["financial-services"]),
    },
    "Incident": {
        "category": CATEGORIES[0], "family": "SDO", "type": "incident",
        "summary": "Representa un incidente de ciberseguridad de alto nivel. En STIX 2.1 es un objeto básico (stub).",
        "use": "Úsalo como referencia de un incidente; para metadatos más ricos puede requerir extensiones.",
        "properties": [("name","string","Nombre del incidente."),("description","string","Descripción y contexto.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description"],
        "example": _sdo("incident","8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f","Incidente de acceso no autorizado",description="Acceso detectado en un sistema crítico."),
    },
    "Indicator": {
        "category": CATEGORIES[0], "family": "SDO", "type": "indicator",
        "summary": "Representa un patrón que puede utilizarse para detectar actividad sospechosa o maliciosa.",
        "use": "Úsalo para expresar algo que pueda buscarse o detectarse: IP, dominio, URL, hash u otro patrón.",
        "properties": [("name","string","Nombre legible."),("description","string","Descripción."),("indicator_types","list[open-vocab]","Clasificación."),("pattern","string","Patrón de detección."),("pattern_type","open-vocab","Lenguaje del patrón."),("pattern_version","string","Versión del lenguaje."),("valid_from","timestamp","Inicio de validez."),("valid_until","timestamp","Fin de validez."),("kill_chain_phases","list","Fases relacionadas.")],
        "required": ["type","spec_version","id","created","modified","pattern","pattern_type","valid_from"], "recommended": ["name","description","confidence","labels / x_severity"],
        "example": _sdo("indicator","11111111-1111-4111-8111-111111111111","Dominio malicioso",description="Dominio identificado durante monitoreo de tráfico.",pattern="[domain-name:value = 'malicious-example.com']",pattern_type="stix",valid_from="2026-09-22T12:00:00.000Z",confidence=70,labels=["severity:medium"]),
    },
    "Infrastructure": {
        "category": CATEGORIES[0], "family": "SDO", "type": "infrastructure",
        "summary": "Describe recursos de infraestructura utilizados para soportar actividad cibernética.",
        "use": "Úsalo para servidores, hosting, botnets, C2, redes u otra infraestructura relevante.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("infrastructure_types","list[open-vocab]","Tipos."),("aliases","list[string]","Alias."),("kill_chain_phases","list","Fases."),("first_seen","timestamp","Primera vez."),("last_seen","timestamp","Última vez.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description","infrastructure_types"],
        "example": _sdo("infrastructure","38c47d93-d984-4fd9-b87b-d69d0841628d","Servidor de comando y control",infrastructure_types=["command-and-control"],description="Infraestructura observada comunicándose con endpoints comprometidos."),
    },
    "Intrusion Set": {
        "category": CATEGORIES[0], "family": "SDO", "type": "intrusion-set",
        "summary": "Agrupa comportamientos y recursos maliciosos que se cree pertenecen a un mismo conjunto de actividad.",
        "use": "Úsalo cuando varias actividades puedan atribuirse al mismo conjunto operativo.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("aliases","list[string]","Alias."),("first_seen","timestamp","Primera vez."),("last_seen","timestamp","Última vez."),("goals","list[string]","Objetivos."),("resource_level","open-vocab","Nivel de recursos."),("primary_motivation","open-vocab","Motivación principal."),("secondary_motivations","list[open-vocab]","Motivaciones secundarias.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description","aliases"],
        "example": _sdo("intrusion-set","4cebd2df-83c0-4f9d-b4c1-94d5f2ac2101","Grupo de intrusión ejemplo",description="Conjunto de actividad persistente observado en múltiples campañas.",goals=["Fraude financiero"]),
    },
    "Location": {
        "category": CATEGORIES[0], "family": "SDO", "type": "location",
        "summary": "Representa una ubicación geográfica física.",
        "use": "Úsalo para país, región, ciudad o coordenadas asociadas a inteligencia.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("latitude","float","Latitud."),("longitude","float","Longitud."),("precision","float","Precisión en metros."),("region","open-vocab","Región."),("country","string","Código de país."),("administrative_area","string","Área administrativa."),("city","string","Ciudad."),("street_address","string","Dirección."),("postal_code","string","Código postal.")],
        "required": ["type","spec_version","id","created","modified"], "recommended": ["name","country","city"],
        "example": _sdo("location","7f7d0f4e-87d2-45d7-9f67-e0b2a19ce101","Santo Domingo",country="DO",city="Santo Domingo"),
    },
    "Malware": {
        "category": CATEGORIES[0], "family": "SDO", "type": "malware",
        "summary": "Describe software o código malicioso, incluyendo familias y muestras.",
        "use": "Úsalo para representar malware identificado o una familia asociada a la información reportada.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("malware_types","list[open-vocab]","Tipos."),("is_family","boolean","Indica si es una familia."),("aliases","list[string]","Alias."),("kill_chain_phases","list","Fases."),("first_seen","timestamp","Primera vez."),("last_seen","timestamp","Última vez."),("operating_system_refs","list[identifier]","Sistemas operativos."),("architecture_execution_envs","list[open-vocab]","Arquitecturas."),("implementation_languages","list[open-vocab]","Lenguajes."),("capabilities","list[open-vocab]","Capacidades."),("sample_refs","list[identifier]","Muestras.")],
        "required": ["type","spec_version","id","created","modified","is_family"], "recommended": ["name","description","malware_types"],
        "example": _sdo("malware","31b940d4-6f7f-459a-80ea-9c1f17b5891b","Malware Ejemplo",is_family=True,malware_types=["ransomware"],description="Familia ficticia utilizada para fines educativos."),
    },
    "Malware Analysis": {
        "category": CATEGORIES[0], "family": "SDO", "type": "malware-analysis",
        "summary": "Captura metadatos y resultados de un análisis de malware.",
        "use": "Úsalo para documentar una ejecución o análisis estático/dinámico de una muestra.",
        "properties": [("product","string","Producto de análisis."),("version","string","Versión."),("host_vm_ref","identifier","VM utilizada."),("operating_system_ref","identifier","Sistema operativo."),("installed_software_refs","list[identifier]","Software instalado."),("configuration_version","string","Versión de configuración."),("modules","list[string]","Módulos."),("analysis_engine_version","string","Versión del motor."),("analysis_definition_version","string","Versión de definición."),("submitted","timestamp","Fecha de envío."),("analysis_started","timestamp","Inicio."),("analysis_ended","timestamp","Fin."),("result_name","string","Nombre del resultado."),("result","open-vocab","Resultado."),("analysis_sco_refs","list[identifier]","SCO obtenidos.")],
        "required": ["type","spec_version","id","created","modified","product","version"], "recommended": ["result","analysis_sco_refs"],
        "example": _sdo("malware-analysis","f2e48c60-7e3f-4d8a-a0f6-c64b4a2ce101",product="Sandbox Ejemplo",version="1.0",result="malicious",analysis_sco_refs=["file--7cce6789-89ab-5def-8123-456789abcdef"]),
    },
    "Note": {
        "category": CATEGORIES[0], "family": "SDO", "type": "note",
        "summary": "Añade comentarios o contexto textual a uno o más objetos STIX.",
        "use": "Úsalo para agregar observaciones del analista sin modificar los objetos originales.",
        "properties": [("abstract","string","Resumen corto."),("content","string","Contenido de la nota."),("authors","list[string]","Autores."),("object_refs","list[identifier]","Objetos a los que aplica.")],
        "required": ["type","spec_version","id","created","modified","content","object_refs"], "recommended": ["abstract","authors"],
        "example": _sdo("note","d0f3cb20-3f12-4dd4-82ea-3a7611982101",abstract="Contexto adicional",content="El indicador fue observado en múltiples fuentes internas.",authors=["Analista CTI"],object_refs=["indicator--11111111-1111-4111-8111-111111111111"]),
    },
    "Observed Data": {
        "category": CATEGORIES[0], "family": "SDO", "type": "observed-data",
        "summary": "Representa hechos observados directamente durante una ventana de tiempo.",
        "use": "Úsalo para documentar que uno o más SCO fueron realmente observados.",
        "properties": [("first_observed","timestamp","Primera observación."),("last_observed","timestamp","Última observación."),("number_observed","integer","Número de observaciones."),("object_refs","list[identifier]","Cyber-observables observados."),("objects","dictionary","Representación embebida heredada de STIX 2.0; deprecada en 2.1.")],
        "required": ["type","spec_version","id","created","modified","first_observed","last_observed","number_observed"], "recommended": ["object_refs"],
        "example": _sdo("observed-data","b67d30ff-02ac-498a-92f9-32f845f448cf",first_observed="2026-09-22T11:30:00Z",last_observed="2026-09-22T11:35:00Z",number_observed=3,object_refs=["ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd"]),
    },
    "Opinion": {
        "category": CATEGORIES[0], "family": "SDO", "type": "opinion",
        "summary": "Expresa una evaluación sobre la corrección de información contenida en otros objetos STIX.",
        "use": "Úsalo cuando un analista u organización quiera expresar acuerdo o desacuerdo sobre inteligencia existente.",
        "properties": [("explanation","string","Explicación."),("authors","list[string]","Autores."),("opinion","enum","strongly-disagree, disagree, neutral, agree o strongly-agree."),("object_refs","list[identifier]","Objetos evaluados.")],
        "required": ["type","spec_version","id","created","modified","opinion","object_refs"], "recommended": ["explanation","authors"],
        "example": _sdo("opinion","b01ae5c5-f6d5-4db7-9c02-0f5e4bf52101",opinion="agree",explanation="La evidencia disponible respalda esta evaluación.",object_refs=["indicator--11111111-1111-4111-8111-111111111111"]),
    },
    "Report": {
        "category": CATEGORIES[0], "family": "SDO", "type": "report",
        "summary": "Agrupa objetos STIX relacionados dentro de una publicación o reporte.",
        "use": "Úsalo para boletines, informes o productos de inteligencia que referencian otros objetos.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("report_types","list[open-vocab]","Tipos."),("published","timestamp","Fecha de publicación."),("object_refs","list[identifier]","Objetos incluidos.")],
        "required": ["type","spec_version","id","created","modified","name","published","object_refs"], "recommended": ["description","report_types"],
        "example": _sdo("report","49da8e9e-2d7e-4d8c-81d2-80ad63ad2101","Reporte semanal de amenazas",report_types=["threat-report"],published="2026-09-22T12:00:00Z",object_refs=["indicator--11111111-1111-4111-8111-111111111111"]),
    },
    "Threat Actor": {
        "category": CATEGORIES[0], "family": "SDO", "type": "threat-actor",
        "summary": "Representa individuos, grupos u organizaciones que realizan o apoyan actividad maliciosa.",
        "use": "Úsalo cuando exista suficiente información para describir un actor de amenaza.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("threat_actor_types","list[open-vocab]","Tipos."),("aliases","list[string]","Alias."),("first_seen","timestamp","Primera vez."),("last_seen","timestamp","Última vez."),("roles","list[open-vocab]","Roles."),("goals","list[string]","Objetivos."),("sophistication","open-vocab","Sofisticación."),("resource_level","open-vocab","Recursos."),("primary_motivation","open-vocab","Motivación principal."),("secondary_motivations","list[open-vocab]","Motivaciones secundarias."),("personal_motivations","list[open-vocab]","Motivaciones personales.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description","threat_actor_types"],
        "example": _sdo("threat-actor","8e2e2d2b-17d4-4cbf-938f-98ee46b3cd3f","Actor Ejemplo",threat_actor_types=["crime-syndicate"],primary_motivation="personal-gain"),
    },
    "Tool": {
        "category": CATEGORIES[0], "family": "SDO", "type": "tool",
        "summary": "Representa software legítimo que puede ser utilizado por actores para apoyar una actividad.",
        "use": "Úsalo para herramientas ofensivas, administrativas o utilidades usadas en operaciones.",
        "properties": [("name","string","Nombre."),("description","string","Descripción."),("tool_types","list[open-vocab]","Tipos."),("aliases","list[string]","Alias."),("kill_chain_phases","list","Fases."),("tool_version","string","Versión.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description","tool_types"],
        "example": _sdo("tool","8a0f1f7e-9f1c-4fd2-bb72-bd25156d2101","Herramienta de administración remota",tool_types=["remote-access"],tool_version="2.0"),
    },
    "Vulnerability": {
        "category": CATEGORIES[0], "family": "SDO", "type": "vulnerability",
        "summary": "Representa una debilidad o vulnerabilidad en software, hardware o sistemas.",
        "use": "Úsalo para vulnerabilidades como CVE y agrega referencias externas cuando estén disponibles.",
        "properties": [("name","string","Nombre, por ejemplo un CVE."),("description","string","Descripción y contexto.")],
        "required": ["type","spec_version","id","created","modified","name"], "recommended": ["description","external_references"],
        "example": _sdo("vulnerability","0c8b5a2f-7c81-4f83-8f25-54ec1ebc2101","CVE-2026-12345",description="Vulnerabilidad ficticia utilizada como ejemplo.",external_references=[{"source_name":"cve","external_id":"CVE-2026-12345"}]),
    },

    # ------------------------------------------------------------------ SCO
    "Artifact": {
        "category": CATEGORIES[1], "family": "SCO", "type": "artifact",
        "summary": "Representa contenido binario o datos que pueden transmitirse o almacenarse.",
        "use": "Úsalo para una muestra codificada, payload o artefacto accesible mediante URL.",
        "properties": [("mime_type","string","Tipo MIME."),("payload_bin","binary","Contenido codificado en base64."),("url","string","URL donde se encuentra el artefacto."),("hashes","hashes","Hashes del artefacto."),("encryption_algorithm","enum","Algoritmo de cifrado."),("decryption_key","string","Clave de descifrado.")],
        "required": ["type","id"], "recommended": ["mime_type","hashes"],
        "example": _sco("artifact","ca17bcf8-9846-5ab4-8662-75c1bf6e63ee",mime_type="application/octet-stream",payload_bin="dGVzdA=="),
    },
    "Autonomous System": {
        "category": CATEGORIES[1], "family": "SCO", "type": "autonomous-system",
        "summary": "Representa un Sistema Autónomo (AS) de Internet.",
        "use": "Úsalo para documentar ASN, nombre del AS y registro regional.",
        "properties": [("number","integer","Número ASN."),("name","string","Nombre."),("rir","string","Registro Regional de Internet.")],
        "required": ["type","id","number"], "recommended": ["name","rir"],
        "example": _sco("autonomous-system","f720c34b-98ae-597f-ade5-27dc241e8c74",number=64512,name="Example AS",rir="ARIN"),
    },
    "Directory": {
        "category": CATEGORIES[1], "family": "SCO", "type": "directory",
        "summary": "Representa propiedades de un directorio del sistema de archivos.",
        "use": "Úsalo para rutas de directorio y metadatos temporales asociados.",
        "properties": [("path","string","Ruta."),("path_enc","string","Codificación de la ruta."),("ctime","timestamp","Creación."),("mtime","timestamp","Modificación."),("atime","timestamp","Último acceso."),("contains_refs","list[identifier]","Archivos o directorios contenidos.")],
        "required": ["type","id","path"], "recommended": ["mtime","contains_refs"],
        "example": _sco("directory","a0e2e34b-975b-5d41-8f88-448db2a72101",path="C:\\Users\\Public\\Downloads"),
    },
    "Domain Name": {
        "category": CATEGORIES[1], "family": "SCO", "type": "domain-name",
        "summary": "Representa un nombre de dominio de red.",
        "use": "Úsalo para dominios observados, maliciosos o relacionados con infraestructura.",
        "properties": [("value","string","Nombre de dominio."),("resolves_to_refs","list[identifier]","IPs o nombres a los que resuelve.")],
        "required": ["type","id","value"], "recommended": ["resolves_to_refs"],
        "example": _sco("domain-name","3c10e93f-798e-5a26-a0c1-08156efab7f5",value="malicious-example.com"),
    },
    "Email Address": {
        "category": CATEGORIES[1], "family": "SCO", "type": "email-addr",
        "summary": "Representa una dirección de correo electrónico.",
        "use": "Úsalo para remitentes, destinatarios u otras direcciones observadas.",
        "properties": [("value","string","Dirección de correo."),("display_name","string","Nombre mostrado."),("belongs_to_ref","identifier","Cuenta de usuario asociada.")],
        "required": ["type","id","value"], "recommended": ["display_name"],
        "example": _sco("email-addr","d1b2c3d4-1111-5aaa-8bbb-123456789001",value="security@example.com",display_name="Security Team"),
    },
    "Email Message": {
        "category": CATEGORIES[1], "family": "SCO", "type": "email-message",
        "summary": "Representa un mensaje de correo electrónico y sus encabezados principales.",
        "use": "Úsalo para phishing, spam o correos relevantes para la investigación.",
        "properties": [("is_multipart","boolean","Indica si es multipart."),("date","timestamp","Fecha."),("content_type","string","Content-Type."),("from_ref","identifier","Remitente."),("sender_ref","identifier","Sender."),("to_refs","list[identifier]","Destinatarios."),("cc_refs","list[identifier]","CC."),("bcc_refs","list[identifier]","BCC."),("message_id","string","Message-ID."),("subject","string","Asunto."),("received_lines","list[string]","Líneas Received."),("additional_header_fields","dictionary","Otros encabezados."),("body","string","Cuerpo."),("body_multipart","list","Partes del cuerpo."),("raw_email_ref","identifier","Artefacto con correo crudo.")],
        "required": ["type","id","is_multipart"], "recommended": ["from_ref","to_refs","subject","date"],
        "example": _sco("email-message","7d4a6c17-7c25-5b9e-aab1-c6f721312101",is_multipart=False,date="2026-09-22T11:00:00Z",from_ref="email-addr--d1b2c3d4-1111-5aaa-8bbb-123456789001",subject="Actualización urgente",body="Revise el enlace adjunto."),
    },
    "File": {
        "category": CATEGORIES[1], "family": "SCO", "type": "file",
        "summary": "Representa un archivo y sus metadatos.",
        "use": "Úsalo para hashes, nombres, tamaños y metadatos de archivos observados.",
        "properties": [("hashes","hashes","Hashes."),("size","integer","Tamaño en bytes."),("name","string","Nombre."),("name_enc","string","Codificación."),("magic_number_hex","hex","Magic number."),("mime_type","string","Tipo MIME."),("ctime","timestamp","Creación."),("mtime","timestamp","Modificación."),("atime","timestamp","Acceso."),("parent_directory_ref","identifier","Directorio padre."),("contains_refs","list[identifier]","Objetos contenidos."),("content_ref","identifier","Contenido Artifact."),("extensions","dictionary","Extensiones como PE, PDF, archive, raster-image o NTFS.")],
        "required": ["type","id"], "recommended": ["hashes","name","size"],
        "example": _sco("file","7cce6789-89ab-5def-8123-456789abcdef",name="invoice.exe",size=245760,hashes={"SHA-256":"7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5"}),
    },
    "IPv4 Address": {
        "category": CATEGORIES[1], "family": "SCO", "type": "ipv4-addr",
        "summary": "Representa una dirección IPv4 o un bloque CIDR.",
        "use": "Úsalo para IPs observadas en conexiones, indicadores o infraestructura.",
        "properties": [("value","string","IPv4 o CIDR."),("resolves_to_refs","list[identifier]","MAC relacionadas."),("belongs_to_refs","list[identifier]","Sistemas autónomos.")],
        "required": ["type","id","value"], "recommended": ["belongs_to_refs"],
        "example": _sco("ipv4-addr","ff26c055-6336-5bc5-b98d-13d6226742dd",value="198.51.100.3"),
    },
    "IPv6 Address": {
        "category": CATEGORIES[1], "family": "SCO", "type": "ipv6-addr",
        "summary": "Representa una dirección IPv6 o un bloque CIDR.",
        "use": "Úsalo para direcciones IPv6 observadas o relacionadas con infraestructura.",
        "properties": [("value","string","IPv6 o CIDR."),("resolves_to_refs","list[identifier]","MAC relacionadas."),("belongs_to_refs","list[identifier]","Sistemas autónomos.")],
        "required": ["type","id","value"], "recommended": ["belongs_to_refs"],
        "example": _sco("ipv6-addr","1e61d36c-a16c-53b7-a80f-2a00161c96b1",value="2001:db8:85a3::8a2e:370:7334"),
    },
    "MAC Address": {
        "category": CATEGORIES[1], "family": "SCO", "type": "mac-addr",
        "summary": "Representa una dirección MAC de capa 2.",
        "use": "Úsalo para identificar interfaces o dispositivos en observaciones de red.",
        "properties": [("value","string","Dirección MAC.")],
        "required": ["type","id","value"], "recommended": [],
        "example": _sco("mac-addr","65cfc0f6-5f73-5e21-a165-0c57b1ea2101",value="00:1B:44:11:3A:B7"),
    },
    "Mutex": {
        "category": CATEGORIES[1], "family": "SCO", "type": "mutex",
        "summary": "Representa un mutex del sistema, frecuentemente útil como artefacto de malware.",
        "use": "Úsalo para nombres de mutex observados durante análisis de procesos o malware.",
        "properties": [("name","string","Nombre del mutex.")],
        "required": ["type","id","name"], "recommended": [],
        "example": _sco("mutex","9d4d63f4-2247-5d64-9bd3-0c9dbeca2101",name="Global\\ExampleMutex"),
    },
    "Network Traffic": {
        "category": CATEGORIES[1], "family": "SCO", "type": "network-traffic",
        "summary": "Representa tráfico de red entre dos extremos y sus protocolos.",
        "use": "Úsalo para conexiones, flujos o sesiones observadas.",
        "properties": [("start","timestamp","Inicio."),("end","timestamp","Fin."),("is_active","boolean","Sigue activa."),("src_ref","identifier","Origen."),("dst_ref","identifier","Destino."),("src_port","integer","Puerto origen."),("dst_port","integer","Puerto destino."),("protocols","list[string]","Protocolos, del nivel más bajo al más alto."),("src_byte_count","integer","Bytes origen."),("dst_byte_count","integer","Bytes destino."),("src_packets","integer","Paquetes origen."),("dst_packets","integer","Paquetes destino."),("ipfix","dictionary","Campos IPFIX."),("src_payload_ref","identifier","Payload origen."),("dst_payload_ref","identifier","Payload destino."),("encapsulates_refs","list[identifier]","Tráfico encapsulado."),("encapsulated_by_ref","identifier","Tráfico que lo encapsula."),("extensions","dictionary","Extensiones HTTP, TCP, ICMP, socket, etc.")],
        "required": ["type","id","protocols"], "recommended": ["src_ref","dst_ref","src_port","dst_port","start"],
        "example": _sco("network-traffic","5f3c6f5e-5ed8-5f6b-bb07-a2eb7a522101",start="2026-09-22T11:00:00Z",src_ref="ipv4-addr--ff26c055-6336-5bc5-b98d-13d6226742dd",dst_ref="ipv4-addr--a612e2a0-2d05-5f7a-9b16-0b75a0ba2101",src_port=51514,dst_port=443,protocols=["ipv4","tcp","tls"]),
    },
    "Process": {
        "category": CATEGORIES[1], "family": "SCO", "type": "process",
        "summary": "Representa un proceso observado en un sistema.",
        "use": "Úsalo para PID, argumentos, proceso padre/hijo y binario asociado.",
        "properties": [("is_hidden","boolean","Proceso oculto."),("pid","integer","PID."),("created_time","timestamp","Creación."),("cwd","string","Directorio de trabajo."),("command_line","string","Línea de comandos."),("environment_variables","dictionary","Variables de entorno."),("opened_connection_refs","list[identifier]","Conexiones abiertas."),("creator_user_ref","identifier","Usuario creador."),("image_ref","identifier","Ejecutable."),("parent_ref","identifier","Proceso padre."),("child_refs","list[identifier]","Procesos hijos."),("extensions","dictionary","Extensiones de proceso Windows/servicio.")],
        "required": ["type","id"], "recommended": ["pid","command_line","image_ref"],
        "example": _sco("process","c8f5c937-0e9c-5a15-8f9f-2268b85f2101",pid=4242,created_time="2026-09-22T11:00:00Z",command_line="invoice.exe /silent",image_ref="file--7cce6789-89ab-5def-8123-456789abcdef"),
    },
    "Software": {
        "category": CATEGORIES[1], "family": "SCO", "type": "software",
        "summary": "Representa software, sistema operativo o producto instalado.",
        "use": "Úsalo para identificar productos y versiones observadas en un host.",
        "properties": [("name","string","Nombre."),("cpe","string","CPE."),("swid","string","SWID."),("languages","list[string]","Idiomas."),("vendor","string","Fabricante."),("version","string","Versión.")],
        "required": ["type","id","name"], "recommended": ["vendor","version","cpe"],
        "example": _sco("software","7a1f2f53-612a-5e67-a808-0bdbdb3b2101",name="Example Web Server",vendor="Example Corp",version="4.2.1"),
    },
    "URL": {
        "category": CATEGORIES[1], "family": "SCO", "type": "url",
        "summary": "Representa un Localizador Uniforme de Recursos (URL).",
        "use": "Úsalo para enlaces observados en tráfico, correo, phishing u otra actividad.",
        "properties": [("value","string","URL completa.")],
        "required": ["type","id","value"], "recommended": [],
        "example": _sco("url","c1477287-23ac-5971-a010-5c2878772101",value="https://malicious-example.com/login"),
    },
    "User Account": {
        "category": CATEGORIES[1], "family": "SCO", "type": "user-account",
        "summary": "Representa una cuenta de usuario local, de dominio, Unix, SaaS u otro sistema.",
        "use": "Úsalo para usuarios observados en autenticaciones, endpoints o actividad sospechosa.",
        "properties": [("user_id","string","Identificador."),("credential","string","Credencial cuando proceda; debe manejarse con extremo cuidado."),("account_login","string","Login."),("account_type","open-vocab","Tipo de cuenta."),("display_name","string","Nombre mostrado."),("is_service_account","boolean","Cuenta de servicio."),("is_privileged","boolean","Privilegiada."),("can_escalate_privs","boolean","Puede escalar privilegios."),("is_disabled","boolean","Deshabilitada."),("account_created","timestamp","Creación."),("account_expires","timestamp","Expiración."),("credential_last_changed","timestamp","Cambio de credencial."),("account_first_login","timestamp","Primer login."),("account_last_login","timestamp","Último login.")],
        "required": ["type","id"], "recommended": ["user_id","account_login","account_type"],
        "example": _sco("user-account","5c0b37d4-35c3-59d2-8678-1118548d2101",user_id="1001",account_login="jdoe",account_type="windows-domain",display_name="John Doe",is_privileged=False),
    },
    "Windows Registry Key": {
        "category": CATEGORIES[1], "family": "SCO", "type": "windows-registry-key",
        "summary": "Representa una clave del Registro de Windows y sus valores.",
        "use": "Úsalo para persistencia, configuración o artefactos forenses del Registro.",
        "properties": [("key","string","Ruta de la clave."),("values","list","Valores de la clave."),("modified_time","timestamp","Última modificación."),("creator_user_ref","identifier","Usuario creador."),("number_of_subkeys","integer","Número de subclaves.")],
        "required": ["type","id"], "recommended": ["key","values","modified_time"],
        "example": _sco("windows-registry-key","2d6caeb0-2b3f-56bf-a2f0-e1b8e3302101",key="HKEY_LOCAL_MACHINE\\Software\\Example",values=[{"name":"Updater","data":"C:\\Temp\\invoice.exe","data_type":"REG_SZ"}]),
    },
    "X.509 Certificate": {
        "category": CATEGORIES[1], "family": "SCO", "type": "x509-certificate",
        "summary": "Representa las propiedades de un certificado X.509.",
        "use": "Úsalo para certificados observados en TLS, malware, firmas o infraestructura.",
        "properties": [("is_self_signed","boolean","Autofirmado."),("hashes","hashes","Hashes del certificado."),("version","string","Versión."),("serial_number","string","Número de serie."),("signature_algorithm","string","Algoritmo de firma."),("issuer","string","Emisor."),("validity_not_before","timestamp","Inicio de validez."),("validity_not_after","timestamp","Fin de validez."),("subject","string","Sujeto."),("subject_public_key_algorithm","string","Algoritmo de clave pública."),("subject_public_key_modulus","string","Módulo RSA."),("subject_public_key_exponent","integer","Exponente RSA."),("x509_v3_extensions","object","Extensiones X.509 v3.")],
        "required": ["type","id"], "recommended": ["hashes","serial_number","issuer","subject","validity_not_after"],
        "example": _sco("x509-certificate","463d7b2a-8516-5a50-a3d7-6f801465d5de",serial_number="01:23:45:67:89:AB",issuer="CN=Example CA,O=Example Corp",subject="CN=malicious-example.com",validity_not_before="2026-01-01T00:00:00Z",validity_not_after="2027-01-01T00:00:00Z"),
    },

    # ------------------------------------------------------------------ SRO
    "Relationship": {
        "category": CATEGORIES[2], "family": "SRO", "type": "relationship",
        "summary": "Conecta dos objetos STIX y expresa cómo están relacionados.",
        "use": "Úsalo cuando quieras establecer una relación explícita como indicates, uses, targets o related-to.",
        "properties": [("relationship_type","string","Tipo de relación."),("description","string","Contexto adicional."),("source_ref","identifier","Objeto origen."),("target_ref","identifier","Objeto destino."),("start_time","timestamp","Inicio de la relación."),("stop_time","timestamp","Fin de la relación.")],
        "required": ["type","spec_version","id","created","modified","relationship_type","source_ref","target_ref"], "recommended": ["description"],
        "example": _sro("relationship","6d0bbf0d-2e5d-4e5a-b89f-d13d362b2101",relationship_type="indicates",source_ref="indicator--11111111-1111-4111-8111-111111111111",target_ref="malware--31b940d4-6f7f-459a-80ea-9c1f17b5891b",description="El indicador está asociado con la familia de malware observada."),
    },
    "Sighting": {
        "category": CATEGORIES[2], "family": "SRO", "type": "sighting",
        "summary": "Representa que un SDO fue visto u observado por una entidad.",
        "use": "Úsalo para registrar avistamientos de indicadores u otros SDO, incluyendo conteo y periodo.",
        "properties": [("description","string","Descripción."),("first_seen","timestamp","Primera vez."),("last_seen","timestamp","Última vez."),("count","integer","Número de avistamientos."),("sighting_of_ref","identifier","SDO observado."),("observed_data_refs","list[identifier]","Observed Data relacionado."),("where_sighted_refs","list[identifier]","Identidades que lo observaron."),("summary","boolean","Indica si resume múltiples observaciones.")],
        "required": ["type","spec_version","id","created","modified","sighting_of_ref"], "recommended": ["first_seen","last_seen","count","where_sighted_refs"],
        "example": _sro("sighting","ee20065d-2555-424f-ad9e-0f8428622101",sighting_of_ref="indicator--11111111-1111-4111-8111-111111111111",first_seen="2026-09-22T10:00:00Z",last_seen="2026-09-22T11:00:00Z",count=4,where_sighted_refs=["identity--f431f809-377b-45e0-aa1c-6a4751cae5ff"]),
    },

    # ------------------------------------------------------ Language Content
    "Language Content": {
        "category": CATEGORIES[3], "family": "Language Content Object", "type": "language-content",
        "summary": "Proporciona traducciones de propiedades textuales de otro objeto STIX.",
        "use": "Úsalo cuando necesites distribuir el mismo contenido en uno o más idiomas sin duplicar el objeto original.",
        "properties": [("object_ref","identifier","Objeto al que aplica la traducción."),("object_modified","timestamp","Versión exacta del objeto traducido."),("contents","dictionary","Traducciones organizadas por código de idioma RFC 5646.")],
        "required": ["type","spec_version","id","created","modified","object_ref","contents"], "recommended": ["object_modified"],
        "example": {
            "type":"language-content","spec_version":"2.1","id":"language-content--b86bd89f-98bb-4fa9-8cb2-9ad421da981d","created":"2026-09-22T12:00:00Z","modified":"2026-09-22T12:00:00Z","object_ref":"campaign--12a111f0-b824-4baf-a224-83b80237a094","object_modified":"2026-09-22T12:00:00Z","contents":{"es":{"name":"Campaña de phishing financiero","description":"Actividad coordinada contra usuarios del sector financiero."}}
        },
    },

    # ----------------------------------------------------- Marking Definition
    "Marking Definition": {
        "category": CATEGORIES[4], "family": "Marking Definition Object", "type": "marking-definition",
        "summary": "Define reglas de manejo, distribución o uso que pueden aplicarse a contenido STIX.",
        "use": "Úsalo para aplicar una declaración de uso o una definición de marcado soportada por STIX.",
        "properties": [("name","string","Nombre opcional."),("definition_type","open-vocab","Tipo de definición; en STIX 2.1 esta forma está deprecada para nuevas extensiones."),("definition","object","Contenido de la definición, por ejemplo statement o tlp."),("extensions","dictionary","Mecanismo recomendado para nuevos tipos de marcado.")],
        "required": ["type","spec_version","id","created"], "recommended": ["name"],
        "example": {
            "type":"marking-definition","spec_version":"2.1","id":"marking-definition--4a0042fe-8b88-40fe-9600-dfa128ce6fbd","created":"2026-09-22T12:00:00Z","definition_type":"statement","definition":{"statement":"Uso exclusivo para intercambio autorizado entre participantes."}
        },
        "note": "Para TLP, STIX 2.1 exige usar las definiciones estándar establecidas por la especificación; no se deben crear IDs TLP arbitrarios.",
    },
}


def objects_by_category():
    """Devuelve los nombres de objetos agrupados respetando el orden de CATEGORIES."""
    return {
        category: [name for name, item in WIKI_OBJECTS.items() if item["category"] == category]
        for category in CATEGORIES
    }
