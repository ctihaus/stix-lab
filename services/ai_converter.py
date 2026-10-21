import requests


# ============================================================
# WORKER CLIENT
# ============================================================

class AIConverterError(Exception):
    pass


class AIRateLimitError(AIConverterError):

    def __init__(
        self,
        message,
        usage=None,
    ):

        super().__init__(message)

        self.usage = (
            usage or {}
        )


def _headers(
    shared_secret: str
) -> dict:

    return {

        "X-STIXLAB-KEY":
            shared_secret,

        "Content-Type":
            "application/json",
    }


# ============================================================
# GET USAGE
# ============================================================

def get_ai_usage(
    worker_url: str,
    shared_secret: str,
) -> dict:

    url = (
        worker_url.rstrip("/")
        + "/usage"
    )

    try:

        response = requests.get(
            url,
            headers=_headers(
                shared_secret
            ),
            timeout=15,
        )

    except requests.RequestException as exc:

        raise AIConverterError(
            "No fue posible conectar "
            "con el servicio de IA."
        ) from exc


    if response.status_code == 401:

        raise AIConverterError(
            "El servicio rechazó las "
            "credenciales de STIX Lab."
        )


    try:

        payload = response.json()

    except ValueError as exc:

        raise AIConverterError(
            "El servicio devolvió "
            "una respuesta inválida."
        ) from exc


    if not response.ok:

        raise AIConverterError(
            payload.get(
                "error",
                "No fue posible consultar "
                "el uso de IA."
            )
        )


    return payload


# ============================================================
# ANALYZE
# ============================================================

def analyze_log_with_ai(
    text: str,
    worker_url: str,
    shared_secret: str,
) -> dict:

    text = text.strip()

    if not text:

        raise AIConverterError(
            "El log está vacío."
        )


    url = (
        worker_url.rstrip("/")
        + "/analyze"
    )


    try:

        response = requests.post(
            url,
            headers=_headers(
                shared_secret
            ),
            json={
                "log": text
            },
            timeout=90,
        )

    except requests.RequestException as exc:

        raise AIConverterError(
            "No fue posible conectar "
            "con el servicio de IA."
        ) from exc


    try:

        payload = response.json()

    except ValueError as exc:

        raise AIConverterError(
            "El servicio de IA devolvió "
            "una respuesta inválida."
        ) from exc


    # ========================================================
    # DAILY LIMIT
    # ========================================================

    if response.status_code == 429:

        raise AIRateLimitError(
            payload.get(
                "error",
                "Se alcanzó el límite "
                "diario de IA."
            ),
            payload.get(
                "usage",
                {}
            ),
        )


    # ========================================================
    # OTHER ERROR
    # ========================================================

    if not response.ok:

        message = payload.get(
            "error",
            "No fue posible ejecutar "
            "el análisis con IA."
        )

        detail = payload.get(
            "detail"
        )

        if detail:

            message += (
                f" Detalle: {detail}"
            )

        raise AIConverterError(
            message
        )


    # ========================================================
    # SUCCESS
    # ========================================================

    analysis = payload.get(
        "analysis"
    )

    if not isinstance(
        analysis,
        dict
    ):

        raise AIConverterError(
            "La respuesta no contiene "
            "un análisis válido."
        )


    return payload
