import sys
from pathlib import Path

# Project root add to PYTHONPATH
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from backend.app.main import app

import streamlit as st
st.write("Backend loaded successfully")
