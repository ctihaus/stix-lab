import json
import re
from datetime import datetime, timezone
from ipaddress import ip_address
from urllib.parse import urlparse

from stix2.v21 import Bundle, Indicator


# ============================================================
# CONFIGURACIÓN
# ============================================================

HASH_LENGTHS = {
    32: "MD5",
    40: "SHA-1",
    64: "SHA-256",
    128: "SHA-512",
}


# ============================================================
# TEXTOS PREDETERMINADOS DEL CONSTRUCTOR MANUAL
# ============================================================

INDICATOR_DEFAULTS = {
    "IPv4": {
        "name": "Dirección IPv4 sospechosa",
        "description": (
            "Dirección IPv4 identificada durante actividades de monitoreo "
            "y asociada a comportamiento potencialmente malicioso."
        ),
        "placeholder": "185.234.72.15",
    },

    "IPv6": {
        "name": "Dirección IPv6 sospechosa",
        "description": (
            "Dirección IPv6 identificada durante actividades de monitoreo "
            "y asociada a comportamiento potencialmente malicioso."
        ),
        "placeholder": "2001:db8::1",
    },

    "Domain": {
        "name": "Dominio sospechoso",
        "description": (
            "Dominio identificado durante actividades de monitoreo "
            "y asociado a comportamiento potencialmente malicioso."
        ),
        "placeholder": "malicious-example.com",
    },

    "URL": {
        "name": "URL sospechosa",
        "description": (
            "URL identificada durante actividades de monitoreo "
            "y asociada a comportamiento potencialmente malicioso."
        ),
        "placeholder": "https://malicious-example.com/login",
    },

    "Email": {
        "name": "Dirección de correo electrónico sospechosa",
        "description": (
            "Dirección de correo electrónico identificada durante actividades "
            "de monitoreo y asociada a actividad potencialmente maliciosa."
        ),
        "placeholder": "malicious@example.com",
    },

    "MD5": {
        "name": "Hash MD5 sospechoso",
        "description": (
            "Hash MD5 asociado a un archivo identificado durante actividades "
            "de monitoreo o análisis de seguridad."
        ),
        "placeholder": "2f87ce4617f593d7148b739bbf06d059",
    },

    "SHA-1": {
        "name": "Hash SHA-1 sospechoso",
        "description": (
            "Hash SHA-1 asociado a un archivo identificado durante actividades "
            "de monitoreo o análisis de seguridad."
        ),
        "placeholder": "613000dc53e7ef0b048021f68dd06c101994da29",
    },

    "SHA-256": {
        "name": "Hash SHA-256 sospechoso",
        "description": (
            "Hash SHA-256 asociado a un archivo identificado durante actividades "
            "de monitoreo o análisis de seguridad."
        ),
        "placeholder": (
            "7600ffe12da441fe89d035b13801e8e91"
            "d064bc544a27b19a5cf49f6ab8b18f5"
        ),
    },

    "SHA-512": {
        "name": "Hash SHA-512 sospechoso",
        "description": (
            "Hash SHA-512 asociado a un archivo identificado durante actividades "
            "de monitoreo o análisis de seguridad."
        ),
        "placeholder": (
            "cf83e1357eefb8bdf1542850d66d8007d620e405"
            "0b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0"
            "ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        ),
    },
}


def get_indicator_defaults(indicator_type: str) -> dict:
    """
    Devuelve los textos predeterminados utilizados por el
    constructor manual.

    Retorna:
        {
            "name": "...",
            "description": "...",
            "placeholder": "..."
        }
    """

    return INDICATOR_DEFAULTS.get(
        indicator_type,
        {
            "name": f"Indicador {indicator_type}",
            "description": (
                "Indicador identificado durante actividades "
                "de monitoreo de seguridad."
            ),
            "placeholder": "",
        },
    )


# ============================================================
# HELPERS
# ============================================================

def _escape_stix(value: str) -> str:
    """
    Escapa caracteres especiales antes de incluir el valor
    dentro de un STIX Pattern.
    """

    return (
        value
        .replace("\\", "\\\\")
        .replace("'", "\\'")
    )


def normalize_defanged(value: str) -> str:
    """
    Convierte indicadores defanged a su representación normal.

    Ejemplos:

    hxxp://example[.]com
        ->
    http://example.com
    """

    return (
        value.strip()
        .replace("hxxps://", "https://")
        .replace("hxxp://", "http://")
        .replace("[.]", ".")
        .replace("(.)", ".")
    )


# ============================================================
# DETECCIÓN DE INDICADORES
# ============================================================

def detect_indicator(value: str):
    """
    Intenta determinar automáticamente el tipo de indicador.

    Retorna:

        ("IPv4", "185.234.72.15")

    o:

        (None, valor)
    """

    raw = normalize_defanged(value)

    # --------------------------------------------------------
    # IP
    # --------------------------------------------------------

    try:

        parsed_ip = ip_address(raw)

        return (
            "IPv4" if parsed_ip.version == 4 else "IPv6",
            str(parsed_ip),
        )

    except ValueError:
        pass

    # --------------------------------------------------------
    # HASH
    # --------------------------------------------------------

    if (
        re.fullmatch(r"[A-Fa-f0-9]+", raw)
        and len(raw) in HASH_LENGTHS
    ):

        return (
            HASH_LENGTHS[len(raw)],
            raw.lower(),
        )

    # --------------------------------------------------------
    # URL
    # --------------------------------------------------------

    if raw.lower().startswith(
        (
            "http://",
            "https://",
        )
    ):

        parsed = urlparse(raw)

        if parsed.netloc:

            return (
                "URL",
                raw,
            )

    # --------------------------------------------------------
    # DOMAIN
    # --------------------------------------------------------

    domain_regex = (
        r"(?=.{1,253}$)"
        r"(?:"
        r"[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"\."
        r")+"
        r"[A-Za-z]{2,63}"
    )

    if re.fullmatch(
        domain_regex,
        raw,
    ):

        return (
            "Domain",
            raw.lower(),
        )

    # --------------------------------------------------------
    # EMAIL
    # --------------------------------------------------------

    if re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+",
        raw,
    ):

        return (
            "Email",
            raw.lower(),
        )

    return (
        None,
        raw,
    )


