from pathlib import Path
import sys
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env.aws.generated", override=True)
load_dotenv(ROOT / ".env", override=False)
from lbml.cloud import cloud_status, publish_run
from lbml.simulator import run_comparison

st.set_page_config(page_title="LBML Control Plane", page_icon="◈", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--ink:#f4f0e8;--muted:#a9aaa5;--orange:#ff8a3d;--lime:#b6f36b;--panel:#171a1d;--line:#34393d}
.stApp{background:linear-gradient(135deg,#0b0d0e 0%,#15181a 55%,#101b16 100%);color:var(--ink);font-family:'IBM Plex Mono',monospace}.stApp:before{content:'';position:fixed;inset:0;pointer-events:none;opacity:.16;background-image:linear-gradient(#ffffff10 1px,transparent 1px),linear-gradient(90deg,#ffffff10 1px,transparent 1px);background-size:32px 32px}.block-container{max-width:1280px;padding:1.7rem 2.6rem}.hero,.card{background:var(--panel);border:1px solid var(--line);box-shadow:8px 8px 0 #080909;border-radius:5px}.hero{padding:1.7rem 2rem;margin-bottom:1.1rem;border-left:5px solid var(--orange);background:linear-gradient(90deg,#1d2022,#151819)}.hero h1{font:700 2.4rem 'Space Grotesk';letter-spacing:-.04em;margin:.15rem 0}.hero p{color:#bfc0ba;font-size:.92rem}.card{padding:1.1rem;margin-bottom:.8rem}.metric{font:700 1.55rem 'Space Grotesk';color:var(--lime)}.stButton>button{border-radius:3px;background:var(--orange);border:1px solid #ffb178;color:#101112;font-family:'IBM Plex Mono';font-weight:600;box-shadow:3px 3px 0 #080909}.stButton>button:hover{background:var(--lime);color:#101112;transform:translate(-1px,-1px)}[data-testid="stSidebar"]{background:#0d0f10;border-right:1px solid #3d4244}[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{font-family:'Space Grotesk';color:var(--orange)}.stSelectbox>div>div,.stNumberInput>div>div{background:#202427;border-radius:3px;border:1px solid #4b5052}.stDataFrame{border:1px solid var(--line)}
</style>""", unsafe_allow_html=True)
st.markdown('<div class="hero"><div style="letter-spacing:.18em;color:#ff8a3d;font-size:.7rem">LBML // EXPERIMENT CONTROL PLANE // ONLINE</div><h1>◈ CloudBalancer</h1><p>Predictive routing laboratory for workload pressure, capacity headroom, and server imbalance.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## CONTROL PLANE")
    scenario = st.selectbox("Scenario", ["E1", "E2", "E3", "E4"], index=2)
    duration = st.slider("Simulation duration (seconds)", 60, 300, 180, 30)
    seed = st.number_input("Workload seed", min_value=1, value=101, step=1)
    st.divider()
    st.markdown("### AWS TELEMETRY")
    for name, enabled, detail in cloud_status():
        st.markdown(f"{'🟢' if enabled else '⚪'} **{name}**  \n<small>{detail}</small>", unsafe_allow_html=True)
    run_clicked = st.button("▶ RUN EXPERIMENT", use_container_width=True)

if run_clicked or "results" not in st.session_state:
    with st.spinner("Generating identical workload and evaluating all three policies..."):
        results, details = run_comparison(scenario, duration, int(seed))
    st.session_state.results, st.session_state.details = results, details
    st.session_state.scenario = scenario

results, details = st.session_state.results, st.session_state.details
st.markdown(f'<div class="card"><b>RUN {st.session_state.scenario} / SEED {seed}</b> &nbsp; | &nbsp; TRACE LOCKED &nbsp; | &nbsp; WINDOW {duration}s<br><span style="color:#a9aaa5">Simulation metrics are synthetic cluster measurements. Routing and model overhead are measured locally.</span></div>', unsafe_allow_html=True)
cols = st.columns(4)
for col, label, value in zip(cols, ["Best p95 latency", "Lowest overload events", "ML route overhead", "Policies compared"], [f"{results.p95_latency_s.min():.3f}s", str(int(results.overload_events.min())), f"{results.loc[results.policy=='ml_predictive','route_time_us'].iloc[0]:.1f} µs", "3"]):
    with col:
        st.markdown(f'<div class="card"><small>{label}</small><div class="metric">{value}</div></div>', unsafe_allow_html=True)
st.subheader("POLICY BENCHMARK MATRIX")
st.dataframe(results[["policy", "requests", "avg_latency_s", "p95_latency_s", "throughput_rps", "overload_events", "imbalance_cv", "route_time_us"]].style.format({"avg_latency_s":"{:.3f}", "p95_latency_s":"{:.3f}", "throughput_rps":"{:.2f}", "imbalance_cv":"{:.3f}", "route_time_us":"{:.2f}"}), use_container_width=True, hide_index=True)
left, right = st.columns(2)
with left:
    st.subheader("PRESSURE PROFILE")
    st.bar_chart(results.set_index("policy")[["avg_latency_s", "p95_latency_s", "overload_events"]])
with right:
    st.subheader("REQUEST ALLOCATION")
    shares = pd.DataFrame({p: details[p]["server"].value_counts(normalize=True) for p in details}).fillna(0)
    st.bar_chart(shares)
st.subheader("SERVER TELEMETRY / PREDICTIVE TRACE")
policy = st.selectbox("Trace policy", list(details), index=2)
trace = details[policy].copy()
observed = trace.pivot_table(index="time", columns="server", values="cpu_before", aggfunc="mean").fillna(0)
st.line_chart(observed, height=320)
if policy == "ml_predictive":
    st.caption("The dashed conceptual prediction series is available per request in the exported CSV; the chart above shows observed server utilization.")
if st.button("⇧ PUBLISH ML RUN TO AWS"):
    ml = results[results.policy == "ml_predictive"].iloc[0].to_dict()
    try:
        messages = publish_run(ml)
        st.success(" · ".join(messages) if messages else "AWS is not configured. Run deploy_aws.ps1 first.")
    except Exception as exc:
        st.error(f"AWS publish failed: {exc}")
