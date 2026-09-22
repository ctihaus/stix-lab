import json

SDO_TYPES_REQUIRING_NAME_DESCRIPTION = {
    "attack-pattern", "campaign", "course-of-action", "grouping", "indicator",
    "infrastructure", "intrusion-set", "location", "malware",
    "report", "threat-actor", "tool", "vulnerability",
}
VALID_SEVERITIES = {"medium", "high", "critical"}


def _objects(data):
    if isinstance(data, dict) and data.get("type") == "bundle":
        return [obj for obj in data.get("objects", []) if isinstance(obj, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _severity_values(obj):
    values = []
    if isinstance(obj.get("x_severity"), str):
        values.append(obj["x_severity"].strip().lower())
    for label in obj.get("labels", []) or []:
        if isinstance(label, str) and label.lower().startswith("severity:"):
            values.append(label.split(":", 1)[1].strip().lower())
    return values


def run_quality_checks(payload):
    if isinstance(payload, str):
        payload = json.loads(payload)

    results = []
    for obj in _objects(payload):
        obj_type = obj.get("type", "desconocido")
        obj_id = obj.get("id", "sin-id")

        if obj_type in SDO_TYPES_REQUIRING_NAME_DESCRIPTION:
            results.append({
                "level": "error" if not str(obj.get("name", "")).strip() else "ok",
                "object": obj_id,
                "rule": "SP-2 / name",
                "message": "El objeto debe incluir un nombre con contenido." if not str(obj.get("name", "")).strip() else "Nombre presente.",
            })
            results.append({
                "level": "error" if not str(obj.get("description", "")).strip() else "ok",
                "object": obj_id,
                "rule": "SP-2 / description",
                "message": "El objeto debe incluir una descripción con contenido." if not str(obj.get("description", "")).strip() else "Descripción presente.",
            })

        severities = _severity_values(obj)
        if not severities:
            results.append({
                "level": "warning", "object": obj_id, "rule": "SP-1 / severity",
                "message": "No se encontró severidad en labels ni x_severity.",
            })
        elif any(value not in VALID_SEVERITIES for value in severities):
            results.append({
                "level": "error", "object": obj_id, "rule": "SP-1 / severity",
                "message": "La severidad debe ser Medium, High o Critical (sin distinguir mayúsculas/minúsculas).",
            })
        else:
            results.append({
                "level": "ok", "object": obj_id, "rule": "SP-1 / severity",
                "message": "Severidad válida.",
            })

        if "confidence" not in obj:
            results.append({
                "level": "warning", "object": obj_id, "rule": "confidence",
                "message": "Se recomienda incluir confidence (0-100) cuando sea posible.",
            })

    return results
