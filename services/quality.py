import json


# ============================================================
# CONFIGURACIÓN
# ============================================================

VALID_SEVERITIES = {
    "medium",
    "high",
    "critical",
}


# Objetos en los que queremos aplicar la regla institucional
# de Name + Description.
#
# Se excluyen SCO, SRO y objetos STIX que normalmente no utilizan
# estas propiedades de la misma forma.
SDO_TYPES_REQUIRING_NAME_DESCRIPTION = {
    "attack-pattern",
    "campaign",
    "course-of-action",
    "grouping",
    "identity",
    "incident",
    "indicator",
    "infrastructure",
    "intrusion-set",
    "malware",
    "report",
    "threat-actor",
    "tool",
    "vulnerability",
}


# Tipos para los cuales confidence puede aportar contexto.
CONFIDENCE_RELEVANT_TYPES = {
    "attack-pattern",
    "campaign",
    "course-of-action",
    "grouping",
    "identity",
    "incident",
    "indicator",
    "infrastructure",
    "intrusion-set",
    "malware",
    "malware-analysis",
    "note",
    "observed-data",
    "opinion",
    "report",
    "threat-actor",
    "tool",
    "vulnerability",
    "relationship",
    "sighting",
}


# ============================================================
# HELPERS
# ============================================================

def _objects(payload):
    """
    Devuelve los objetos STIX que deben ser evaluados.

    Si payload es un Bundle:
        devuelve payload["objects"]

    Si payload es un objeto individual:
        devuelve [payload]
    """

    if not isinstance(payload, dict):
        return []

    if payload.get("type") == "bundle":
        objects = payload.get("objects", [])

        if isinstance(objects, list):
            return [
                obj
                for obj in objects
                if isinstance(obj, dict)
            ]

        return []

    return [payload]


def _payload_id(payload):
    """
    Obtiene un identificador para mostrar en las reglas globales.
    """

    if isinstance(payload, dict):
        return payload.get("id", "STIX")

    return "STIX"


def _object_id(obj):
    """
    Obtiene el ID del objeto o un texto alternativo.
    """

    if not isinstance(obj, dict):
        return "objeto"

    return obj.get(
        "id",
        obj.get("type", "objeto")
    )


def _get_severity_values(obj):
    """
    Busca severity dentro de un objeto STIX.

    Formatos soportados:

    1. x_severity
       "x_severity": "High"

    2. Propiedades personalizadas terminadas en _severity
       "x_sprics_severity": "Medium"
       "x_company_severity": "Critical"

    3. labels
       "labels": ["severity:medium"]

    Devuelve una lista con los valores encontrados.
    """

    values = []

    if not isinstance(obj, dict):
        return values

    # --------------------------------------------------------
    # x_severity
    # --------------------------------------------------------

    value = obj.get("x_severity")

    if isinstance(value, str) and value.strip():
        values.append(value.strip())

    # --------------------------------------------------------
    # Custom properties:
    # x_sprics_severity
    # x_company_severity
    # etc.
    # --------------------------------------------------------

    for key, value in obj.items():

        if not isinstance(key, str):
            continue

        if (
            key.startswith("x_")
            and key.endswith("_severity")
            and key != "x_severity"
            and isinstance(value, str)
            and value.strip()
        ):
            values.append(value.strip())

    # --------------------------------------------------------
    # labels: ["severity:medium"]
    # --------------------------------------------------------

    labels = obj.get("labels", [])

    if isinstance(labels, list):

        for label in labels:

            if not isinstance(label, str):
                continue

            if label.lower().startswith("severity:"):

                value = label.split(":", 1)[1].strip()

                if value:
                    values.append(value)

    return values


def _validate_severity_global(payload, objects):
    """
    SP-1

    Severity se evalúa UNA SOLA VEZ para todo el reporte.

    Reglas:

    - Debe existir al menos una severity en el STIX.
    - No es obligatorio tener severity en cada objeto.
    - Los valores permitidos son:
        Medium
        High
        Critical
    - La validación es case-insensitive.
    """

    results = []

    severity_values = []

    for obj in objects:
        severity_values.extend(
            _get_severity_values(obj)
        )

    report_id = _payload_id(payload)

    # --------------------------------------------------------
    # No existe severity en ningún objeto
    # --------------------------------------------------------

    if not severity_values:

        results.append({
            "level": "warning",
            "object": report_id,
            "rule": "SP-1 / severity",
            "message": (
                "No se encontró severidad en el reporte STIX. "
                "Se espera uno de los siguientes valores: "
                "Medium, High o Critical."
            ),
        })

        return results

    # --------------------------------------------------------
    # Buscar valores inválidos
    # --------------------------------------------------------

    invalid_values = [
        value
        for value in severity_values
        if value.lower() not in VALID_SEVERITIES
    ]

    if invalid_values:

        invalid_unique = sorted(
            set(invalid_values),
            key=str.lower
        )

        results.append({
            "level": "error",
            "object": report_id,
            "rule": "SP-1 / severity",
            "message": (
                "Se encontraron valores de severidad no válidos: "
                f"{', '.join(invalid_unique)}. "
                "Los valores permitidos son "
                "Medium, High o Critical."
            ),
        })

        return results

    # --------------------------------------------------------
    # Todas las severidades encontradas son válidas
    # --------------------------------------------------------

    normalized_values = {
        value.lower()
        for value in severity_values
    }

    display_order = [
        severity.capitalize()
        for severity in (
            "medium",
            "high",
            "critical"
        )
        if severity in normalized_values
    ]

    results.append({
        "level": "ok",
        "object": report_id,
        "rule": "SP-1 / severity",
        "message": (
            "Severidad presente y válida: "
            f"{', '.join(display_order)}."
        ),
    })

    return results


