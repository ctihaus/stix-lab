import json
import streamlit as st
from services.ai_converter import (
    analyze_log_with_ai,
    get_ai_usage,
    AIConverterError,
    AIRateLimitError,
)

from data.wiki_content import (
    COMMON_PROPERTIES_BY_FAMILY,
    CATEGORIES,
    WIKI_OBJECTS,
    objects_by_category,
)

from services.converter import (
    extract_indicators,
    make_bundle,
    make_indicator,
    detect_indicator,
    get_indicator_defaults,
)

from services.quality import run_quality_checks
from services.validator import validate_stix_text


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="STIX Lab",
    page_icon="🧩",
    layout="wide",
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1320px;
    }

    .hero {
        padding: 1.15rem 1.35rem;
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 18px;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.15rem;
    }

    .hero p {
        margin: .3rem 0 0 0;
        opacity: .78;
    }

    .soft-card {
        border: 1px solid rgba(128,128,128,.22);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin: .35rem 0 .8rem 0;
    }

    .badge {
        display: inline-block;
        padding: .18rem .55rem;
        border-radius: 999px;
        border: 1px solid rgba(128,128,128,.28);
        margin-right: .35rem;
        font-size: .82rem;
    }

    .small-muted {
        opacity: .7;
        font-size: .9rem;
    }

    div[data-testid="stMetricValue"] {
        font-size: 16px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🧩 STIX Lab Demo</h1>
        <p>
            Aprende. Convierte. Valida.
            Una herramienta práctica para crear reportes
            STIX 2.1 de mejor calidad.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

wiki_tab, converter_tab, validator_tab = st.tabs(
    [
        "📚 Wiki",
        "🔄 Convertidor",
        "✅ Validador",
    ]
)


# ============================================================
# HELPERS DE INTERFAZ
# ============================================================

def render_properties(rows, required):

    table = []

    for prop, datatype, description in rows:

        table.append(
            {
                "Propiedad": prop,
                "Tipo": datatype,
                "Requerida": (
                    "Sí"
                    if prop in required
                    else "No"
                ),
                "Descripción": description,
            }
        )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )


def update_manual_defaults():
    """
    Se ejecuta automáticamente cuando cambia el tipo
    de indicador del Constructor manual.

    Actualiza Nombre y Descripción con textos apropiados
    para el nuevo tipo seleccionado.
    """

    indicator_type = st.session_state.get(
        "manual_indicator_type",
        "IPv4",
    )

    defaults = get_indicator_defaults(
        indicator_type
    )

    st.session_state["manual_name"] = (
        defaults["name"]
    )

    st.session_state["manual_description"] = (
        defaults["description"]
    )


# ============================================================
# AYUDA DE CATEGORÍAS WIKI
# ============================================================

CATEGORY_HELP = {

    "STIX Domain Objects (SDO)":
        (
            "Conceptos de alto nivel utilizados por analistas: "
            "amenazas, vulnerabilidades, reportes, indicadores, "
            "identidades y otros elementos de inteligencia."
        ),

    "STIX Cyber-observable Objects (SCO)":
        (
            "Hechos técnicos observables en hosts o redes: IP, "
            "dominios, archivos, procesos, tráfico, cuentas, "
            "correos y otros artefactos."
        ),

    "STIX Relationship Objects (SRO)":
        (
            "Objetos que conectan otros objetos STIX o registran "
            "que un objeto fue observado."
        ),

    "Language Content Objects":
        (
            "Permiten proporcionar traducciones del contenido "
            "textual de otros objetos STIX."
        ),

    "Marking Definition Objects":
        (
            "Definen reglas de manejo, distribución o uso "
            "aplicables al contenido STIX."
        ),
}


# ============================================================
# WIKI
# ============================================================

