import streamlit as st
import json
import re
from groq import Groq

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL DINÁMICO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="BetBrothers.AI • Centro Cuantitativo Pro",
    page_icon="⚡",
    layout="wide"
)

# Estilos CSS personalizados para un look moderno, animado y llamativo (Neón/Dark Mode)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    /* Tarjetas personalizadas con efecto flotante y borde brillante */
    div.st-emotion-cache-1r6slb0, div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background: rgba(30, 41, 59, 0.7);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div.st-emotion-cache-1r6slb0:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.6);
        box-shadow: 0 20px 30px -10px rgba(56, 189, 248, 0.2);
    }
    /* Botones llamativos con degradado */
    .stButton > button {
        background: linear-gradient(90deg, #3b82f6 0%, #10b981 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        background: linear-gradient(90deg, #2563eb 0%, #059669 100%);
    }
    /* Títulos con brillo */
    h1, h2, h3 {
        letter-spacing: -0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GESTIÓN DE ESTADO (Lista vacía al inicio por defecto)
# -----------------------------------------------------------------------------
if "modo_activo" not in st.session_state:
    st.session_state.modo_activo = "futbol"

if "lista_enlaces" not in st.session_state:
    st.session_state.lista_enlaces = []

# -----------------------------------------------------------------------------
# CALENDARIO OFICIAL PRECARGADO (LIGA NACIONAL DE ECUAVÓLEY)
# -----------------------------------------------------------------------------
PARTIDOS_ESTRELLAS_ECUAVOLEY = [
    {
        "partido": "Quito Capitalinos vs. Ibarra Norteños",
        "estrellas": "⭐⭐⭐",
        "etiqueta": "🔥 Partido Estelar de la Jornada (3v3)",
        "fecha": "Viernes 28 de agosto - 16:00",
        "sede": "Quito - Coliseo de Sangolquí",
        "url": "https://lne-ec.com/calendario/quito-capitalinos-ibarra-nortenos"
    },
    {
        "partido": "Quito Granaderos vs. Santo Domingo Tsáchilas",
        "estrellas": "⭐⭐⭐",
        "etiqueta": "⚡ Choque de Alto Poderío",
        "fecha": "Viernes 28 de agosto - 16:00",
        "sede": "Quito - Coliseo de Sangolquí",
        "url": "https://lne-ec.com/calendario/quito-granaderos-santo-domingo"
    },
    {
        "partido": "Latacunga Sultanes vs. Tena Jaguares",
        "estrellas": "⭐⭐",
        "etiqueta": "🎯 Duelo Regional Destacado",
        "fecha": "Jueves 27 de agosto - 16:00",
        "sede": "Riobamba - Coliseo Teodoro Gallegos Borja",
        "url": "https://lne-ec.com/calendario/latacunga-sultanes-tena-jaguares"
    },
    {
        "partido": "Riobamba Hieleros vs. Ambato Diablos",
        "estrellas": "⭐⭐",
        "etiqueta": "💥 Clásico Interandino",
        "fecha": "Jueves 27 de agosto - 16:00",
        "sede": "Riobamba - Coliseo Teodoro Gallegos Borja",
        "url": "https://lne-ec.com/calendario/riobamba-hieleros-ambato-diablos"
    },
    {
        "partido": "Loja Escuderos vs. Machala Mineros",
        "estrellas": "⭐⭐",
        "etiqueta": "🚀 Duelo del Austro",
        "fecha": "Sábado 29 de agosto - 16:00",
        "sede": "Cuenca - Coliseo Universidad Católica",
        "url": "https://lne-ec.com/calendario/loja-escuderos-machala-mineros"
    }
]

# -----------------------------------------------------------------------------
# FUNCIÓN IA (GROQ) CON EL PROMPT ESPECIALIZADO DE FÚTBOL Y ECUAVOLEY
# -----------------------------------------------------------------------------
def analizar_por_enlace_o_texto(identificador_partido, url_flashscore, groq_api_key, es_ecuavoley=False):
    client = Groq(api_key=groq_api_key)
    
    if es_ecuavoley:
        prompt = f"""
        Actúa como un Analista Deportivo y Especialista Cuantitativo en Ecuavoley Profesional (Modalidad 3v3). Tu objetivo es realizar un análisis probabilístico y táctico 100% objetivo para el siguiente desafío: '{identificador_partido}' (Ref LNE: {url_flashscore}).
        
        Evalúa rendimiento, roles (Colocador, Volador, Ponedor/Servidor) y ventajas tácticas sin sesgos.
        
        Devuelve ÚNICAMENTE un objeto JSON válido con esta estructura exacta y limpia:
        {{
            "competencia": "LIGA NACIONAL DE ECUAVOLEY 3V3 (lne-ec.com)",
            "horario": "Calendario Oficial",
            "trío_local": "Trío Local (Colocador / Volador / Ponedor)",
            "trío_visitante": "Trío Retador (Colocador / Volador / Ponedor)",
            "favorito_ganador": "Trío con mayor probabilidad de victoria",
            "cuota_ganador": 1.88,
            "probabilidad_ganador": "62.5%",
            "sugerencia_doble_oportunidad": "Trío Local o Empate (Gana o Empata)",
            "cuota_doble_oportunidad": 1.25,
            "comparativa_roles": "Evaluación detallada de la potencia del colocador, cobertura del volador y precisión de alzada del servidor.",
            "estado_forma_tríos": "Excelente racha en batidas largas y gran solidez en canchas abiertas.",
            "choque_estilos": "Disputa táctica entre juego aéreo/potencia vs. colocación y defensa rápida en la bomba.",
            "ganador_primer_quince": "Trío Local (15-11)",
            "ganador_segundo_quince": "Trío Visitante (13-15)",
            "probabilidad_definicion": "Se extiende a un 3er Quince (2-1 en sets)",
            "proyeccion_puntos_totales": "Más de 42.5 puntos globales en el encuentro",
            "marcador_proyectado": "15-12 / 13-15 / 15-10",
            "dominio_batida": "Alta efectividad desacomodando la recepción rival con saques colocados a la línea.",
            "efectividad_cambio_defensa": "88.0% de efectividad en el primer ataque tras alzada; excelente rescate en esquinas.",
            "valor_apuesta_mercado": "EV Positivo (+7.4%) en victoria ajustada",
            "nivel_confianza": "Alto",
            "stake_recomendado": "2/10",
            "recomendacion_1xbet": "Apuesta a ganador de trío / Más de 41.5 puntos"
        }}
        """
    else:
        prompt = f"""
        Actúa como Analista Cuantitativo de Apuestas Deportivas especializado en modelos predictivos de Poisson. Analiza: '{identificador_partido}' (URL: {url_flashscore}).
        Incluye métricas detalladas de saques de esquina (Córners), tarjetas amarillas/rojas y la sugerencia de Doble Oportunidad (Gana o Empata).
        Devuelve ÚNICAMENTE un objeto JSON válido con esta estructura exacta y sin texto adicional:
        {{
            "competencia": "LIGA PROFESIONAL",
            "horario": "Próximo",
            "equipo_local": "Local",
            "equipo_visitante": "Visitante",
            "favorito_ganador": "Favorito",
            "cuota_ganador": 1.75,
            "probabilidad_ganador": "55.0%",
            "sugerencia_doble_oportunidad": "Local o Empata (1X)",
            "cuota_doble_oportunidad": 1.22,
            "goles_esperados_local": 1.75,
            "goles_esperados_visitante": 0.95,
            "total_goles_estimado": 2.7,
            "tendencia_goles_veredicto": "Inclinación clara hacia MÁS DE 2.5 GOLES (Over).",
            "analisis_mas_menos_goles": "Mediante Poisson, el xG combinado arroja 2.70 goles esperados.",
            "estado_forma_local": "Invicto en los últimos 5 partidos como local.",
            "estado_forma_visitante": "Irregular fuera de casa, acumula 2 derrotas recientes.",
            "metrica_xg_local": "xGF: 1.82 / xGA: 0.85",
            "metrica_xg_visitante": "xGF: 1.15 / xGA: 1.40",
            "bajas_confirmadas": "Sin bajas destacadas.",
            "prob_ambos_anotan": "53.0%",
            "prob_gol_1t": "80.0%",
            "prob_gol_2t": "92.0%",
            "prob_over_15": "78.0%",
            "prob_over_25": "55.0%",
            "prob_over_35": "33.0%",
            "remates_total_partido": "24.5",
            "remates_local": "14.0",
            "remates_visitante": "10.5",
            "jugadores_clave_remates": "Delantero centro local",
            "corners_total": "10.5",
            "corners_local": "6.0",
            "corners_visitante": "4.5",
            "analisis_corners": "Promedio alto de saques de esquina debido al volumen ofensivo por bandas.",
            "tarjetas_estimadas": "4.2 amonestaciones totales",
            "tarjetas_local": "2.2 tarjetas",
            "tarjetas_visitante": "2.0 tarjetas",
            "analisis_tarjetas": "Encuentro de alta intensidad física en el medio campo con tendencia a superar las 3.5 tarjetas.",
            "valor_ev": "EV Positivo (+7.2%)",
            "estrategia_apuesta": "Más de 2.5 Goles y Triunfo Local",
            "nivel_confianza": "Alto",
            "stake_recomendado": "2/10",
            "parley_combinada": "Victoria Local + Más de 1.5 Goles",
            "cuota_parley": 1.92
        }}
        """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "Eres un analista cuantitativo experto. Responde exclusivamente con el objeto JSON solicitado."},
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-20b",
        temperature=0.2,
    )
    raw = chat_completion.choices[0].message.content.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    return json.loads(match.group(0) if match else raw)

