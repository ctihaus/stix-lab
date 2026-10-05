import json


# ============================================================
# CONFIGURACIÓN
# ============================================================

VALID_SEVERITIES = {
    "medium",
    "high",
    "critical",
}


# Objetos para los cuales se requiere Name + Description
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


# Objetos donde confidence puede ser relevante
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
    Devuelve los objetos STIX a evaluar.

    Bundle:
        devuelve payload["objects"]

    Objeto individual:
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

    if isinstance(payload, dict):
        return payload.get("id", "STIX")

    return "STIX"


def _object_id(obj):

    if not isinstance(obj, dict):
        return "objeto"

    return obj.get(
        "id",
        obj.get("type", "objeto")
    )


def _get_severity_values(obj):
    """
    Busca severity en:

    x_severity

    x_*_severity
    Ej:
        x_sprics_severity

    labels
    Ej:
        labels: ["severity:medium"]
    """

    values = []

    if not isinstance(obj, dict):
        return values

    # ========================================================
    # x_severity
    # ========================================================

    value = obj.get("x_severity")

    if isinstance(value, str) and value.strip():
        values.append(value.strip())

    # ========================================================
    # x_*_severity
    # ========================================================

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

    # ========================================================
    # labels
    # ========================================================

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


# ============================================================
# SP-1
# SEVERITY GLOBAL
# ============================================================

def _validate_severity_global(payload, objects):

    severity_values = []

    for obj in objects:
        severity_values.extend(
            _get_severity_values(obj)
        )

    report_id = _payload_id(payload)

    # --------------------------------------------------------
    # No existe severity
    # --------------------------------------------------------

    if not severity_values:

        return [{
            "level": "warning",
            "object": report_id,
            "rule": "SP-1 / Severity",
            "message": (
                "No se encontró severidad en el reporte STIX. "
                "Se espera Medium, High o Critical."
            ),
            "affected": [],
        }]

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

        return [{
            "level": "error",
            "object": report_id,
            "rule": "SP-1 / Severity",
            "message": (
                "Se encontraron valores de severidad no válidos: "
                f"{', '.join(invalid_unique)}. "
                "Los valores permitidos son Medium, High o Critical."
            ),
            "affected": [],
        }]

    # --------------------------------------------------------
    # Severity correcta
    # --------------------------------------------------------

    normalized = {
        value.lower()
        for value in severity_values
    }

    display_values = [
        value.capitalize()
        for value in (
            "medium",
            "high",
            "critical",
        )
        if value in normalized
    ]

    return [{
        "level": "ok",
        "object": report_id,
        "rule": "SP-1 / Severity",
        "message": (
            "Severidad presente y válida: "
            f"{', '.join(display_values)}."
        ),
        "affected": [],
    }]


# ============================================================
# SP-2
# NAME GLOBAL
# ============================================================

def _validate_name_grouped(objects):

    applicable_objects = [
        obj
        for obj in objects
        if obj.get("type")
        in SDO_TYPES_REQUIRING_NAME_DESCRIPTION
    ]

    if not applicable_objects:
        return []

    missing = []

    for obj in applicable_objects:

        name = obj.get("name")

        if not (
            isinstance(name, str)
            and name.strip()
        ):
            missing.append(
                _object_id(obj)
            )

    total = len(applicable_objects)

    # --------------------------------------------------------
    # Todos correctos
    # --------------------------------------------------------

    if not missing:

        return [{
            "level": "ok",
            "object": "Reporte STIX",
            "rule": "SP-2 / Name",
            "message": (
                f"Todos los objetos evaluados ({total}) "
                "contienen nombre."
            ),
            "affected": [],
        }]

    # --------------------------------------------------------
    # Objetos sin name
    # --------------------------------------------------------

    return [{
        "level": "error",
        "object": "Reporte STIX",
        "rule": "SP-2 / Name",
        "message": (
            f"{len(missing)} de {total} objetos evaluados "
            "no contienen la propiedad 'name' con contenido."
        ),
        "affected": missing,
    }]


# ============================================================
# SP-2
# DESCRIPTION GLOBAL
# ============================================================

