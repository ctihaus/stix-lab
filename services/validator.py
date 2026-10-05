import json

from stix2validator import (
    validate_instance,
    ValidationOptions
)


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
    # STIX 2.1
    # =========================================================

    try:

        options = ValidationOptions(
            version="2.1"
        )

        result = validate_instance(
            data,
            options
        )

        response["stix_ok"] = bool(
            result.is_valid
        )

        for error in getattr(
            result,
            "errors",
            []
        ) or []:

            response["errors"].append(
                _format_issue(error)
            )

        for warning in getattr(
            result,
            "warnings",
            []
        ) or []:

            response["warnings"].append(
                _format_issue(warning)
            )

    except Exception as exc:

        response["stix_ok"] = False

        response["errors"].append(
            f"No fue posible completar "
            f"la validación STIX: {exc}"
        )

    return response