with wiki_tab:

    st.subheader("Wiki STIX 2.1")

    st.caption(
        "Explora los objetos STIX 2.1 por familia, "
        "revisa sus propiedades y observa cómo se vería "
        "cada objeto en JSON."
    )

    grouped = objects_by_category()

    total_objects = len(
        WIKI_OBJECTS
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Objetos documentados",
        total_objects,
    )

    m2.metric(
        "Familias",
        len(CATEGORIES),
    )

    m3.metric(
        "Ejemplos JSON",
        sum(
            1
            for x in WIKI_OBJECTS.values()
            if x.get("example")
        ),
    )

    st.markdown("---")

    left, right = st.columns(
        [1.05, 2.3],
        gap="large",
    )

    # --------------------------------------------------------
    # MENÚ
    # --------------------------------------------------------

    with left:

        query = st.text_input(
            "🔎 Buscar en la Wiki",
            placeholder=(
                "Ej. File, Indicator, Relationship..."
            ),
        )

        if query.strip():

            q = query.lower().strip()

            filtered = [
                name
                for name, item
                in WIKI_OBJECTS.items()
                if (
                    q in name.lower()
                    or q in item["type"].lower()
                    or q in item["category"].lower()
                    or q in item["summary"].lower()
                )
            ]

            if filtered:

                selected = st.radio(
                    "Resultados",
                    filtered,
                    label_visibility="collapsed",
                )

            else:

                st.info(
                    "No se encontraron objetos "
                    "con ese término."
                )

                selected = next(
                    iter(WIKI_OBJECTS)
                )

        else:

            selected_category = st.selectbox(
                "Familia STIX",
                CATEGORIES,
            )

            st.caption(
                CATEGORY_HELP[
                    selected_category
                ]
            )

            selected = st.radio(
                (
                    f"Objetos "
                    f"({len(grouped[selected_category])})"
                ),
                grouped[selected_category],
                label_visibility="visible",
            )

    # --------------------------------------------------------
    # CONTENIDO
    # --------------------------------------------------------

    with right:

        item = WIKI_OBJECTS[
            selected
        ]

        st.markdown(
            f"## {selected}"
        )

        st.markdown(
            f"<span class='badge'>{item['family']}</span>"
            f"<span class='badge'>{item['type']}</span>"
            f"<span class='badge'>STIX 2.1</span>",
            unsafe_allow_html=True,
        )

        st.caption(
            item["category"]
        )

        st.markdown(
            (
                "<div class='soft-card'>"
                "<b>¿Qué representa?</b><br>"
                f"{item['summary']}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                "<div class='soft-card'>"
                "<b>¿Cuándo utilizarlo?</b><br>"
                f"{item['use']}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        if item.get("note"):

            st.info(
                item["note"]
            )

        # ----------------------------------------------------
        # PROPIEDADES COMUNES
        # ----------------------------------------------------

        common_rows = (
            COMMON_PROPERTIES_BY_FAMILY.get(
                item["family"],
                [],
            )
        )

        if common_rows:

            st.markdown(
                "### Propiedades comunes"
            )

            with st.expander(
                (
                    "Ver propiedades comunes "
                    f"de {item['family']}"
                ),
                expanded=False,
            ):

                render_properties(
                    common_rows,
                    set(
                        item.get(
                            "required",
                            [],
                        )
                    ),
                )

        # ----------------------------------------------------
        # PROPIEDADES ESPECÍFICAS
        # ----------------------------------------------------

        st.markdown(
            "### Propiedades específicas"
        )

        render_properties(
            item["properties"],
            set(
                item.get(
                    "required",
                    [],
                )
            ),
        )

        specific_property_names = {
            prop[0]
            for prop
            in item["properties"]
        }

        required_specific = [
            x
            for x in item.get(
                "required",
                [],
            )
            if x in specific_property_names
        ]

        if required_specific:

            st.caption(
                "Propiedades específicas requeridas: "
                + " · ".join(
                    f"`{x}`"
                    for x
                    in required_specific
                )
            )

        # ----------------------------------------------------
        # RECOMENDACIONES
        # ----------------------------------------------------

        recommended = item.get(
            "recommended",
            [],
        )

        if recommended:

            st.markdown(
                "### Recomendaciones de calidad"
            )

            st.write(
                " · ".join(
                    f"`{x}`"
                    for x
                    in recommended
                )
            )

        # ----------------------------------------------------
        # EJEMPLO JSON
        # ----------------------------------------------------

        st.markdown(
            "### Ejemplo de archivo STIX"
        )

        st.caption(
            "Ejemplo educativo mínimo para visualizar "
            "la estructura del objeto en un archivo "
            "JSON STIX 2.1."
        )

        example_payload = json.dumps(
            item["example"],
            indent=2,
            ensure_ascii=False,
        )

        st.code(
            example_payload,
            language="json",
        )

        ec1, ec2 = st.columns(
            [1, 2]
        )

        with ec1:

            st.download_button(
                "⬇️ Descargar ejemplo",
                example_payload,
                file_name=(
                    f"{item['type']}"
                    "_example.json"
                ),
                mime="application/json",
                key=(
                    f"wiki_download_"
                    f"{item['type']}"
                ),
                use_container_width=True,
            )

        with ec2:

            if st.button(
                "✅ Copiar ejemplo al Validador",
                key=(
                    f"wiki_validate_"
                    f"{item['type']}"
                ),
                use_container_width=True,
            ):

                st.session_state[
                    "generated_stix"
                ] = example_payload

                st.success(
                    "Ejemplo preparado. "
                    "Abre la pestaña **Validador** "
                    "para validarlo."
                )


# ============================================================
# CONVERTIDOR
# ============================================================

with converter_tab:

    st.subheader(
        "Convertidor STIX"
    )

    st.caption(
        "Extrae indicadores de un log, crea un indicador manualmente "
        "o utiliza IA para interpretar eventos y generar STIX 2.1."
    )

    mode = st.segmented_control(
        "Modo",
    [
        "Log → STIX",
        "Constructor manual",
        "✨ AI Converter",
    ],
        default="Log → STIX",
        key="converter_mode",
    )

    # ========================================================
    # LOG -> STIX
    # ========================================================

    if mode == "Log → STIX":

        sample = (
            "2026-09-21 10:31:02 "
            "action=blocked "
            "src_ip=185.234.72.15\n"
            "url=hxxp://malicious-example[.]com/login\n"
            "sha256="
            "7600ffe12da441fe89d035b13801e8e91"
            "d064bc544a27b19a5cf49f6ab8b18f5"
        )

        log_text = st.text_area(
            "Pega un log, alerta o texto",
            value=sample,
            height=180,
        )

        if st.button(
            "Analizar",
            type="primary",
            use_container_width=False,
        ):

            st.session_state[
                "extracted"
            ] = extract_indicators(
                log_text
            )

        extracted = st.session_state.get(
            "extracted",
            [],
        )

        if extracted:

            st.markdown(
                "### Indicadores detectados"
            )

            selected_rows = []

            for i, row in enumerate(
                extracted
            ):

                cols = st.columns(
                    [.55, 1.15, 4]
                )

                with cols[0]:

                    enabled = st.checkbox(
                        "Usar",
                        value=True,
                        key=f"ioc_{i}",
                        label_visibility="collapsed",
                    )

                with cols[1]:

                    st.code(
                        row["type"],
                        language=None,
                    )

                with cols[2]:

                    st.code(
                        row["value"],
                        language=None,
                    )

                if enabled:

                    selected_rows.append(
                        row
                    )

            c1, c2, c3 = st.columns(
                [2, 2, 1]
            )

            with c1:

                severity = st.selectbox(
                    "Severidad",
                    [
                        "Medium",
                        "High",
                        "Critical",
                    ],
                    key="bulk_sev",
                )

            with c2:

                confidence = st.slider(
                    "Confidence",
                    0,
                    100,
                    70,
                    key="bulk_conf",
                )

            with c3:

                st.write("")
                st.write("")

                generate = st.button(
                    "Generar Bundle",
                    type="primary",
                )

            if generate:

                indicators = []

                for row in selected_rows:

                    indicators.append(
                        make_indicator(
                            row["type"],
                            row["value"],
                            name=(
                                f"Indicador "
                                f"{row['type']}: "
                                f"{row['value'][:60]}"
                            ),
                            description=(
                                "Indicador extraído de una "
                                "muestra de log mediante "
                                "STIX Lab."
                            ),
                            confidence=confidence,
                            severity=severity,
                        )
                    )

                bundle = make_bundle(
                    indicators
                )

                payload = json.dumps(
                    bundle,
                    indent=2,
                    ensure_ascii=False,
                )

                st.session_state[
                    "generated_stix"
                ] = payload

                st.success(
                    (
                        "Bundle generado con "
                        f"{len(indicators)} "
                        "indicador(es)."
                    )
                )

                st.code(
                    payload,
                    language="json",
                )

                st.download_button(
                    "Descargar JSON",
                    payload,
                    file_name="stix_bundle.json",
                    mime="application/json",
                )

        else:

            st.info(
                "Pulsa **Analizar** para extraer "
                "IPs, dominios, URLs, hashes "
                "y correos electrónicos."
            )

    # ========================================================
    # CONSTRUCTOR MANUAL
    # ========================================================

    elif mode == "Constructor manual":

        c1, c2 = st.columns(
            2,
            gap="large",
        )

        with c1:

            # ------------------------------------------------
            # TIPO DE INDICADOR
            # ------------------------------------------------

            indicator_type = st.selectbox(
                "Tipo de indicador",
                [
                    "IPv4",
                    "IPv6",
                    "Domain",
                    "URL",
                    "Email",
                    "MD5",
                    "SHA-1",
                    "SHA-256",
                    "SHA-512",
                ],
                key="manual_indicator_type",
                on_change=update_manual_defaults,
            )

            # Obtener defaults correspondientes
            # al tipo actualmente seleccionado
            defaults = get_indicator_defaults(
                indicator_type
            )

            # ------------------------------------------------
            # INICIALIZAR NOMBRE Y DESCRIPCIÓN
            # ------------------------------------------------

            if (
                "manual_name"
                not in st.session_state
            ):

                st.session_state[
                    "manual_name"
                ] = defaults["name"]

            if (
                "manual_description"
                not in st.session_state
            ):

                st.session_state[
                    "manual_description"
                ] = defaults[
                    "description"
                ]

            # ------------------------------------------------
            # VALOR
            # ------------------------------------------------

            value = st.text_input(
                "Valor",
                placeholder=defaults[
                    "placeholder"
                ],
                key="manual_value",
            )

            # ------------------------------------------------
            # NOMBRE
            # ------------------------------------------------

            name = st.text_input(
                "Nombre",
                key="manual_name",
            )

            # ------------------------------------------------
            # DESCRIPCIÓN
            # ------------------------------------------------

            description = st.text_area(
                "Descripción",
                key="manual_description",
                height=110,
            )

            # ------------------------------------------------
            # SEVERIDAD
            # ------------------------------------------------

            severity = st.selectbox(
                "Severidad",
                [
                    "Medium",
                    "High",
                    "Critical",
                ],
                key="manual_severity",
            )

            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            confidence = st.slider(
                "Confidence",
                0,
                100,
                70,
                key="manual_confidence",
            )

            # ------------------------------------------------
            # DETECCIÓN AUTOMÁTICA
            # ------------------------------------------------

            valid_type, normalized = (
                detect_indicator(value)
                if value
                else (None, "")
            )

            if (
                value
                and valid_type
                and valid_type
                != indicator_type
            ):

                st.warning(
                    (
                        "El valor parece ser "
                        f"**{valid_type}**, "
                        "pero seleccionaste "
                        f"**{indicator_type}**."
                    )
                )

            # ------------------------------------------------
            # GENERAR STIX
            # ------------------------------------------------

            if st.button(
                "Generar STIX",
                type="primary",
                key="generate_manual_stix",
            ):

                if not value.strip():

                    st.warning(
                        "Introduce un valor para "
                        "el indicador."
                    )

                else:

                    try:

                        obj = make_indicator(
                            indicator_type,
                            value,
                            name,
                            description,
                            confidence,
                            severity,
                        )

                        payload = json.dumps(
                            obj,
                            indent=2,
                            ensure_ascii=False,
                        )

                        st.session_state[
                            "generated_stix"
                        ] = payload

                    except Exception as exc:

                        st.error(
                            (
                                "No se pudo generar "
                                f"el objeto: {exc}"
                            )
                        )

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        with c2:

            st.markdown(
                "### STIX generado"
            )

            payload = st.session_state.get(
                "generated_stix"
            )

            if payload:

                st.code(
                    payload,
                    language="json",
                )

                st.download_button(
                    "Descargar JSON",
                    payload,
                    file_name="indicator.json",
                    mime="application/json",
                    key="download_manual",
                )

            else:

                st.info(
                    "Completa el formulario y "
                    "genera un objeto para verlo aquí."
                )

    # ========================================================
    # AI CONVERTER
    # ========================================================

    elif mode == "✨ AI Converter":

        st.markdown("### ✨ AI Converter")

        st.caption(
            "Utiliza un modelo de lenguaje de pesos abiertos alojado en "
            "Cloudflare Workers AI para interpretar logs, identificar "
            "indicadores y convertir el resultado a STIX 2.1."
        )

        st.info(
            "La IA se utiliza para interpretar y extraer contexto. "
            "La construcción final de STIX continúa realizándose con "
            "las funciones determinísticas de STIX Lab."
        )

        # ----------------------------------------------------
        # CONFIGURACIÓN DEL WORKER
        # ----------------------------------------------------

        try:
            worker_url = st.secrets["AI_WORKER_URL"]
            worker_secret = st.secrets["AI_WORKER_SECRET"]
            ai_configured = True

        except KeyError:
            worker_url = None
            worker_secret = None
            ai_configured = False

        if not ai_configured:

            st.error(
                "AI Converter no está configurado. Agrega "
                "`AI_WORKER_URL` y `AI_WORKER_SECRET` en los "
                "Secrets de Streamlit."
            )

        else:

            # =================================================
            # CONTADOR GLOBAL DE USO
            # =================================================

            usage = None
            usage_error = None

            try:
                usage = get_ai_usage(
                    worker_url,
                    worker_secret,
                )

            except AIConverterError as exc:
                usage_error = str(exc)

            if usage_error:
                st.warning(
                    "No fue posible consultar el contador global de IA: "
                    f"{usage_error}"
                )

            if usage:

                used = int(
                    usage.get("used", 0)
                )

                remaining = int(
                    usage.get("remaining", 0)
                )

                daily_limit = int(
                    usage.get("limit", 0)
                )

                usage_date = usage.get(
                    "date",
                    "",
                )

                u1, u2, u3 = st.columns(3)

                u1.metric(
                    "Solicitudes utilizadas",
                    used,
                )

                u2.metric(
                    "Solicitudes restantes",
                    remaining,
                )

                u3.metric(
                    "Límite diario",
                    daily_limit,
                )

                if daily_limit > 0:
                    st.progress(
                        min(
                            used / daily_limit,
                            1.0,
                        )
                    )

                if usage_date:
                    st.caption(
                        f"Cuota global correspondiente a {usage_date}. "
                        "El contador se reinicia diariamente a las "
                        "00:00 UTC."
                    )
                else:
                    st.caption(
                        "El contador es global para todos los usuarios "
                        "y se reinicia diariamente a las 00:00 UTC."
                    )

            else:
                # Si no se pudo consultar la cuota, dejamos el botón
                # disponible. El Worker seguirá aplicando el límite real.
                remaining = None
                daily_limit = None

            st.divider()

            # =================================================
            # ENTRADA DEL LOG
            # =================================================

            ai_sample = (
                "2026-10-20 14:20:13 event=firewall action=blocked\\n"
                "src_ip=10.10.4.25 dst_ip=185.234.72.15\\n"
                "url=hxxp://malicious-example[.]com/login\\n"
                "sha256="
                "7600ffe12da441fe89d035b13801e8e91"
                "d064bc544a27b19a5cf49f6ab8b18f5\\n"
                "message=Multiple outbound connections were blocked."
            )

            ai_log = st.text_area(
                "Log, alerta o evento",
                value=ai_sample,
                height=220,
                key="ai_log",
            )

            MAX_AI_LOG_CHARS = 12000

            char_count = len(ai_log)

            st.caption(
                f"{char_count:,} / "
                f"{MAX_AI_LOG_CHARS:,} caracteres"
            )

            log_too_large = (
                char_count > MAX_AI_LOG_CHARS
            )

            if log_too_large:
                st.error(
                    "El contenido supera el tamaño máximo permitido "
                    f"de {MAX_AI_LOG_CHARS:,} caracteres."
                )

            limit_reached = (
                remaining is not None
                and remaining <= 0
            )

            if limit_reached:
                st.warning(
                    "Se alcanzó el límite global de análisis con IA "
                    "para hoy."
                )

            analyze_button = st.button(
                "✨ Analizar con IA",
                type="primary",
                key="ai_analyze_button",
                disabled=(
                    log_too_large
                    or limit_reached
                    or not ai_log.strip()
                ),
            )

            # =================================================
            # LLAMADA AL WORKER
            # =================================================

            if analyze_button:

                # Eliminar un análisis anterior para no confundirlo
                # con una solicitud nueva que pueda fallar.
                st.session_state.pop(
                    "ai_analysis",
                    None,
                )

                try:

                    with st.spinner(
                        "Analizando el evento con IA..."
                    ):
                        ai_response = analyze_log_with_ai(
                            ai_log,
                            worker_url,
                            worker_secret,
                        )

                    st.session_state[
                        "ai_analysis"
                    ] = ai_response.get(
                        "analysis",
                        {},
                    )

                    st.session_state[
                        "ai_usage"
                    ] = ai_response.get(
                        "usage",
                        {},
                    )

                    st.success(
                        "Análisis completado correctamente."
                    )

                    # Fuerza un rerun para que el contador superior
                    # consulte nuevamente D1 y refleje el nuevo consumo.
                    st.rerun()

                except AIRateLimitError as exc:

                    st.error(
                        "Se alcanzó el límite diario de análisis con IA."
                    )

                    if getattr(exc, "usage", None):
                        st.session_state[
                            "ai_usage"
                        ] = exc.usage

                except AIConverterError as exc:

                    st.error(
                        f"No fue posible completar el análisis: {exc}"
                    )

                except Exception as exc:

                    st.error(
                        "Ocurrió un error inesperado durante el análisis: "
                        f"{exc}"
                    )

            # =================================================
            # RESULTADO DEL ANÁLISIS
            # =================================================

            analysis = st.session_state.get(
                "ai_analysis"
            )

            if analysis:

                st.divider()

                st.markdown(
                    "### Resultado del análisis"
                )

                summary = analysis.get(
                    "summary",
                    "",
                )

                if summary:
                    st.markdown("**Resumen**")
                    st.write(summary)

                a1, a2 = st.columns(2)

                with a1:
                    st.metric(
                        "Severidad sugerida",
                        analysis.get(
                            "severity",
                            "-",
                        ),
                    )

                with a2:
                    st.metric(
                        "Confidence",
                        analysis.get(
                            "confidence",
                            "-",
                        ),
                    )

                indicators_found = analysis.get(
                    "indicators",
                    [],
                )

                st.markdown(
                    "### Indicadores identificados"
                )

                if not indicators_found:

                    st.info(
                        "El modelo no identificó indicadores "
                        "en la muestra."
                    )

                else:

                    selected_ai_indicators = []

                    for i, indicator in enumerate(
                        indicators_found
                    ):

                        ai_type = str(
                            indicator.get(
                                "type",
                                "",
                            )
                        ).strip()

                        ai_value = str(
                            indicator.get(
                                "value",
                                "",
                            )
                        ).strip()

                        ai_description = str(
                            indicator.get(
                                "description",
                                "",
                            )
                        ).strip()

                        # Validación determinística adicional de la
                        # salida del LLM antes de generar STIX.
                        detected_type, normalized_value = (
                            detect_indicator(ai_value)
                            if ai_value
                            else (None, "")
                        )

                        indicator_is_valid = (
                            detected_type is not None
                        )

                        type_matches = (
                            indicator_is_valid
                            and detected_type == ai_type
                        )

                        cols = st.columns(
                            [.45, 1.1, 3.1, 4]
                        )

                        with cols[0]:

                            enabled = st.checkbox(
                                "Usar",
                                value=(
                                    indicator_is_valid
                                ),
                                key=f"ai_ioc_{i}",
                                label_visibility="collapsed",
                                disabled=(
                                    not indicator_is_valid
                                ),
                            )

                        with cols[1]:
                            st.code(
                                ai_type,
                                language=None,
                            )

                        with cols[2]:
                            st.code(
                                ai_value,
                                language=None,
                            )

                        with cols[3]:
                            st.caption(
                                ai_description
                                or "Sin descripción."
                            )

                            if not indicator_is_valid:
                                st.error(
                                    "Formato no reconocido por "
                                    "el convertidor determinístico."
                                )

                            elif not type_matches:
                                st.warning(
                                    "La IA lo clasificó como "
                                    f"{ai_type}, pero STIX Lab "
                                    f"detecta {detected_type}. "
                                    "Se usará la clasificación "
                                    "determinística."
                                )

                        if enabled and indicator_is_valid:

                            selected_ai_indicators.append(
                                {
                                    "type": detected_type,
                                    "value": (
                                        normalized_value
                                        or ai_value
                                    ),
                                    "description": (
                                        ai_description
                                        or (
                                            "Indicador identificado "
                                            "mediante análisis "
                                            "asistido por IA."
                                        )
                                    ),
                                }
                            )

                    # =========================================
                    # GENERAR STIX
                    # =========================================

                    if selected_ai_indicators:

                        st.markdown(
                            "### Generar STIX"
                        )

                        st.caption(
                            "Solo los indicadores seleccionados y "
                            "validados por las reglas determinísticas "
                            "de STIX Lab serán incluidos."
                        )

                        if st.button(
                            "Generar STIX desde análisis IA",
                            type="primary",
                            key="generate_ai_stix",
                        ):

                            try:

                                stix_indicators = []

                                ai_confidence = int(
                                    analysis.get(
                                        "confidence",
                                        50,
                                    )
                                )

                                ai_confidence = max(
                                    0,
                                    min(
                                        ai_confidence,
                                        100,
                                    ),
                                )

                                ai_severity = analysis.get(
                                    "severity",
                                    "Medium",
                                )

                                if ai_severity not in {
                                    "Medium",
                                    "High",
                                    "Critical",
                                }:
                                    ai_severity = "Medium"

                                for item in selected_ai_indicators:

                                    stix_indicators.append(
                                        make_indicator(
                                            indicator_type=item[
                                                "type"
                                            ],
                                            value=item[
                                                "value"
                                            ],
                                            name=(
                                                f"Indicador "
                                                f"{item['type']}: "
                                                f"{item['value'][:60]}"
                                            ),
                                            description=item[
                                                "description"
                                            ],
                                            confidence=ai_confidence,
                                            severity=ai_severity,
                                        )
                                    )

                                bundle = make_bundle(
                                    stix_indicators
                                )

                                payload = json.dumps(
                                    bundle,
                                    indent=2,
                                    ensure_ascii=False,
                                )

                                st.session_state[
                                    "generated_stix"
                                ] = payload

                                st.success(
                                    "Bundle generado con "
                                    f"{len(stix_indicators)} "
                                    "indicador(es)."
                                )

                                st.code(
                                    payload,
                                    language="json",
                                )

                                st.download_button(
                                    "Descargar STIX",
                                    payload,
                                    file_name=(
                                        "ai_stix_bundle.json"
                                    ),
                                    mime="application/json",
                                    key="download_ai_stix",
                                )

                            except Exception as exc:

                                st.error(
                                    "No fue posible generar el "
                                    f"STIX: {exc}"
                                )

                    else:

                        st.warning(
                            "No hay indicadores válidos "
                            "seleccionados para generar STIX."
                        )


# ============================================================
# VALIDADOR
# ============================================================

with validator_tab:

    st.subheader(
        "Validador STIX"
    )

    st.caption(
        "Comprueba por separado la conformidad "
        "con STIX 2.1 y las reglas de calidad "
        "del reporte."
    )

    default_text = st.session_state.get(
        "generated_stix",
        "",
    )

    uploaded = st.file_uploader(
        "Cargar archivo JSON",
        type=["json"],
    )

    if uploaded is not None:

        default_text = (
            uploaded
            .getvalue()
            .decode(
                "utf-8",
                errors="replace",
            )
        )

    validation_text = st.text_area(
        "STIX JSON",
        value=default_text,
        height=360,
        placeholder=(
            "Pega aquí un objeto o "
            "Bundle STIX 2.1..."
        ),
    )

    if st.button(
        "Validar",
        type="primary",
    ):

        if not validation_text.strip():

            st.warning(
                "Primero pega o carga "
                "una muestra STIX."
            )

        else:

            result = validate_stix_text(
                validation_text
            )

            # =================================================
            # CONFORMIDAD STIX
            # =================================================

            st.markdown(
                "### 1. Conformidad STIX"
            )

            m1, m2, m3 = st.columns(3)

            m1.metric(
                "JSON",
                (
                    "✅ Válido"
                    if result["json_ok"]
                    else "❌ Inválido"
                ),
            )

            m2.metric(
                "STIX 2.1",
                (
                    "✅ Válido"
                    if result["stix_ok"]
                    else "❌ Con errores"
                ),
            )

            m3.metric(
                "Advertencias",
                len(
                    result["warnings"]
                ),
            )

            if result["errors"]:

                st.error(
                    "Se encontraron errores "
                    "de conformidad."
                )

                for err in result[
                    "errors"
                ]:

                    st.write(
                        f"- ❌ {err}"
                    )

            elif result["stix_ok"]:

                st.success(
                    "La muestra cumple la "
                    "validación STIX ejecutada "
                    "por el validador OASIS."
                )

            if result["warnings"]:

                with st.expander(
                    (
                        "Advertencias del "
                        "validador STIX"
                    ),
                    expanded=True,
                ):

                    for warning in result[
                        "warnings"
                    ]:

                        st.write(
                            f"- ⚠️ {warning}"
                        )

            # =================================================
            # CALIDAD
            # =================================================

            st.markdown(
                "### 2. Calidad del reporte"
            )

            if result["json_ok"]:

                quality = run_quality_checks(
                    result["data"]
                )

                counts = {

                    "ok": sum(
                        1
                        for x in quality
                        if x["level"] == "ok"
                    ),

                    "warning": sum(
                        1
                        for x in quality
                        if x["level"]
                        == "warning"
                    ),

                    "error": sum(
                        1
                        for x in quality
                        if x["level"]
                        == "error"
                    ),
                }

                q1, q2, q3 = st.columns(3)

                q1.metric(
                    "Correcto",
                    counts["ok"],
                )

                q2.metric(
                    "Advertencias",
                    counts["warning"],
                )

                q3.metric(
                    "Errores",
                    counts["error"],
                )

                # --------------------------------------------
                # RESULTADOS AGRUPADOS
                # --------------------------------------------

                for item in quality:

                    icon = {
                        "ok": "✅",
                        "warning": "⚠️",
                        "error": "❌",
                    }[
                        item["level"]
                    ]

                    st.markdown(
                        (
                            f"#### {icon} "
                            f"{item['rule']}"
                        )
                    )

                    st.write(
                        item["message"]
                    )

                    affected = item.get(
                        "affected",
                        [],
                    )

                    if affected:

                        with st.expander(
                            (
                                "Ver objetos afectados "
                                f"({len(affected)})"
                            )
                        ):

                            for obj_id in affected:

                                st.code(
                                    obj_id,
                                    language=None,
                                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "STIX Lab · Herramienta educativa basada en "
    "STIX 2.1. Para decisiones normativas, consulte "
    "siempre la especificación oficial de OASIS."
)
