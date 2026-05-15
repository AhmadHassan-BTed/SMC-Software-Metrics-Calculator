import streamlit as st
import sys
from pathlib import Path

# Add paths to sys.path to resolve internal modules
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR / "src"))
sys.path.append(str(ROOT_DIR / "java_analyzer"))

# Global Page Configuration
st.set_page_config(
    page_title="Unified Software Quality Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Render main navigation in sidebar
with st.sidebar:
    st.markdown("## 🛠️ Quality Suite Hub")
    app_mode = st.radio(
        "Select Analysis Tool:",
        ["Python & Agile Metrics", "Java Static Analyzer"],
        help="Choose between Python Code/Agile metrics and Java Static Analysis."
    )
    st.markdown("---")

# Import the main functions here to avoid executing module-level code before page config
from software_metrics.ui.dashboard import run_app as run_python_dashboard
from dashboard import main as run_java_dashboard

if __name__ == "__main__":
    if app_mode == "Python & Agile Metrics":
        run_python_dashboard()
    elif app_mode == "Java Static Analyzer":
        run_java_dashboard()