def _validate_description_grouped(objects):

    applicable_objects = [
        obj
        for obj in objects
        if obj.get("type")
        in SDO_TYPES_REQUIRING_NAME_DESCRIPTION
    ]

    if not applicable_objects:
        return []

    missing = []

    for obj in applicable_objects:

        description = obj.get("description")

        if not (
            isinstance(description, str)
            and description.strip()
        ):
            missing.append(
                _object_id(obj)
            )

    total = len(applicable_objects)

    # --------------------------------------------------------
    # Todos correctos
    # --------------------------------------------------------

    if not missing:

        return [{
            "level": "ok",
            "object": "Reporte STIX",
            "rule": "SP-2 / Description",
            "message": (
                f"Todos los objetos evaluados ({total}) "
                "contienen descripción."
            ),
            "affected": [],
        }]

    # --------------------------------------------------------
    # Objetos sin description
    # --------------------------------------------------------

    return [{
        "level": "error",
        "object": "Reporte STIX",
        "rule": "SP-2 / Description",
        "message": (
            f"{len(missing)} de {total} objetos evaluados "
            "no contienen la propiedad 'description' con contenido."
        ),
        "affected": missing,
    }]


# ============================================================
# CONFIDENCE GLOBAL
# ============================================================

def _validate_confidence_grouped(objects):

    applicable_objects = [
        obj
        for obj in objects
        if obj.get("type")
        in CONFIDENCE_RELEVANT_TYPES
    ]

    if not applicable_objects:
        return []

    missing = []
    invalid = []
    valid = []

    for obj in applicable_objects:

        obj_id = _object_id(obj)

        # ----------------------------------------------------
        # No existe
        # ----------------------------------------------------

        if "confidence" not in obj:

            missing.append(obj_id)
            continue

        confidence = obj.get("confidence")

        # ----------------------------------------------------
        # Existe y es válido
        # ----------------------------------------------------

        if (
            isinstance(confidence, int)
            and not isinstance(confidence, bool)
            and 0 <= confidence <= 100
        ):

            valid.append(obj_id)

        # ----------------------------------------------------
        # Existe pero es inválido
        # ----------------------------------------------------

        else:

            invalid.append(obj_id)

    total = len(applicable_objects)

    # ========================================================
    # Confidence inválido
    # ========================================================

    if invalid:

        affected = invalid + missing

        message = (
            f"{len(invalid)} de {total} objetos contienen "
            "un valor de confidence inválido."
        )

        if missing:

            message += (
                f" Además, {len(missing)} objetos "
                "no contienen confidence."
            )

        return [{
            "level": "error",
            "object": "Reporte STIX",
            "rule": "Confidence",
            "message": message,
            "affected": affected,
        }]

    # ========================================================
    # Confidence ausente
    # ========================================================

    if missing:

        return [{
            "level": "warning",
            "object": "Reporte STIX",
            "rule": "Confidence",
            "message": (
                f"{len(missing)} de {total} objetos evaluados "
                "no contienen confidence. "
                "Se recomienda incluir un valor entre 0 y 100 "
                "cuando sea posible."
            ),
            "affected": missing,
        }]

    # ========================================================
    # Todos correctos
    # ========================================================

    return [{
        "level": "ok",
        "object": "Reporte STIX",
        "rule": "Confidence",
        "message": (
            f"Todos los objetos evaluados ({total}) "
            "contienen un confidence válido."
        ),
        "affected": [],
    }]


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def run_quality_checks(payload):
    """
    Ejecuta las reglas de calidad de manera AGRUPADA.

    Devuelve un resultado por regla, no un resultado
    por cada objeto STIX.
    """

    # ========================================================
    # Permitir JSON como texto
    # ========================================================

    if isinstance(payload, str):

        try:

            payload = json.loads(payload)

        except json.JSONDecodeError:

            return [{
                "level": "error",
                "object": "JSON",
                "rule": "JSON",
                "message": (
                    "No fue posible ejecutar las reglas de calidad "
                    "porque el JSON es inválido."
                ),
                "affected": [],
            }]

    if not isinstance(payload, dict):

        return [{
            "level": "error",
            "object": "STIX",
            "rule": "Estructura",
            "message": (
                "El contenido recibido no corresponde "
                "a un objeto JSON válido."
            ),
            "affected": [],
        }]

    objects = _objects(payload)

    results = []

    # ========================================================
    # SP-1
    # ========================================================

    results.extend(
        _validate_severity_global(
            payload,
            objects
        )
    )

    # ========================================================
    # SP-2 NAME
    # ========================================================

    results.extend(
        _validate_name_grouped(
            objects
        )
    )

    # ========================================================
    # SP-2 DESCRIPTION
    # ========================================================

    results.extend(
        _validate_description_grouped(
            objects
        )
    )

    # ========================================================
    # CONFIDENCE
    # ========================================================

    results.extend(
        _validate_confidence_grouped(
            objects
        )
    )

    return results
