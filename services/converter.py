import json
import re
from datetime import datetime, timezone
from ipaddress import ip_address
from urllib.parse import urlparse

from stix2.v21 import Bundle, Indicator

HASH_LENGTHS = {32: "MD5", 40: "SHA-1", 64: "SHA-256", 128: "SHA-512"}


def _escape_stix(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def normalize_defanged(value: str) -> str:
    return (
        value.strip()
        .replace("hxxps://", "https://")
        .replace("hxxp://", "http://")
        .replace("[.]", ".")
        .replace("(.)", ".")
    )


def detect_indicator(value: str):
    raw = normalize_defanged(value)

    try:
        parsed_ip = ip_address(raw)
        return ("IPv4" if parsed_ip.version == 4 else "IPv6", str(parsed_ip))
    except ValueError:
        pass

    if re.fullmatch(r"[A-Fa-f0-9]+", raw) and len(raw) in HASH_LENGTHS:
        return (HASH_LENGTHS[len(raw)], raw.lower())

    if raw.lower().startswith(("http://", "https://")):
        parsed = urlparse(raw)
        if parsed.netloc:
            return ("URL", raw)

    if re.fullmatch(r"(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}", raw):
        return ("Domain", raw.lower())

    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", raw):
        return ("Email", raw.lower())

    return (None, raw)


def build_pattern(indicator_type: str, value: str) -> str:
    value = normalize_defanged(value)
    safe = _escape_stix(value)
    mappings = {
        "IPv4": f"[ipv4-addr:value = '{safe}']",
        "IPv6": f"[ipv6-addr:value = '{safe}']",
        "Domain": f"[domain-name:value = '{safe}']",
        "URL": f"[url:value = '{safe}']",
        "Email": f"[email-addr:value = '{safe}']",
        "MD5": f"[file:hashes.MD5 = '{safe.lower()}']",
        "SHA-1": f"[file:hashes.'SHA-1' = '{safe.lower()}']",
        "SHA-256": f"[file:hashes.'SHA-256' = '{safe.lower()}']",
        "SHA-512": f"[file:hashes.'SHA-512' = '{safe.lower()}']",
    }
    if indicator_type not in mappings:
        raise ValueError(f"Tipo de indicador no soportado: {indicator_type}")
    return mappings[indicator_type]


def make_indicator(indicator_type: str, value: str, name: str, description: str,
                   confidence: int = 50, severity: str = "Medium") -> dict:
    pattern = build_pattern(indicator_type, value)
    indicator = Indicator(
        name=name.strip() or f"Indicador {indicator_type}",
        description=description.strip() or "Indicador generado con STIX Lab.",
        indicator_types=["malicious-activity"],
        pattern=pattern,
        pattern_type="stix",
        valid_from=datetime.now(timezone.utc),
        confidence=int(confidence),
        labels=[f"severity:{severity.lower()}"],
    )
    return json.loads(indicator.serialize())


def make_bundle(indicators: list[dict]) -> dict:
    objects = [Indicator(**obj, allow_custom=True) for obj in indicators]
    bundle = Bundle(*objects, allow_custom=True)
    return json.loads(bundle.serialize())


def extract_indicators(text: str) -> list[dict]:
    if not text.strip():
        return []

    candidates = []

    # URLs first to avoid splitting their domains into duplicate candidates.
    url_pattern = re.compile(r"(?:https?|hxxps?)://[^\s\"'<>]+", re.I)
    for match in url_pattern.finditer(text):
        candidates.append(("URL", match.group(0).rstrip(".,);]")))

    # IPs (v4 and broad v6 candidates)
    token_pattern = re.compile(r"(?<![\w.-])(?:\d{1,3}\.){3}\d{1,3}(?![\w.-])|(?<!\w)(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}(?!\w)")
    for match in token_pattern.finditer(text):
        kind, normalized = detect_indicator(match.group(0))
        if kind in {"IPv4", "IPv6"}:
            candidates.append((kind, normalized))

    # Hashes
    for match in re.finditer(r"(?<![A-Fa-f0-9])[A-Fa-f0-9]{32,128}(?![A-Fa-f0-9])", text):
        kind, normalized = detect_indicator(match.group(0))
        if kind in HASH_LENGTHS.values():
            candidates.append((kind, normalized))

    # Emails
    for match in re.finditer(r"\b[^@\s]+@[^@\s]+\.[A-Za-z]{2,63}\b", text):
        candidates.append(("Email", match.group(0).lower()))

    # Defanged and normal domains
    domain_pattern = re.compile(r"\b(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\[\.\]|\(\.\)|\.)){1,}[A-Za-z]{2,63}\b")
    for match in domain_pattern.finditer(text):
        raw = match.group(0)
        normalized = normalize_defanged(raw).lower()
        # Ignore a domain if already part of a detected URL.
        if any(t == "URL" and normalized in normalize_defanged(v).lower() for t, v in candidates):
            continue
        candidates.append(("Domain", normalized))

    seen = set()
    results = []
    for indicator_type, value in candidates:
        key = (indicator_type, value.lower())
        if key in seen:
            continue
        seen.add(key)
        results.append({"type": indicator_type, "value": value})

    return results
