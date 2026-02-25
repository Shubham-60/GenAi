import time

import streamlit as st


THRESHOLD = 0.58
INCOME_OPTIONS = {
    "1 — Less than $10,000": 1,
    "2 — $10,000 to < $15,000": 2,
    "3 — $15,000 to < $20,000": 3,
    "4 — $20,000 to < $25,000": 4,
    "5 — $25,000 to < $35,000": 5,
    "6 — $35,000 to < $50,000": 6,
    "7 — $50,000 to < $75,000": 7,
    "8 — $75,000 or more": 8,
}


def init_session_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "form"
    if "form_values" not in st.session_state:
        st.session_state.form_values = {}
    if "features" not in st.session_state:
        st.session_state.features = {}
    if "risk_probability" not in st.session_state:
        st.session_state.risk_probability = None
    if "risk_class" not in st.session_state:
        st.session_state.risk_class = None
    if "needs_prediction" not in st.session_state:
        st.session_state.needs_prediction = False


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --medical-blue: #2E86C1;
                --medical-blue-deep: #1F6FA7;
                --medical-cyan: #4FB3D9;
                --app-bg: #F8F9FA;
                --card-bg: #FFFFFF;
                --text-main: #1F2937;
                --text-muted: #6B7280;
                --border-soft: #E5E7EB;
                --shadow-soft: 0 12px 30px rgba(30, 41, 59, 0.08);
                --success: #2E7D32;
                --warning: #F59E0B;
                --danger: #D32F2F;
            }

            html {
                scroll-behavior: smooth;
            }

            .stApp *,
            .stApp *::before,
            .stApp *::after {
                box-sizing: border-box;
            }

            .stApp {
                background: linear-gradient(140deg, #edf7fc 0%, #f5fbff 42%, #eef8f2 100%);
                color: var(--text-main);
                background-attachment: fixed;
            }

            .block-container {
                max-width: 1020px;
                padding-top: 3.6rem;
                padding-bottom: 2rem;
            }

            [data-testid="stHeader"] {
                background: rgba(248, 249, 250, 0.88);
                backdrop-filter: blur(8px);
                border-bottom: 1px solid rgba(148, 163, 184, 0.22);
            }

            .hero-shell {
                background: linear-gradient(115deg, rgba(46, 134, 193, 0.09), rgba(79, 179, 217, 0.08));
                border: 1px solid rgba(46, 134, 193, 0.16);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 26px rgba(46, 134, 193, 0.08);
                animation: riseIn 420ms ease-out;
            }

            .hero-chip {
                display: inline-block;
                background: rgba(46, 134, 193, 0.12);
                color: var(--medical-blue-deep);
                border: 1px solid rgba(46, 134, 193, 0.24);
                border-radius: 999px;
                font-size: 0.75rem;
                font-weight: 650;
                padding: 0.2rem 0.55rem;
                margin-bottom: 0.45rem;
            }

            .hero-title {
                font-size: 2.05rem;
                font-weight: 760;
                color: var(--text-main);
                margin-bottom: 0.2rem;
                letter-spacing: -0.01em;
            }

            .hero-subtitle {
                font-size: 0.98rem;
                color: var(--text-muted);
                margin-bottom: 0.2rem;
            }

            [data-testid="stVerticalBlockBorderWrapper"] {
                position: relative;
                overflow: hidden;
                border-radius: 18px;
                border: 1px solid var(--border-soft);
                box-shadow: var(--shadow-soft);
                background: var(--card-bg);
                padding: 1rem 1.1rem;
                animation: riseIn 360ms ease-out;
            }

            [data-testid="stVerticalBlockBorderWrapper"]::before {
                content: "";
                position: absolute;
                top: 0;
                left: -110%;
                width: 120%;
                height: 100%;
                background: linear-gradient(105deg, transparent, rgba(255, 255, 255, 0.4), transparent);
                animation: cardSheen 7.5s ease-in-out infinite;
                pointer-events: none;
            }

            .section-shell {
                display: flex;
                gap: 0.75rem;
                align-items: flex-start;
                padding: 0.75rem 0.9rem;
                border-radius: 14px;
                border: 1px solid rgba(46, 134, 193, 0.16);
                background: linear-gradient(115deg, rgba(46, 134, 193, 0.08), rgba(79, 179, 217, 0.06));
                box-shadow: 0 12px 24px rgba(31, 111, 167, 0.08);
                margin-bottom: 0.6rem;
                animation: floatIn 360ms ease-out;
            }

            .section-accent {
                width: 6px;
                min-height: 44px;
                border-radius: 999px;
                background: linear-gradient(180deg, var(--medical-blue-deep), var(--medical-cyan));
                box-shadow: 0 6px 14px rgba(46, 134, 193, 0.25);
            }

            .section-title {
                font-size: 1.1rem;
                font-weight: 650;
                color: var(--text-main);
                margin-bottom: 0.4rem;
            }

            .section-caption {
                color: var(--text-muted);
                margin-bottom: 0.8rem;
                font-size: 0.9rem;
            }

            hr.section-divider {
                border: none;
                border-top: 1px solid var(--border-soft);
                margin: 0.2rem 0 1rem 0;
            }

            .helper-text {
                color: var(--text-muted);
                font-size: 0.8rem;
                margin-top: -0.35rem;
                margin-bottom: 0.7rem;
            }

            .risk-percentage {
                font-size: 3rem;
                font-weight: 750;
                line-height: 1;
                color: var(--text-main);
                margin-bottom: 0.6rem;
            }

            .score-grid {
                display: flex;
                gap: 1.5rem;
                align-items: center;
                flex-wrap: wrap;
                padding: 0.35rem 0.2rem 0.2rem;
            }

            .score-ring {
                --score: 0;
                --ring-color: #2E86C1;
                width: 176px;
                height: 176px;
                border-radius: 50%;
                flex-shrink: 0;
                margin: 0.2rem 0.4rem 0.2rem 0.1rem;
                background: conic-gradient(
                    from -90deg,
                    #2E7D32 0 30%,
                    #F59E0B 30% 60%,
                    #D32F2F 60% 100%
                );
                display: grid;
                place-items: center;
                position: relative;
                box-shadow: 0 18px 30px rgba(31, 111, 167, 0.18);
                animation: floatIn 420ms ease-out;
            }

            .score-ring::before {
                content: "";
                position: absolute;
                width: 130px;
                height: 130px;
                border-radius: 50%;
                background: #FFFFFF;
                box-shadow: inset 0 0 20px rgba(148, 163, 184, 0.16);
                z-index: 2;
            }

            .score-ring::after {
                content: "";
                position: absolute;
                inset: 0;
                border-radius: 50%;
                background: conic-gradient(
                    from -90deg,
                    transparent 0 calc(var(--score) * 1%),
                    #E9EEF4 calc(var(--score) * 1%) 100%
                );
                z-index: 1;
            }

            .score-center {
                position: relative;
                text-align: center;
                z-index: 3;
            }

            .score-value {
                font-size: 2.2rem;
                font-weight: 760;
                color: var(--text-main);
                margin-bottom: 0.1rem;
            }

            .score-label {
                font-size: 0.85rem;
                color: var(--text-muted);
            }

            .score-metrics {
                flex: 1;
                min-width: 240px;
            }

            .metric-row {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                gap: 0.75rem;
                margin-bottom: 0.6rem;
            }

            div[data-testid="stToggle"] div[role="switch"] {
                width: 48px;
                height: 26px;
                padding: 2px;
                background: #D1D5DB;
                border-radius: 999px;
                box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.45);
                transition: background 180ms ease, box-shadow 180ms ease;
            }

            div[data-testid="stToggle"] div[role="switch"][aria-checked="true"] {
                background: linear-gradient(120deg, var(--medical-blue-deep), var(--medical-cyan));
                box-shadow: 0 8px 18px rgba(46, 134, 193, 0.32);
            }

            div[data-testid="stToggle"] div[role="switch"] > div {
                width: 22px;
                height: 22px;
                border-radius: 999px;
                background: #FFFFFF;
                box-shadow: 0 6px 14px rgba(30, 41, 59, 0.18);
                transition: transform 180ms ease;
            }

            div[data-testid="stToggle"] div[role="switch"][aria-checked="true"] > div {
                transform: translateX(22px);
            }

            .metric-card {
                border-radius: 12px;
                border: 1px solid rgba(148, 163, 184, 0.2);
                background: rgba(255, 255, 255, 0.8);
                padding: 0.6rem 0.75rem;
                box-shadow: 0 10px 20px rgba(30, 41, 59, 0.08);
                animation: floatIn 420ms ease-out;
            }

            .metric-title {
                font-size: 0.78rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.25rem;
            }

            .metric-value {
                font-size: 1.05rem;
                font-weight: 700;
                color: var(--text-main);
            }

            .risk-track {
                width: 100%;
                height: 14px;
                background: #E9EEF4;
                border-radius: 999px;
                overflow: hidden;
                margin: 0.35rem 0 1rem 0;
            }

            .risk-fill {
                height: 14px;
                border-radius: 999px;
                transition: width 460ms ease-in-out;
                box-shadow: 0 0 10px rgba(46, 134, 193, 0.25);
            }

            .badge {
                display: inline-block;
                padding: 0.25rem 0.65rem;
                border-radius: 999px;
                font-size: 0.8rem;
                font-weight: 650;
                margin-bottom: 0.4rem;
            }

            .badge-green {
                color: #14532D;
                background: #DCFCE7;
            }

            .badge-red {
                color: #7F1D1D;
                background: #FEE2E2;
            }

            .assessment {
                font-size: 1.1rem;
                font-weight: 640;
                margin-bottom: 0.2rem;
            }

            .result-note {
                color: var(--text-muted);
                font-size: 0.9rem;
            }

            .disclaimer {
                margin-top: 1.25rem;
                text-align: center;
                font-size: 0.82rem;
                color: var(--text-muted);
                background: rgba(255, 255, 255, 0.62);
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 12px;
                padding: 0.55rem 0.7rem;
            }

            .loading-chip {
                margin-top: 0.5rem;
                color: var(--medical-blue-deep);
                font-weight: 600;
                font-size: 0.92rem;
                animation: pulseFade 1.1s ease-in-out infinite;
            }

            .loader-shell {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 0.75rem;
                padding: 2rem 1.5rem;
                border-radius: 16px;
                border: 1px solid rgba(46, 134, 193, 0.18);
                background: linear-gradient(120deg, rgba(46, 134, 193, 0.08), rgba(79, 179, 217, 0.06));
                box-shadow: 0 12px 24px rgba(31, 111, 167, 0.08);
            }

            .loader-orbit {
                width: 110px;
                height: 110px;
                border-radius: 50%;
                background: conic-gradient(
                    from 0deg,
                    rgba(46, 134, 193, 0.1),
                    rgba(46, 134, 193, 0.6),
                    rgba(46, 134, 193, 0.1)
                );
                display: grid;
                place-items: center;
                animation: orbitSpin 1.1s linear infinite;
                position: relative;
            }

            .loader-orbit::before {
                content: "";
                width: 74px;
                height: 74px;
                border-radius: 50%;
                background: #FFFFFF;
                box-shadow: inset 0 0 18px rgba(148, 163, 184, 0.2);
            }

            .loader-dot {
                position: absolute;
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background: #2E86C1;
                box-shadow: 0 6px 14px rgba(46, 134, 193, 0.35);
                transform: translate(0, -55px);
            }

            .loader-text {
                font-size: 0.95rem;
                color: var(--text-muted);
            }

            div[data-baseweb="select"] > div,
            .stNumberInput input,
            .stTextInput input {
                border-radius: 11px !important;
                border: 1px solid #D6E2ED !important;
                background: #FBFDFF !important;
                transition: border-color 150ms ease, box-shadow 150ms ease;
            }

            div[data-baseweb="select"] > div:focus-within,
            .stNumberInput input:focus,
            .stTextInput input:focus {
                border-color: rgba(46, 134, 193, 0.55) !important;
                box-shadow: 0 0 0 4px rgba(46, 134, 193, 0.15) !important;
            }

            div.stButton > button[kind="primary"] {
                background: linear-gradient(118deg, var(--medical-blue-deep), var(--medical-blue), var(--medical-cyan));
                background-size: 200% 200%;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0.68rem 1rem;
                font-weight: 650;
                transition: transform 120ms ease-in-out, box-shadow 170ms ease-in-out;
                box-shadow: 0 10px 22px rgba(46, 134, 193, 0.26);
                animation: gradientShift 5.5s ease infinite;
            }

            div.stButton > button[kind="primary"]:hover {
                transform: translateY(-2px);
                box-shadow: 0 13px 24px rgba(46, 134, 193, 0.31);
            }

            div.stButton > button[kind="secondary"] {
                border-radius: 12px;
                border: 1px solid #CAD8E6;
                color: #1F2937;
                background: #FDFEFF;
                font-weight: 600;
            }

            @keyframes gradientShift {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            @keyframes pulseFade {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.55; }
            }

            @keyframes riseIn {
                from {
                    opacity: 0;
                    transform: translateY(8px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes floatIn {
                from {
                    opacity: 0;
                    transform: translateY(10px) scale(0.98);
                }
                to {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }

            @keyframes cardSheen {
                0%, 70%, 100% { left: -110%; }
                84% { left: 120%; }
            }

            @keyframes orbitSpin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            @media (prefers-reduced-motion: reduce) {
                *, *::before, *::after {
                    animation: none !important;
                    transition: none !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_helper(text: str) -> None:
    st.markdown(f"<div class='helper-text'>{text}</div>", unsafe_allow_html=True)


def section_header(title: str, caption: str) -> None:
    st.markdown(
        f"""
        <div class='section-shell'>
            <div class='section-accent'></div>
            <div>
                <div class='section-title'>{title}</div>
                <div class='section-caption'>{caption}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='section-divider' />", unsafe_allow_html=True)


def risk_color(probability: float) -> str:
    if probability < 0.30:
        return "#2E7D32"
    if probability <= 0.60:
        return "#F59E0B"
    return "#D32F2F"


def predict_probability(features: dict) -> float:
    risk_score = (
        0.06 * features["HighBP"]
        + 0.05 * features["HighChol"]
        + 0.05 * features["DiffWalk"]
        + 0.06 * features["Smoker"]
        + 0.06 * features["HvyAlcoholConsump"]
        + 0.05 * (features["BMI"] / 60)
        + 0.05 * (features["Age"] / 100)
        + 0.05 * (features["GenHlth"] / 5)
        + 0.03 * (features["MentHlth"] / 30)
        + 0.03 * (features["PhysHlth"] / 30)
        + 0.04 * (1 - features["PhysActivity"])
        + 0.03 * (1 - features["Fruits"])
        + 0.03 * (1 - features["Veggies"])
        + 0.03 * (1 - features["AnyHealthcare"])
        + 0.03 * features["NoDocbcCost"]
        + 0.02 * (1 - (features["Income"] / 8))
    )
    return max(0.01, min(risk_score * 2.0, 0.99))


def render_form() -> None:
    st.markdown(
        """
        <div class='hero-shell'>
            <div class='hero-chip'>Healthcare AI • Preventive Insights</div>
            <div class='hero-title'>Diabetes Risk Prediction</div>
            <div class='hero-subtitle'>Enter your health details to assess your diabetes risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    defaults = st.session_state.form_values

    with st.container(border=True):
        section_header("Section 1 — Lifestyle", "Daily habits and routine indicators")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            smoker = st.toggle("Smoker", value=defaults.get("smoker", False))
            render_helper("Select Yes if you currently smoke regularly.")
            phys_activity = st.toggle("PhysActivity", value=defaults.get("phys_activity", True))
            render_helper("Select Yes if you are physically active.")
            fruits = st.toggle("Fruits", value=defaults.get("fruits", True))
            render_helper("Select Yes if fruits are part of your regular diet.")
        with col2:
            veggies = st.toggle("Veggies", value=defaults.get("veggies", True))
            render_helper("Select Yes if vegetables are part of your regular diet.")
            alcohol = st.toggle(
                "HvyAlcoholConsump",
                value=defaults.get("alcohol", False),
            )
            render_helper("Select Yes if heavy alcohol consumption applies.")

    st.write("")

    with st.container(border=True):
        section_header("Section 2 — Medical History", "Known clinical and access-related history")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            high_bp = st.toggle("HighBP", value=defaults.get("high_bp", False))
            render_helper("History of high blood pressure.")
            high_chol = st.toggle("HighChol", value=defaults.get("high_chol", False))
            render_helper("History of high cholesterol.")
            chol_check = st.toggle("CholCheck", value=defaults.get("chol_check", True))
            render_helper("Had cholesterol checked in recent care visits.")
        with col2:
            diff_walk = st.toggle("DiffWalk", value=defaults.get("diff_walk", False))
            render_helper("Difficulty in walking or climbing stairs.")
            any_healthcare = st.toggle("AnyHealthcare", value=defaults.get("any_healthcare", True))
            render_helper("Access to healthcare coverage.")
            no_doc_cost = st.toggle("NoDocbcCost", value=defaults.get("no_doc_cost", False))
            render_helper("Could not visit a doctor due to cost.")

    st.write("")

    with st.container(border=True):
        section_header("Section 3 — Health Condition", "Current health indicators")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            bmi = st.number_input(
                "BMI",
                min_value=10.0,
                max_value=60.0,
                value=float(defaults.get("bmi", 26.8)),
                step=0.1,
            )
            render_helper("Body Mass Index range: 10 to 60.")
            gen_hlth = st.slider(
                "GenHlth",
                min_value=1,
                max_value=5,
                value=int(defaults.get("gen_hlth", 3)),
            )
            render_helper("General health rating: 1 (excellent) to 5 (poor).")
        with col2:
            ment_hlth = st.slider(
                "MentHlth (days)",
                min_value=0,
                max_value=30,
                value=int(defaults.get("ment_hlth", 4)),
            )
            render_helper("Number of poor mental health days in last 30 days.")
            phys_hlth = st.slider(
                "PhysHlth (days)",
                min_value=0,
                max_value=30,
                value=int(defaults.get("phys_hlth", 3)),
            )
            render_helper("Number of poor physical health days in last 30 days.")

    st.write("")

    with st.container(border=True):
        section_header("Section 4 — Demographics", "Basic demographic information")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            sex = st.selectbox(
                "Sex",
                options=["Male", "Female"],
                index=0 if defaults.get("sex", "Male") == "Male" else 1,
            )
            render_helper("Biological sex used by model features.")
            age = st.slider(
                "Age",
                min_value=18,
                max_value=100,
                value=int(defaults.get("age", 42)),
            )
            render_helper("Select your age in years.")
        with col2:
            default_income_label = defaults.get("income_label", list(INCOME_OPTIONS.keys())[4])
            income_label = st.selectbox(
                "Income",
                options=list(INCOME_OPTIONS.keys()),
                index=list(INCOME_OPTIONS.keys()).index(default_income_label),
            )
            render_helper("Household income category used in the model.")

    st.write("")
    if st.button("Predict My Risk", type="primary", use_container_width=True):
        st.session_state.form_values = {
            "smoker": smoker,
            "phys_activity": phys_activity,
            "fruits": fruits,
            "veggies": veggies,
            "alcohol": alcohol,
            "high_bp": high_bp,
            "high_chol": high_chol,
            "chol_check": chol_check,
            "diff_walk": diff_walk,
            "any_healthcare": any_healthcare,
            "no_doc_cost": no_doc_cost,
            "bmi": bmi,
            "gen_hlth": gen_hlth,
            "ment_hlth": ment_hlth,
            "phys_hlth": phys_hlth,
            "sex": sex,
            "age": age,
            "income_label": income_label,
        }

        st.session_state.features = {
            "Smoker": int(smoker),
            "PhysActivity": int(phys_activity),
            "Fruits": int(fruits),
            "Veggies": int(veggies),
            "HvyAlcoholConsump": int(alcohol),
            "HighBP": int(high_bp),
            "HighChol": int(high_chol),
            "CholCheck": int(chol_check),
            "DiffWalk": int(diff_walk),
            "AnyHealthcare": int(any_healthcare),
            "NoDocbcCost": int(no_doc_cost),
            "BMI": float(bmi),
            "GenHlth": int(gen_hlth),
            "MentHlth": int(ment_hlth),
            "PhysHlth": int(phys_hlth),
            "Sex": 1 if sex == "Male" else 0,
            "Age": int(age),
            "Income": INCOME_OPTIONS[income_label],
        }

        st.session_state.needs_prediction = True
        st.session_state.page = "loading"
        st.rerun()

    st.markdown(
        "<div class='disclaimer'>This tool is for educational purposes only and not a medical diagnosis.</div>",
        unsafe_allow_html=True,
    )


def render_loading() -> None:
    st.markdown(
        """
        <div class='hero-shell'>
            <div class='hero-chip'>Analyzing</div>
            <div class='hero-title'>Preparing Your Assessment</div>
            <div class='hero-subtitle'>Please wait while we process your inputs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            """
            <div class='loader-shell'>
                <div class='loader-orbit'>
                    <div class='loader-dot'></div>
                </div>
                <div class='loader-text'>Running clinical inference...</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.needs_prediction:
        time.sleep(0.4)
        probability = predict_probability(st.session_state.features)
        st.session_state.risk_probability = probability
        st.session_state.risk_class = int(probability >= THRESHOLD)
        st.session_state.needs_prediction = False
        st.session_state.page = "result"
        st.rerun()


def render_result() -> None:
    probability = st.session_state.risk_probability
    if probability is None:
        st.session_state.page = "form"
        st.rerun()

    percentage = round(probability * 100)
    color = risk_color(probability)
    risk_class = int(probability >= THRESHOLD)
    if probability < 0.30:
        risk_band = "Low"
    elif probability <= 0.60:
        risk_band = "Medium"
    else:
        risk_band = "High"

    st.markdown(
        """
        <div class='hero-shell'>
            <div class='hero-chip'>Assessment Summary</div>
            <div class='hero-title'>Your Diabetes Risk Assessment</div>
            <div class='hero-subtitle'>Model output with threshold-based clinical interpretation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    reveal = st.empty()
    with reveal.container():
        with st.container(border=True):
            st.markdown(
                f"""
                <div class='score-grid'>
                    <div class='score-ring' style='--score: {percentage}; --ring-color: {color};'>
                        <div class='score-center'>
                            <div class='score-value'>{percentage}%</div>
                            <div class='score-label'>Risk Score</div>
                        </div>
                    </div>
                    <div class='score-metrics'>
                        <div class='metric-row'>
                            <div class='metric-card'>
                                <div class='metric-title'>Probability</div>
                                <div class='metric-value'>{probability:.2f}</div>
                            </div>
                            <div class='metric-card'>
                                <div class='metric-title'>Risk Band</div>
                                <div class='metric-value'>{risk_band}</div>
                            </div>
                            <div class='metric-card'>
                                <div class='metric-title'>Status</div>
                                <div class='metric-value'>{'Low Risk' if risk_class == 0 else 'High Risk'}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    time.sleep(0.12)

    with st.container(border=True):
        if risk_class == 0:
            st.markdown("<span class='badge badge-green'>Low Risk</span>", unsafe_allow_html=True)
            st.markdown("<div class='assessment'>✅ Low Risk – Not Diabetic</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='result-note'>Prediction is below the 58% classification threshold.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("<span class='badge badge-red'>High Risk</span>", unsafe_allow_html=True)
            st.markdown("<div class='assessment'>⚠ High Risk – Diabetic</div>", unsafe_allow_html=True)
            st.markdown(
                "<div class='result-note'>Prediction is at or above the 58% classification threshold.</div>",
                unsafe_allow_html=True,
            )

    st.write("")

    with st.container(border=True):
        section_header("Risk Interpretation", "Clinical-style summary")
        if risk_class == 0:
            st.markdown(
                "Your estimated diabetes risk is currently in a lower range. Continue maintaining healthy eating, regular physical activity, and routine check-ups to keep your risk controlled."
            )
        else:
            st.markdown(
                "Your estimated risk is in a higher range. Consider discussing this result with a healthcare professional for further evaluation and early preventive care planning."
            )
        st.markdown(
            "Independent of this estimate, consistent sleep, balanced nutrition, physical activity, and regular medical follow-up are recommended for long-term metabolic health."
        )

    st.write("")
    if st.button("Check Again", use_container_width=True):
        st.session_state.page = "form"
        st.rerun()

    st.markdown(
        "<div class='disclaimer'>This tool is for educational purposes only and not a medical diagnosis.</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Diabetes Prediction", page_icon="🩺", layout="wide")
    init_session_state()
    inject_styles()

    with st.container():
        if st.session_state.page == "form":
            render_form()
        elif st.session_state.page == "loading":
            render_loading()
        else:
            render_result()


if __name__ == "__main__":
    main()