# ============================================================
# STIX PATTERN
# ============================================================

def build_pattern(
    indicator_type: str,
    value: str,
) -> str:

    value = normalize_defanged(value)

    safe = _escape_stix(value)

    mappings = {
        "IPv4": (
            f"[ipv4-addr:value = '{safe}']"
        ),

        "IPv6": (
            f"[ipv6-addr:value = '{safe}']"
        ),

        "Domain": (
            f"[domain-name:value = '{safe}']"
        ),

        "URL": (
            f"[url:value = '{safe}']"
        ),

        "Email": (
            f"[email-addr:value = '{safe}']"
        ),

        "MD5": (
            f"[file:hashes.MD5 = '{safe.lower()}']"
        ),

        "SHA-1": (
            f"[file:hashes.'SHA-1' = '{safe.lower()}']"
        ),

        "SHA-256": (
            f"[file:hashes.'SHA-256' = '{safe.lower()}']"
        ),

        "SHA-512": (
            f"[file:hashes.'SHA-512' = '{safe.lower()}']"
        ),
    }

    if indicator_type not in mappings:

        raise ValueError(
            f"Tipo de indicador no soportado: "
            f"{indicator_type}"
        )

    return mappings[indicator_type]


# ============================================================
# CREAR INDICATOR
# ============================================================

def make_indicator(
    indicator_type: str,
    value: str,
    name: str = "",
    description: str = "",
    confidence: int = 50,
    severity: str = "Medium",
) -> dict:
    """
    Crea un STIX Indicator 2.1.

    Si name o description están vacíos utiliza automáticamente
    los valores predeterminados correspondientes al tipo
    de indicador.
    """

    pattern = build_pattern(
        indicator_type,
        value,
    )

    defaults = get_indicator_defaults(
        indicator_type
    )

    # --------------------------------------------------------
    # Nombre
    # --------------------------------------------------------

    final_name = (
        name.strip()
        if isinstance(name, str) and name.strip()
        else defaults["name"]
    )

    # --------------------------------------------------------
    # Descripción
    # --------------------------------------------------------

    final_description = (
        description.strip()
        if (
            isinstance(description, str)
            and description.strip()
        )
        else defaults["description"]
    )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    severity = (
        str(severity).strip()
        if severity
        else "Medium"
    )

    indicator = Indicator(

        name=final_name,

        description=final_description,

        indicator_types=[
            "malicious-activity"
        ],

        pattern=pattern,

        pattern_type="stix",

        valid_from=datetime.now(
            timezone.utc
        ),

        confidence=int(confidence),

        labels=[
            f"severity:{severity.lower()}"
        ],
    )

    return json.loads(
        indicator.serialize()
    )