# -----------------------------------------------------------------------------
# INTERFAZ PRINCIPAL CON TOQUE DINÁMICO Y MODERNO
# -----------------------------------------------------------------------------
st.title("⚡ BetBrothers.AI • Centro Cuantitativo Pro")
st.markdown("<p style='color: #38bdf8; font-weight: 600; font-size: 1.1rem;'>Plataforma Inteligente de Análisis Predictivo • Betano & 1xBet Ecuador</p>", unsafe_allow_html=True)

col_btn1, col_btn2, col_space = st.columns([1.5, 1.5, 4])
with col_btn1:
    if st.button("⚽ Fútbol Profesional", key="nav_fut_nativ", use_container_width=True):
        st.session_state.modo_activo = "futbol"
        st.rerun()
with col_btn2:
    if st.button("🏐 Ecuavoley Ecuador", key="nav_ecu_nativ", use_container_width=True):
        st.session_state.modo_activo = "ecuavoley"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

selected_matches_from_calendar = []

if st.session_state.modo_activo == "ecuavoley":
    st.markdown("### 🏐 MODO ECUAVOLEY DE ECUADOR ACTIVADO")
    st.info("Selecciona los duelos estelares de la Liga Nacional de Ecuavóley (lne-ec.com) para activar el motor cuantitativo 3v3.")
    
    st.markdown("#### ⭐ Cartelera de Partidos Oficiales")
    
    for idx_item, item in enumerate(PARTIDOS_ESTRELLAS_ECUAVOLEY):
        with st.container():
            col_info, col_sel = st.columns([5, 1])
            with col_info:
                st.caption(f"🗓️ {item['fecha']} | 📍 {item['sede']} — {item['estrellas']}")
                st.markdown(f"**{item['partido']}**")
                st.success(item['etiqueta'])
            with col_sel:
                st.write("") 
                if st.checkbox("Analizar", key=f"chk_ecu_nativ_{idx_item}"):
                    selected_matches_from_calendar.append(item['url'])
