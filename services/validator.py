import json
from stix2validator import validate_string

def validate_stix_text(text: str):
    response = {
        "json_ok": False,
        "stix_ok": False,
        "errors": [],
        "warnings": [],
        "data": None
    }

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

    try:

        # =====================================================
        # BUNDLE
        # =====================================================

        if data.get("type") == "bundle":

            bundle_valid = True

            # Validaciones básicas del contenedor
            bundle_id = data.get("id", "")

            if not bundle_id.startswith("bundle--"):
                response["errors"].append(
                    "El identificador del Bundle debe iniciar con 'bundle--'."
                )
                bundle_valid = False

            objects = data.get("objects")

            if not isinstance(objects, list):
                response["errors"].append(
                    "La propiedad 'objects' del Bundle debe ser una lista."
                )
                bundle_valid = False

            elif len(objects) == 0:
                response["errors"].append(
                    "El Bundle debe contener al menos un objeto STIX."
                )
                bundle_valid = False

            # Validar objetos individualmente
            if isinstance(objects, list):

                for obj in objects:

                    obj_text = json.dumps(obj)

                    result = validate_string(obj_text)

                    result_list = (
                        result if isinstance(result, list)
                        else [result]
                    )

                    for r in result_list:

                        obj_id = (
                            getattr(r, "object_id", None)
                            or obj.get("id", "objeto")
                        )

                        if not getattr(r, "is_valid", False):
                            bundle_valid = False

                        for error in getattr(r, "errors", []) or []:
                            response["errors"].append(
                                f"{obj_id}: {_format_issue(error)}"
                            )

                        for warning in getattr(r, "warnings", []) or []:
                            response["warnings"].append(
                                f"{obj_id}: {_format_issue(warning)}"
                            )

            response["stix_ok"] = bundle_valid

        # =====================================================
        # OBJETO STIX NORMAL
        # =====================================================

        else:

            results = validate_string(text)

            result_list = (
                results if isinstance(results, list)
                else [results]
            )

            all_valid = True

            for result in result_list:

                if not getattr(result, "is_valid", False):
                    all_valid = False

                obj_id = (
                    getattr(result, "object_id", None)
                    or data.get("id", "objeto")
                )

                for error in getattr(result, "errors", []) or []:
                    response["errors"].append(
                        f"{obj_id}: {_format_issue(error)}"
                    )

                for warning in getattr(result, "warnings", []) or []:
                    response["warnings"].append(
                        f"{obj_id}: {_format_issue(warning)}"
                    )

            response["stix_ok"] = all_valid

    except Exception as exc:

        response["errors"].append(
            f"No fue posible completar la validación STIX: {exc}"
        )

    return response
