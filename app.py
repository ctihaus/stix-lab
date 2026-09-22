import json
import streamlit as st

from data.wiki_content import COMMON_PROPERTIES_BY_FAMILY, CATEGORIES, WIKI_OBJECTS, objects_by_category
from services.converter import extract_indicators, make_bundle, make_indicator, detect_indicator
from services.quality import run_quality_checks
from services.validator import validate_stix_text

st.set_page_config(page_title="STIX Lab", page_icon="🧩", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1320px;}
.hero {padding: 1.15rem 1.35rem; border: 1px solid rgba(128,128,128,.22); border-radius: 18px; margin-bottom: 1rem;}
.hero h1 {margin:0; font-size:2.15rem;}
.hero p {margin:.3rem 0 0 0; opacity:.78;}
.soft-card {border:1px solid rgba(128,128,128,.22); border-radius:14px; padding:1rem 1.1rem; margin:.35rem 0 .8rem 0;}
.badge {display:inline-block; padding:.18rem .55rem; border-radius:999px; border:1px solid rgba(128,128,128,.28); margin-right:.35rem; font-size:.82rem;}
.small-muted {opacity:.7; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
div[data-testid="stMetricValue"] {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🧩 STIX Lab Demo</h1>
  <p>Aprende. Convierte. Valida. Una herramienta práctica para crear reportes STIX 2.1 de mejor calidad.</p>
</div>
""", unsafe_allow_html=True)

wiki_tab, converter_tab, validator_tab = st.tabs(["📚 Wiki", "🔄 Convertidor", "✅ Validador"])


def render_properties(rows, required):
    table = []
    for prop, datatype, description in rows:
        table.append({
            "Propiedad": prop,
            "Tipo": datatype,
            "Requerida": "Sí" if prop in required else "No",
            "Descripción": description,
        })
    st.dataframe(table, use_container_width=True, hide_index=True)


CATEGORY_HELP = {
    "STIX Domain Objects (SDO)": "Conceptos de alto nivel utilizados por analistas: amenazas, vulnerabilidades, reportes, indicadores, identidades y otros elementos de inteligencia.",
    "STIX Cyber-observable Objects (SCO)": "Hechos técnicos observables en hosts o redes: IP, dominios, archivos, procesos, tráfico, cuentas, correos y otros artefactos.",
    "STIX Relationship Objects (SRO)": "Objetos que conectan otros objetos STIX o registran que un objeto fue observado.",
    "Language Content Objects": "Permiten proporcionar traducciones del contenido textual de otros objetos STIX.",
    "Marking Definition Objects": "Definen reglas de manejo, distribución o uso aplicables al contenido STIX.",
}


with wiki_tab:
    st.subheader("Wiki STIX 2.1")
    st.caption("Explora los objetos STIX 2.1 por familia, revisa sus propiedades y observa cómo se vería cada objeto en JSON.")

    grouped = objects_by_category()
    total_objects = len(WIKI_OBJECTS)
    m1, m2, m3 = st.columns(3)
    m1.metric("Objetos documentados", total_objects)
    m2.metric("Familias", len(CATEGORIES))
    m3.metric("Ejemplos JSON", sum(1 for x in WIKI_OBJECTS.values() if x.get("example")))

    st.markdown("---")
    left, right = st.columns([1.05, 2.3], gap="large")

    with left:
        query = st.text_input("🔎 Buscar en la Wiki", placeholder="Ej. File, Indicator, Relationship...")

        if query.strip():
            q = query.lower().strip()
            filtered = [
                name for name, item in WIKI_OBJECTS.items()
                if q in name.lower()
                or q in item["type"].lower()
                or q in item["category"].lower()
                or q in item["summary"].lower()
            ]
            if filtered:
                selected = st.radio("Resultados", filtered, label_visibility="collapsed")
            else:
                st.info("No se encontraron objetos con ese término.")
                selected = next(iter(WIKI_OBJECTS))
        else:
            selected_category = st.selectbox("Familia STIX", CATEGORIES)
            st.caption(CATEGORY_HELP[selected_category])
            selected = st.radio(
                f"Objetos ({len(grouped[selected_category])})",
                grouped[selected_category],
                label_visibility="visible",
            )

    with right:
        item = WIKI_OBJECTS[selected]
        st.markdown(f"## {selected}")
        st.markdown(
            f"<span class='badge'>{item['family']}</span>"
            f"<span class='badge'>{item['type']}</span>"
            f"<span class='badge'>STIX 2.1</span>",
            unsafe_allow_html=True,
        )
        st.caption(item["category"])

        st.markdown(f"<div class='soft-card'><b>¿Qué representa?</b><br>{item['summary']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='soft-card'><b>¿Cuándo utilizarlo?</b><br>{item['use']}</div>", unsafe_allow_html=True)

        if item.get("note"):
            st.info(item["note"])

        common_rows = COMMON_PROPERTIES_BY_FAMILY.get(item["family"], [])
        if common_rows:
            st.markdown("### Propiedades comunes")
            with st.expander(f"Ver propiedades comunes de {item['family']}", expanded=False):
                render_properties(common_rows, set(item.get("required", [])))

        st.markdown("### Propiedades específicas")
        render_properties(item["properties"], set(item.get("required", [])))

        required_specific = [x for x in item.get("required", []) if x in {p[0] for p in item["properties"]}]
        if required_specific:
            st.caption("Propiedades específicas requeridas: " + " · ".join(f"`{x}`" for x in required_specific))

        recommended = item.get("recommended", [])
        if recommended:
            st.markdown("### Recomendaciones de calidad")
            st.write(" · ".join(f"`{x}`" for x in recommended))

        st.markdown("### Ejemplo de archivo STIX")
        st.caption("Ejemplo educativo mínimo para visualizar la estructura del objeto en un archivo JSON STIX 2.1.")
        example_payload = json.dumps(item["example"], indent=2, ensure_ascii=False)
        st.code(example_payload, language="json")

        ec1, ec2 = st.columns([1, 2])
        with ec1:
            st.download_button(
                "⬇️ Descargar ejemplo",
                example_payload,
                file_name=f"{item['type']}_example.json",
                mime="application/json",
                key=f"wiki_download_{item['type']}",
                use_container_width=True,
            )
        with ec2:
            if st.button("✅ Copiar ejemplo al Validador", key=f"wiki_validate_{item['type']}", use_container_width=True):
                st.session_state["generated_stix"] = example_payload
                st.success("Ejemplo preparado. Abre la pestaña **Validador** para validarlo.")

with converter_tab:
    st.subheader("Convertidor STIX")
    st.caption("Extrae indicadores de un log o crea un indicador manualmente y genera STIX 2.1.")

    mode = st.segmented_control("Modo", ["Log → STIX", "Constructor manual"], default="Log → STIX")

    if mode == "Log → STIX":
        sample = """2026-09-21 10:31:02 action=blocked src_ip=185.234.72.15\nurl=hxxp://malicious-example[.]com/login\nsha256=7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5"""
        log_text = st.text_area("Pega un log, alerta o texto", value=sample, height=180)
        if st.button("Analizar", type="primary", use_container_width=False):
            st.session_state["extracted"] = extract_indicators(log_text)

        extracted = st.session_state.get("extracted", [])
        if extracted:
            st.markdown("### Indicadores detectados")
            selected_rows = []
            for i, row in enumerate(extracted):
                cols = st.columns([.55, 1.15, 4])
                with cols[0]:
                    enabled = st.checkbox("Usar", value=True, key=f"ioc_{i}", label_visibility="collapsed")
                with cols[1]:
                    st.code(row["type"], language=None)
                with cols[2]:
                    st.code(row["value"], language=None)
                if enabled:
                    selected_rows.append(row)

            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                severity = st.selectbox("Severidad", ["Medium", "High", "Critical"], key="bulk_sev")
            with c2:
                confidence = st.slider("Confidence", 0, 100, 70, key="bulk_conf")
            with c3:
                st.write("")
                st.write("")
                generate = st.button("Generar Bundle", type="primary")

            if generate:
                indicators = []
                for row in selected_rows:
                    indicators.append(make_indicator(
                        row["type"], row["value"],
                        name=f"Indicador {row['type']}: {row['value'][:60]}",
                        description="Indicador extraído de una muestra de log mediante STIX Lab.",
                        confidence=confidence, severity=severity,
                    ))
                bundle = make_bundle(indicators)
                payload = json.dumps(bundle, indent=2, ensure_ascii=False)
                st.session_state["generated_stix"] = payload
                st.success(f"Bundle generado con {len(indicators)} indicador(es).")
                st.code(payload, language="json")
                st.download_button("Descargar JSON", payload, file_name="stix_bundle.json", mime="application/json")
        else:
            st.info("Pulsa **Analizar** para extraer IPs, dominios, URLs, hashes y correos electrónicos.")

    else:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            indicator_type = st.selectbox("Tipo de indicador", ["IPv4", "IPv6", "Domain", "URL", "Email", "MD5", "SHA-1", "SHA-256", "SHA-512"])
            value = st.text_input("Valor", placeholder="Ej. 185.234.72.15")
            name = st.text_input("Nombre", placeholder="Ej. IP asociada a actividad maliciosa")
            description = st.text_area("Descripción", placeholder="Explica dónde se detectó y por qué es relevante.")
            severity = st.selectbox("Severidad", ["Medium", "High", "Critical"])
            confidence = st.slider("Confidence", 0, 100, 70)
            valid_type, normalized = detect_indicator(value) if value else (None, "")
            if value and valid_type and valid_type != indicator_type:
                st.warning(f"El valor parece ser **{valid_type}**, pero seleccionaste **{indicator_type}**.")
            if st.button("Generar STIX", type="primary"):
                try:
                    obj = make_indicator(indicator_type, value, name, description, confidence, severity)
                    payload = json.dumps(obj, indent=2, ensure_ascii=False)
                    st.session_state["generated_stix"] = payload
                except Exception as exc:
                    st.error(f"No se pudo generar el objeto: {exc}")
        with c2:
            st.markdown("### STIX generado")
            payload = st.session_state.get("generated_stix")
            if payload:
                st.code(payload, language="json")
                st.download_button("Descargar JSON", payload, file_name="indicator.json", mime="application/json", key="download_manual")
            else:
                st.info("Completa el formulario y genera un objeto para verlo aquí.")

with validator_tab:
    st.subheader("Validador STIX")
    st.caption("Comprueba por separado la conformidad con STIX 2.1 y las reglas de calidad del reporte.")

    default_text = st.session_state.get("generated_stix", "")
    uploaded = st.file_uploader("Cargar archivo JSON", type=["json"])
    if uploaded is not None:
        default_text = uploaded.getvalue().decode("utf-8", errors="replace")

    validation_text = st.text_area("STIX JSON", value=default_text, height=360, placeholder="Pega aquí un objeto o Bundle STIX 2.1...")
    if st.button("Validar", type="primary"):
        if not validation_text.strip():
            st.warning("Primero pega o carga una muestra STIX.")
        else:
            result = validate_stix_text(validation_text)
            st.markdown("### 1. Conformidad STIX")
            m1, m2, m3 = st.columns(3)
            m1.metric("JSON", "✅ Válido" if result["json_ok"] else "❌ Inválido")
            m2.metric("STIX 2.1", "✅ Válido" if result["stix_ok"] else "❌ Con errores")
            m3.metric("Advertencias", len(result["warnings"]))

            if result["errors"]:
                st.error("Se encontraron errores de conformidad.")
                for err in result["errors"]:
                    st.write(f"- ❌ {err}")
            elif result["stix_ok"]:
                st.success("La muestra cumple la validación STIX ejecutada por el validador OASIS.")

            if result["warnings"]:
                with st.expander("Advertencias del validador STIX", expanded=True):
                    for warning in result["warnings"]:
                        st.write(f"- ⚠️ {warning}")

            st.markdown("### 2. Calidad del reporte")
            if result["json_ok"]:
                quality = run_quality_checks(result["data"])
                counts = {
                    "ok": sum(1 for x in quality if x["level"] == "ok"),
                    "warning": sum(1 for x in quality if x["level"] == "warning"),
                    "error": sum(1 for x in quality if x["level"] == "error"),
                }
                q1, q2, q3 = st.columns(3)
                q1.metric("Correcto", counts["ok"])
                q2.metric("Advertencias", counts["warning"])
                q3.metric("Errores", counts["error"])

                for item in quality:
                    icon = {"ok": "✅", "warning": "⚠️", "error": "❌"}[item["level"]]
                    st.write(f"{icon} **{item['rule']}** — {item['message']}  \n`{item['object']}`")

st.divider()
st.caption("STIX Lab · Herramienta educativa basada en STIX 2.1. Para decisiones normativas, consulte siempre la especificación oficial de OASIS.")