def _validate_name_description(obj):
    """
    SP-2

    Evalúa Name y Description únicamente para los tipos
    definidos en SDO_TYPES_REQUIRING_NAME_DESCRIPTION.
    """

    results = []

    if not isinstance(obj, dict):
        return results

    obj_type = obj.get("type", "desconocido")
    obj_id = _object_id(obj)

    if obj_type not in SDO_TYPES_REQUIRING_NAME_DESCRIPTION:
        return results

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    name = obj.get("name")

    name_present = (
        isinstance(name, str)
        and bool(name.strip())
    )

    if name_present:

        results.append({
            "level": "ok",
            "object": obj_id,
            "rule": "SP-2 / name",
            "message": "Nombre presente.",
        })

    else:

        results.append({
            "level": "error",
            "object": obj_id,
            "rule": "SP-2 / name",
            "message": (
                "El objeto debe incluir la propiedad "
                "'name' con contenido."
            ),
        })

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = obj.get("description")

    description_present = (
        isinstance(description, str)
        and bool(description.strip())
    )

    if description_present:

        results.append({
            "level": "ok",
            "object": obj_id,
            "rule": "SP-2 / description",
            "message": "Descripción presente.",
        })

    else:

        results.append({
            "level": "error",
            "object": obj_id,
            "rule": "SP-2 / description",
            "message": (
                "El objeto debe incluir la propiedad "
                "'description' con contenido."
            ),
        })

    return results


def _validate_confidence(obj):
    """
    Confidence es una recomendación de calidad.

    - Si existe, debe estar entre 0 y 100.
    - Si no existe, genera advertencia.
    """

    results = []

    if not isinstance(obj, dict):
        return results

    obj_type = obj.get("type", "")
    obj_id = _object_id(obj)

    if obj_type not in CONFIDENCE_RELEVANT_TYPES:
        return results

    # --------------------------------------------------------
    # Confidence no existe
    # --------------------------------------------------------

    if "confidence" not in obj:

        results.append({
            "level": "warning",
            "object": obj_id,
            "rule": "confidence",
            "message": (
                "Se recomienda incluir confidence "
                "(valor entre 0 y 100) cuando sea posible."
            ),
        })

        return results

    # --------------------------------------------------------
    # Confidence existe
    # --------------------------------------------------------

    confidence = obj.get("confidence")

    if (
        isinstance(confidence, int)
        and not isinstance(confidence, bool)
        and 0 <= confidence <= 100
    ):

        results.append({
            "level": "ok",
            "object": obj_id,
            "rule": "confidence",
            "message": (
                f"Confidence válido: {confidence}."
            ),
        })

    else:

        results.append({
            "level": "error",
            "object": obj_id,
            "rule": "confidence",
            "message": (
                "Confidence debe ser un número entero "
                "entre 0 y 100."
            ),
        })

    return results


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def run_quality_checks(payload):
    """
    Ejecuta las reglas de calidad institucionales.

    Puede recibir:

    - dict de Python
    - string JSON
    - Bundle STIX
    - objeto STIX individual

    Devuelve:

    [
        {
            "level": "ok" | "warning" | "error",
            "object": "...",
            "rule": "...",
            "message": "..."
        }
    ]
    """

    # --------------------------------------------------------
    # Permitir recibir JSON como string
    # --------------------------------------------------------

    if isinstance(payload, str):

        try:
            payload = json.loads(payload)

        except json.JSONDecodeError:

            return [{
                "level": "error",
                "object": "JSON",
                "rule": "JSON",
                "message": (
                    "No fue posible ejecutar las reglas "
                    "de calidad porque el JSON es inválido."
                ),
            }]

    if not isinstance(payload, dict):

        return [{
            "level": "error",
            "object": "STIX",
            "rule": "estructura",
            "message": (
                "El contenido recibido no corresponde "
                "a un objeto JSON válido."
            ),
        }]

    results = []

    objects = _objects(payload)

    # ========================================================
    # SP-1
    # SEVERITY GLOBAL
    # ========================================================

    results.extend(
        _validate_severity_global(
            payload,
            objects
        )
    )

    # ========================================================
    # REGLAS POR OBJETO
    # ========================================================

    for obj in objects:

        # ----------------------------------------------------
        # SP-2
        # NAME + DESCRIPTION
        # ----------------------------------------------------

        results.extend(
            _validate_name_description(obj)
        )

        # ----------------------------------------------------
        # CONFIDENCE
        # ----------------------------------------------------

        results.extend(
            _validate_confidence(obj)
        )

    return results