else:
    st.markdown("### ⚽ MODO FÚTBOL PROFESIONAL ACTIVADO (BETANO)")
    st.info("Añade tus enlaces de Flashscore para el análisis dinámico de cuotas y goles.")
    
    col_input_nuevo, col_add_btn = st.columns([5, 1])
    with col_input_nuevo:
        nuevo_enlace_input = st.text_input(
            "Añadir nuevo enlace",
            placeholder="Ej: https://www.flashscore.es/partido/arsenal-chelsea/",
            label_visibility="collapsed",
            key="input_nuevo_enlace_nativo"
        )
    with col_add_btn:
        if st.button("➕ Añadir", key="btn_add_url_nativo", use_container_width=True):
            if nuevo_enlace_input.strip() and nuevo_enlace_input.strip() not in st.session_state.lista_enlaces:
                st.session_state.lista_enlaces.append(nuevo_enlace_input.strip())
                st.rerun()

    # IMPORTANTE: Al entrar, la lista inicia vacía por defecto y solo muestra elementos si el usuario los agrega.
    if not st.session_state.lista_enlaces:
        st.info("💡 No hay enlaces agregados todavía. Ingresa uno arriba y presiona 'Añadir'.")
    else:
        for i, enlace in enumerate(list(st.session_state.lista_enlaces)):
            col_l, col_del = st.columns([6, 1])
            with col_l:
                url_editada = st.text_input(f"Partido {i+1}", value=enlace, key=f"enlace_nativo_item_{i}", label_visibility="collapsed")
                st.session_state.lista_enlaces[i] = url_editada
            with col_del:
                if st.button("🗑️", key=f"del_nativo_item_{i}", help="Eliminar enlace"):
                    if i < len(st.session_state.lista_enlaces):
                        st.session_state.lista_enlaces.pop(i)
                        st.rerun()

