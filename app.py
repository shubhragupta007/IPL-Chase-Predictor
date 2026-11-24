# Serves the IPL Chase Win Predictor website (index.html) through Streamlit.
# The model runs inside index.html, so model.pkl is not needed here.
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="IPL Chase Win Predictor", page_icon="🏏",
                   layout="wide", initial_sidebar_state="collapsed")

# hide Streamlit's own header, menu, footer and padding so only the website shows
st.markdown(
    """
    <style>
      #MainMenu, header, footer {visibility: hidden;}
      [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stHeader"] {display: none;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      [data-testid="stAppViewContainer"], .stApp {background: #090D28;}
      iframe {display: block; width: 100% !important; height: 100vh !important; border: 0;}
    </style>
    """,
    unsafe_allow_html=True,
)

html = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
components.html(html, height=1000, scrolling=True)
