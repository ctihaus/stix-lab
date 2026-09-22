import json
from stix2validator import validate_string


def _format_issue(issue):
    if hasattr(issue, "message"):
        return str(issue.message)
    return str(issue)


def validate_stix_text(text: str):
    response = {"json_ok": False, "stix_ok": False, "errors": [], "warnings": [], "data": None}

    try:
        data = json.loads(text)
        response["json_ok"] = True
        response["data"] = data
    except json.JSONDecodeError as exc:
        response["errors"].append(f"JSON inválido: línea {exc.lineno}, columna {exc.colno}: {exc.msg}")
        return response

    try:
        results = validate_string(text)
        response["stix_ok"] = bool(results.is_valid)

        fatal = getattr(results, "fatal", None)
        if fatal:
            response["errors"].append(_format_issue(fatal))

        for obj_result in getattr(results, "object_results", []) or []:
            obj_id = getattr(obj_result, "object_id", "objeto") or "objeto"
            for error in getattr(obj_result, "errors", []) or []:
                response["errors"].append(f"{obj_id}: {_format_issue(error)}")
            for warning in getattr(obj_result, "warnings", []) or []:
                response["warnings"].append(f"{obj_id}: {_format_issue(warning)}")

        # Some validator result variants may expose a single object_result.
        single = getattr(results, "object_result", None)
        if single and not getattr(results, "object_results", None):
            obj_id = getattr(single, "object_id", "objeto") or "objeto"
            for error in getattr(single, "errors", []) or []:
                response["errors"].append(f"{obj_id}: {_format_issue(error)}")
            for warning in getattr(single, "warnings", []) or []:
                response["warnings"].append(f"{obj_id}: {_format_issue(warning)}")

    except Exception as exc:
        response["errors"].append(f"No fue posible completar la validación STIX: {exc}")

    return response