enlaces_a_procesar = []
if st.session_state.modo_activo == "ecuavoley":
    if selected_matches_from_calendar:
        enlaces_a_procesar.extend(selected_matches_from_calendar)
else:
    enlaces_a_procesar.extend(st.session_state.lista_enlaces)

# -----------------------------------------------------------------------------
# APARTADO DE INVERSIÓN
# -----------------------------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
with st.container():
    st.markdown("### 💵 Configuración de Inversión / Stake")
    monto_apuesta = st.number_input("Inversión Monto ($)", value=10.0, step=5.0, label_visibility="collapsed", key="inversion_nativa_input")

groq_key = "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"

st.markdown("<br>", unsafe_allow_html=True)
btn_ejecutar = st.button("🚀 EJECUTAR MOTOR PREDICTIVO INTELIGENTE", use_container_width=True, type="primary")

st.markdown("---")
st.markdown("### 📊 Panel de Resultados y Proyecciones")

if btn_ejecutar:
    if not groq_key.strip():
        st.error("⚠️ Verifica tu Clave API de Groq.")
    elif not enlaces_a_procesar or not any(e.strip() for e in enlaces_a_procesar):
        st.warning("⚠️ Añade o selecciona al menos un partido válido para continuar.")
    else:
        lista_urls_limpia = [e.strip() for e in enlaces_a_procesar if e.strip()]
        es_ecuavoley_actual = (st.session_state.modo_activo == "ecuavoley")
        
        with st.spinner("⚡ Procesando algoritmos de alta precisión..."):
            try:
                cuota_total = 1.0
                resultados = []

                for url in lista_urls_limpia:
                    match_slug = url.split("/")[-1] if len(url.split("/")) > 1 else url
                    datos = analizar_por_enlace_o_texto(match_slug, url, groq_key, es_ecuavoley=es_ecuavoley_actual)
                    cuota_pick = float(datos.get("cuota_ganador", 1.85))
                    
                    cuota_total *= cuota_pick
                    resultados.append({"datos": datos, "cuota_pick": cuota_pick, "url": url})

                ganancia_total = monto_apuesta * cuota_total
                neta = ganancia_total - monto_apuesta

                nombre_casa = "1xBet Ecuador" if es_ecuavoley_actual else "Betano"
                url_casa = "https://1xbet.ec/es" if es_ecuavoley_actual else "https://ec.betano.com/"

                with st.container():
                    col_res1, col_res2 = st.columns(2)
                    with col_res1:
                        st.metric(f"💎 Cuota Total Combinada ({nombre_casa})", f"{cuota_total:.2f}")
                        st.text(f"Inversión Base: ${monto_apuesta:.2f}")
                    with col_res2:
                        st.metric("🚀 Retorno Estimado", f"${ganancia_total:.2f}", delta=f"+${neta:.2f} Neto")

                st.markdown("<br>", unsafe_allow_html=True)

                for idx, res in enumerate(resultados):
                    d = res["datos"]
                    cp = res["cuota_pick"]
                    u = res["url"]

                    with st.container():
                        st.caption(f"📌 {d.get('competencia')} • {d.get('horario')}")
                        
                        if es_ecuavoley_actual:
                            st.markdown(f"### 🏐 {d.get('trío_local')} vs 🛡️ {d.get('trío_visitante')}")
                        else:
                            st.markdown(f"### ⚽ {d.get('equipo_local')} vs ✈️ {d.get('equipo_visitante')}")
                        
                        col_faiv1, col_faiv2 = st.columns(2)
                        with col_faiv1:
                            st.info(f"🏆 **Favorito:** {d.get('favorito_ganador')}")
                        with col_faiv2:
                            st.success(f"📈 **Probabilidad:** {d.get('probabilidad_ganador')} | **Cuota:** {cp:.2f}")

                        # Sugerencia de Doble Oportunidad (Gana o Empata)
                        st.warning(f"🛡️ **Sugerencia Doble Oportunidad:** {d.get('sugerencia_doble_oportunidad')} (Cuota aprox: {d.get('cuota_doble_oportunidad', 1.25)})")

                        if es_ecuavoley_actual:
                            st.markdown("#### 1. Análisis Métrico y Táctico de los Tríos")
                            st.write(f"- **Roles Clave (Colocador, Volador, Ponedor):** {d.get('comparativa_roles')}")
                            st.write(f"- **Estado de Forma:** {d.get('estado_forma_tríos')}")
                            st.write(f"- **Choque de Estilos:** {d.get('choque_estilos')}")

                            st.markdown("#### 2. Estimación Probabilística (%)")
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.metric("1er Quince", d.get('ganador_primer_quince'))
                            with col_m2:
                                st.metric("2do Quince", d.get('ganador_segundo_quince'))
                            with col_m3:
                                st.metric("Definición", d.get('probabilidad_definicion'))

                            st.markdown("#### 3. Proyección de Puntos y Factores Clave")
                            st.warning(f"🎯 **Línea Proyectada:** {d.get('proyeccion_puntos_totales')} (Marcador: {d.get('marcador_proyectado')})")
                            st.write(f"- **Dominio en la Batida:** {d.get('dominio_batida')}")
                            st.write(f"- **Efectividad y Defensa:** {d.get('efectividad_cambio_defensa')}")

                            st.markdown("#### 4. Matriz de Riesgo y Valor")
                            st.write(f"- **Valor de Mercado:** {d.get('valor_apuesta_mercado')}")
                            st.write(f"- **Confianza & Stake:** {d.get('nivel_confianza')} (Stake: {d.get('stake_recomendado')})")
                            st.write(f"- **Estrategia 1xBet:** {d.get('recomendacion_1xbet')}")
                        else:
                            st.markdown("#### 1. Estado de Forma")
                            st.write(f"- **Local:** {d.get('estado_forma_local')}")
                            st.write(f"- **Visitante:** {d.get('estado_forma_visitante')}")
                            st.write(f"- **Métricas xG:** Local [{d.get('metrica_xg_local')}] vs Visitante [{d.get('metrica_xg_visitante')}]")

                            st.markdown("#### 2. Probabilidades de Mercado")
                            col_m1, col_m2, col_m3 = st.columns(3)
                            with col_m1:
                                st.metric("Ambos Anotan", d.get('prob_ambos_anotan'))
                            with col_m2:
                                st.metric("Gol 1er T", d.get('prob_gol_1t'))
                            with col_m3:
                                st.metric("Gol 2do T", d.get('prob_gol_2t'))

                            st.markdown("#### 3. Análisis de Goles (Over / Under)")
                            st.warning(f"🎯 **Veredicto:** {d.get('tendencia_goles_veredicto')}")
                            st.write(d.get('analisis_mas_menos_goles'))

                            st.markdown("#### 4. Córners (Saques de Esquina) y Tarjetas")
                            col_c1, col_c2 = st.columns(2)
                            with col_c1:
                                st.metric("🚩 Córners Estimados", f"{d.get('corners_total', '10.5')}", f"Local: {d.get('corners_local', '6.0')} | Vis: {d.get('corners_visitante', '4.5')}")
                                st.write(d.get('analisis_corners', ''))
                            with col_c2:
                                st.metric("🟨 Tarjetas Estimadas", f"{d.get('tarjetas_estimadas', '4.2')}", f"Local: {d.get('tarjetas_local', '2.2')} | Vis: {d.get('tarjetas_visitante', '2.0')}")
                                st.write(d.get('analisis_tarjetas', ''))

                            st.markdown("#### 5. Recomendación Final y Valor")
                            st.write(f"- **Valor EV:** {d.get('valor_ev')}")
                            st.write(f"- **Apuesta Sugerida:** {d.get('estrategia_apuesta')}")
                            st.write(f"- **Stake Recomendado:** {d.get('stake_recomendado')} ({d.get('nivel_confianza')})")
                            st.write(f"- **Combinada (Bet Builder):** {d.get('parley_combinada')} (Cuota: {d.get('cuota_parley')})")

                        st.markdown("<br>", unsafe_allow_html=True)
                        col_lks1, col_lks2 = st.columns(2)
                        with col_lks1:
                            st.link_button("🌐 Ver Calendario Oficial ↗", u, use_container_width=True)
                        with col_lks2:
                            st.link_button(f"🔥 Apostar en {nombre_casa} ↗", url_casa, use_container_width=True)
                        
                        st.markdown("---")

            except Exception as e:
                st.error(f"❌ Error al procesar el motor predictivo: {e}.")