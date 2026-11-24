import math

import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="IPL Chase Win Predictor", page_icon="🏏", layout="wide")


@st.cache_resource
def load_model():
    try:
        return joblib.load("model.pkl")
    except FileNotFoundError:
        return None


model = load_model()
data = pd.read_csv("chase_table_final.csv")
venues = sorted(data["venue"].unique())
teams = sorted(data["chasing_team"].unique())


def win_probability(target, score, wickets_lost, balls_bowled, venue, chasing_team, bowling_team):
    """Chance (0 to 1) that the chasing team wins from this situation."""
    runs_left = target - score
    balls_left = 120 - balls_bowled
    wickets_left = 10 - wickets_lost
    if runs_left <= 0:
        return 1.0
    if wickets_left <= 0 or balls_left <= 0:
        return 0.0
    current_rr = score * 6 / balls_bowled if balls_bowled > 0 else 0.0
    required_rr = runs_left * 6 / balls_left
    if model is None:  # demo formula, used only when model.pkl is missing
        z = 0.2 * (wickets_left - 5) + 0.5 * (7.5 - required_rr)
        return 1 / (1 + math.exp(-z))
    row = pd.DataFrame([{
        "target": target,
        "current_score": score,
        "runs_left": runs_left,
        "balls_left": balls_left,
        "wickets_left": wickets_left,
        "current_run_rate": current_rr,
        "required_run_rate": required_rr,
        "venue": venue,
        "chasing_team": chasing_team,
        "bowling_team": bowling_team,
    }])
    return float(model.predict_proba(row)[0][1])


def overs_text(balls):
    return f"{balls // 6}.{balls % 6}"


# ---------- starting values and example buttons ----------
defaults = {"target": 170, "overs": 10, "balls": 0, "score": 80, "wickets": 3}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

presets = {
    "😎 Easy chase": (150, 10, 0, 100, 1),
    "🔥 Powerplay blast": (200, 6, 0, 80, 0),
    "😬 Last-over thriller": (160, 19, 0, 150, 6),
    "🚨 Batting collapse": (170, 12, 0, 70, 7),
}


def load_preset(target, overs, balls, score, wickets):
    st.session_state["target"] = target
    st.session_state["overs"] = overs
    st.session_state["balls"] = balls
    st.session_state["score"] = score
    st.session_state["wickets"] = wickets


# ---------- page ----------
st.title("🏏 IPL Chase Win Predictor")
st.caption("Type in the match situation. Everything below updates as you type.")

if model is None:
    st.warning("model.pkl was not found, so the numbers come from a simple DEMO formula, "
               "not from the trained model. Put model.pkl in this folder and restart the app.")

st.write("Try an example:")
example_cols = st.columns(len(presets))
for col, (label, values) in zip(example_cols, presets.items()):
    col.button(label, on_click=load_preset, args=values)

st.subheader("1. The match situation")
c1, c2, c3, c4, c5 = st.columns(5)
target = c1.number_input("Target to chase", min_value=1, max_value=400, step=1, key="target")
overs = c2.number_input("Overs completed", min_value=0, max_value=19, step=1, key="overs")
balls = c3.number_input("Balls in this over (0-5)", min_value=0, max_value=5, step=1, key="balls")
score = c4.number_input("Runs scored so far", min_value=0, max_value=400, step=1, key="score")
wickets_lost = c5.number_input("Wickets lost", min_value=0, max_value=10, step=1, key="wickets")

v1, v2, v3 = st.columns(3)
venue = v1.selectbox("Venue (type to search)", venues)
chasing_team = v2.selectbox("Chasing team", teams)
bowling_team = v3.selectbox("Bowling team", [t for t in teams if t != chasing_team])

balls_bowled = overs * 6 + balls
runs_left = target - score
balls_left = 120 - balls_bowled
wickets_left = 10 - wickets_lost

if score >= target:
    st.success(f"🎉 {chasing_team} have reached the target of {target}. The chase is won!")
    st.stop()
if wickets_lost >= 10:
    st.error(f"💀 {chasing_team} are all out. The chase is lost.")
    st.stop()

current_rr = score * 6 / balls_bowled if balls_bowled > 0 else 0.0
required_rr = runs_left * 6 / balls_left

# ---------- the automatic boxes ----------
st.subheader("2. Worked out for you")
b1, b2, b3, b4, b5 = st.columns(5)
with b1:
    with st.container(border=True):
        st.metric("Runs needed", f"{runs_left}")
with b2:
    with st.container(border=True):
        st.metric("Balls left", f"{balls_left} ({overs_text(balls_left)} ov)")
with b3:
    with st.container(border=True):
        st.metric("Wickets in hand", f"{wickets_left}")
with b4:
    with st.container(border=True):
        st.metric("Current run rate (CRR)", f"{current_rr:.2f}")
with b5:
    with st.container(border=True):
        st.metric("Required run rate (RRR)", f"{required_rr:.2f}",
                  delta=f"{required_rr - current_rr:+.2f} vs CRR", delta_color="inverse")

# ---------- the prediction ----------
p = win_probability(target, score, wickets_lost, balls_bowled, venue, chasing_team, bowling_team)

st.subheader("3. Who wins?")
if p >= 0.90:
    mood = "🔥 The chasing side is cruising."
elif p >= 0.70:
    mood = "😎 The chasing team has the edge."
elif p >= 0.55:
    mood = "🙂 A slight lean to the chasing team."
elif p > 0.45:
    mood = "😬 Too close to call!"
elif p > 0.30:
    mood = "😅 The bowling side has a slight edge."
elif p > 0.10:
    mood = "🎯 The bowling side is in control."
else:
    mood = "🚨 The chase is nearly gone."

st.markdown(f"**{chasing_team}** (chasing) vs **{bowling_team}** (defending)")
st.markdown(
    f"""
<div style="display:flex;height:40px;border-radius:20px;overflow:hidden;font-weight:600;color:white;">
  <div style="width:{p * 100:.1f}%;background:#1f9d55;display:flex;align-items:center;justify-content:center;">{p:.0%}</div>
  <div style="width:{(1 - p) * 100:.1f}%;background:#d64545;display:flex;align-items:center;justify-content:center;">{1 - p:.0%}</div>
</div>
""",
    unsafe_allow_html=True,
)
st.subheader(mood)

# ---------- what-if ----------
if balls_left > 6:
    st.subheader("4. 🔮 What if the next 6 balls go like this?")
    run_options = list(range(0, 22, 2))
    no_wicket = [
        win_probability(target, score + r, wickets_lost, balls_bowled + 6, venue, chasing_team, bowling_team) * 100
        for r in run_options
    ]
    one_wicket = [
        win_probability(target, score + r, wickets_lost + 1, balls_bowled + 6, venue, chasing_team, bowling_team) * 100
        for r in run_options
    ]
    chart = pd.DataFrame(
        {"No wicket": no_wicket, "One wicket": one_wicket},
        index=pd.Index(run_options, name="Runs scored in the next 6 balls"),
    )
    st.line_chart(chart)
    st.caption("Chasing team's win chance (%) after the next 6 balls.")

st.caption(f"Built from {data['match_id'].nunique()} past IPL matches. "
           "These are estimates from a simulation, not a live feed.")