# ============================================================
# CREAR BUNDLE
# ============================================================

def make_bundle(
    indicators: list[dict],
) -> dict:
    """
    Agrupa múltiples Indicators dentro de un STIX Bundle.
    """

    objects = [
        Indicator(
            **obj,
            allow_custom=True,
        )
        for obj in indicators
    ]

    bundle = Bundle(
        *objects,
        allow_custom=True,
    )

    return json.loads(
        bundle.serialize()
    )


# ============================================================
# EXTRAER INDICADORES DESDE TEXTO / LOG
# ============================================================

def extract_indicators(
    text: str,
) -> list[dict]:
    """
    Extrae posibles indicadores desde texto libre o logs.

    Detecta:

    - URLs
    - IPv4
    - IPv6
    - MD5
    - SHA-1
    - SHA-256
    - SHA-512
    - Emails
    - Domains
    """

    if not text.strip():
        return []

    candidates = []

    # ========================================================
    # URL
    # Se procesan primero para evitar detectar su dominio
    # como indicador separado.
    # ========================================================

    url_pattern = re.compile(
        r"(?:https?|hxxps?)://[^\s\"'<>]+",
        re.I,
    )

    for match in url_pattern.finditer(text):

        value = match.group(0).rstrip(
            ".,);]"
        )

        candidates.append(
            (
                "URL",
                value,
            )
        )

    # ========================================================
    # IPv4 / IPv6
    # ========================================================

    token_pattern = re.compile(
        r"(?<![\w.-])"
        r"(?:\d{1,3}\.){3}\d{1,3}"
        r"(?![\w.-])"
        r"|"
        r"(?<!\w)"
        r"(?:[A-Fa-f0-9]{1,4}:){2,7}"
        r"[A-Fa-f0-9]{1,4}"
        r"(?!\w)"
    )

    for match in token_pattern.finditer(text):

        kind, normalized = detect_indicator(
            match.group(0)
        )

        if kind in {
            "IPv4",
            "IPv6",
        }:

            candidates.append(
                (
                    kind,
                    normalized,
                )
            )

    # ========================================================
    # HASHES
    # ========================================================

    hash_pattern = re.compile(
        r"(?<![A-Fa-f0-9])"
        r"[A-Fa-f0-9]{32,128}"
        r"(?![A-Fa-f0-9])"
    )

    for match in hash_pattern.finditer(text):

        kind, normalized = detect_indicator(
            match.group(0)
        )

        if kind in HASH_LENGTHS.values():

            candidates.append(
                (
                    kind,
                    normalized,
                )
            )

    # ========================================================
    # EMAIL
    # ========================================================

    email_pattern = re.compile(
        r"\b"
        r"[^@\s]+"
        r"@"
        r"[^@\s]+"
        r"\."
        r"[A-Za-z]{2,63}"
        r"\b"
    )

    for match in email_pattern.finditer(text):

        candidates.append(
            (
                "Email",
                match.group(0).lower(),
            )
        )

    # ========================================================
    # DOMAIN
    # Incluye dominios normales y defanged.
    # ========================================================

    domain_pattern = re.compile(
        r"\b"
        r"(?:"
        r"[A-Za-z0-9]"
        r"(?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
        r"(?:\[.\]|\(\.\)|\.)"
        r"){1,}"
        r"[A-Za-z]{2,63}"
        r"\b"
    )

    for match in domain_pattern.finditer(text):

        raw = match.group(0)

        normalized = (
            normalize_defanged(raw)
            .lower()
        )

        # ----------------------------------------------------
        # Evitar duplicar dominios que ya forman parte
        # de una URL detectada.
        # ----------------------------------------------------

        if any(
            indicator_type == "URL"
            and normalized
            in normalize_defanged(value).lower()

            for indicator_type, value
            in candidates
        ):
            continue

        candidates.append(
            (
                "Domain",
                normalized,
            )
        )

    # ========================================================
    # ELIMINAR DUPLICADOS
    # ========================================================

    seen = set()

    results = []

    for indicator_type, value in candidates:

        key = (
            indicator_type,
            value.lower(),
        )

        if key in seen:
            continue

        seen.add(key)

        results.append(
            {
                "type": indicator_type,
                "value": value,
            }
        )

    return results
