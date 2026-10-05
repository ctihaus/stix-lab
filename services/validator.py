import json
from stix2validator import validate_string

def _format_issue(issue):
    if hasattr(issue, "message"):
        return str(issue.message)
    return str(issue)

def validate_stix_text(text: str):
    response = {
        "json_ok": False,
        "stix_ok": False,
        "errors": [],
        "warnings": [],
        "data": None
    }

    # =========================================================
    # JSON
    # =========================================================
    try:
        data = json.loads(text)

        response["json_ok"] = True
        response["data"] = data

    except json.JSONDecodeError as exc:

        response["errors"].append(
            f"JSON inválido: línea {exc.lineno}, "
            f"columna {exc.colno}: {exc.msg}"
        )

        return response

    # =========================================================
    # STIX
    # =========================================================
    try:

        results = validate_string(text)

        # Normalizar resultado
        if isinstance(results, list):
            result_list = results
        else:
            result_list = [results]

        all_valid = True

        for result in result_list:

            if not getattr(result, "is_valid", False):
                all_valid = False

            obj_id = (
                getattr(result, "object_id", None)
                or "objeto"
            )

            # Errores
            for error in getattr(result, "errors", []) or []:

                response["errors"].append(
                    f"{obj_id}: {_format_issue(error)}"
                )

            # Advertencias
            for warning in getattr(result, "warnings", []) or []:

                response["warnings"].append(
                    f"{obj_id}: {_format_issue(warning)}"
                )

            # Error fatal
            fatal_error = getattr(result, "error", None)

            if fatal_error:

                response["errors"].append(
                    f"{obj_id}: {fatal_error}"
                )

                all_valid = False

        response["stix_ok"] = all_valid

    except Exception as exc:

        response["errors"].append(
            f"No fue posible completar la validación STIX: {exc}"
        )

    return response
