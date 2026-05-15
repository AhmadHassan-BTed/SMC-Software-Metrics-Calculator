import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add paths to sys.path to resolve internal modules
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR / "src"))
sys.path.append(str(ROOT_DIR / "src" / "java_analyzer"))

# Global Page Configuration
st.set_page_config(
    page_title="Omniscient Quality Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for unified dashboard
st.markdown("""
    <style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(120deg, #1e3a8a 0%, #3b82f6 100%, #10b981 200%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Import Java dependencies
from java_analyzer.dashboard import (
    initialize_session_state,
    handle_analysis as handle_java_analysis,
    display_analysis_results as display_java_results,
    render_file_info as render_java_file_info
)

# Import Python/Agile dependencies
from software_metrics.calculators.code_analyzer import analyze_python_file
from software_metrics.calculators.estimation import calculate_cocomo
from software_metrics.calculators.agile import analyze_agile_metrics
from software_metrics.ui.components.metrics_cards import render_summary_metrics, render_recommendations
from software_metrics.ui.components.charts import (
    render_loc_distribution, 
    render_complexity_scatter, 
    render_quality_bar,
    render_agile_charts
)

# Initialize Java session state
initialize_session_state()

def render_unified_landing():
    st.markdown('<h1 class="main-header">🛡️ Omniscient Software Intelligence Suite</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Unified Code Quality, Architecture Metrics & Agile Process Analytics</p>', unsafe_allow_html=True)
    
    st.markdown("### 🎯 Unified Capabilities")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### ☕ Architecture & Static Analysis")
        st.markdown("- Deep AST Code Smell Detection\n- Design & Implementation Flaws\n- Maintainability Index")
    with col2:
        st.markdown("#### 📊 Code Metrics")
        st.markdown("- Cyclomatic & Cognitive Complexity\n- Defect Density Prediction\n- COCOMO Estimation")
    with col3:
        st.markdown("#### 🏃 Agile Process")
        st.markdown("- Velocity Tracking\n- Scope Creep Analysis\n- Sprint Burndown")
    
    st.markdown("---")
    st.markdown("### 🔍 How to Use")
    st.markdown("""
    1. **Upload Files:** Use the Control Center sidebar to upload any combination of source code files or Agile JSON data into the single Source Code uploader.
    2. **Configure Engines:** Adjust thresholds and toggle specific analyzers (like Design Smells) to tailor the strictness.
    3. **Execute:** Click the "Execute Omniscient Analysis" button to process all uploaded artifacts simultaneously.
    4. **Review Results:** Navigate through the dynamically generated tabs to explore unified insights seamlessly.
    """)
    st.info("👆 Awaiting data... Upload files from the Control Center to begin.")

def render_python_results(python_files, show_recommendations, complexity_threshold):
    metrics_data = []
    total_kloc = 0

    for uploaded_file in python_files:
        try:
            uploaded_file.seek(0)
            content = uploaded_file.read().decode('utf-8')
            metrics = analyze_python_file(content)
            if metrics:
                metrics_dict = {
                    'filename': uploaded_file.name,
                    'lines_of_code': metrics.lines_of_code,
                    'functions': metrics.functions,
                    'classes': metrics.classes,
                    'cyclomatic_complexity': metrics.cyclomatic_complexity,
                    'cognitive_complexity': metrics.cognitive_complexity,
                    'function_points': metrics.function_points,
                    'defect_density': metrics.defect_density
                }
                metrics_data.append(metrics_dict)
                total_kloc += metrics.lines_of_code / 1000
        except Exception as e:
            st.error(f"Error reading {uploaded_file.name}: {str(e)}")

    if metrics_data:
        df = pd.DataFrame(metrics_data)
        cocomo = calculate_cocomo(total_kloc)

        render_summary_metrics(df, total_kloc, cocomo)

        st.markdown("---")
        st.subheader("🔍 Detailed Code Metrics")
        ptabs = st.tabs(["📝 Code Metrics", "🧠 Complexity Analysis", "📉 Quality Indicators"])

        with ptabs[0]:
            st.dataframe(df, use_container_width=True)
            render_loc_distribution(df)

        with ptabs[1]:
            render_complexity_scatter(df)
            if show_recommendations:
                render_recommendations(df, complexity_threshold)

        with ptabs[2]:
            render_quality_bar(df, total_kloc)

def render_agile_results(sprint_data):
    try:
        sprint_data.seek(0)
        sprint_json = json.load(sprint_data)
        sprint_df = pd.DataFrame(sprint_json)

        if not sprint_df.empty:
            agile_metrics = analyze_agile_metrics(sprint_df)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Velocity", agile_metrics.get('average_velocity', 0))
            with col2:
                st.metric("Scope Creep", f"{agile_metrics.get('scope_creep_percentage', 0)}%")

            render_agile_charts(sprint_df)
    except Exception as e:
        st.error(f"Error analyzing agile data: {str(e)}")

def main():
    with st.sidebar:
        st.markdown("## 📂 Universal Control Center")
        
        st.markdown("### Source Code (Auto-Detect)")
        # UNIFIED SINGLE UPLOADER FOR BOTH PYTHON AND JAVA
        source_files = st.file_uploader("Upload Source Code", type=['py', 'java'], accept_multiple_files=True)
        
        st.markdown("### Process Data")
        sprint_data = st.file_uploader("Upload Sprint Data (JSON)", type=['json'])
        defect_data = st.file_uploader("Upload Defect Data (JSON)", type=['json'])
        
        st.markdown("---")
        st.markdown("### ⚙️ Engine Configuration")
        
        with st.expander("Global Analysis Parameters", expanded=True):
            show_recommendations = st.checkbox("Enable Refactoring Recommendations", value=True)
            complexity_threshold = st.slider("Complexity Warning Threshold", 5, 20, 10)
            enable_design = st.checkbox("Detect Design Smells", value=True)
            enable_implementation = st.checkbox("Detect Implementation Smells", value=True)
            enable_naming = st.checkbox("Check Naming Conventions", value=True)
            enable_documentation = st.checkbox("Verify Documentation Coverage", value=True)
            
            java_config = {
                'design': enable_design,
                'implementation': enable_implementation,
                'naming': enable_naming,
                'documentation': enable_documentation
            }
            
        st.markdown("---")
        analyze_btn = st.button("🚀 Execute Omniscient Analysis", type="primary", use_container_width=True)
        
        st.caption("🔧 Unified Platform v4.1")
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Separate files by extension
    python_files = [f for f in source_files if f.name.endswith('.py')] if source_files else []
    java_files = [f for f in source_files if f.name.endswith('.java')] if source_files else []

    # Handle execute state
    if analyze_btn:
        st.session_state.omni_analyzed = True

    has_content = bool(python_files or java_files or sprint_data)

    if not has_content:
        render_unified_landing()
    else:
        st.markdown('<h1 class="main-header">📊 Unified Analysis Results</h1>', unsafe_allow_html=True)
        
        tab_names = []
        if python_files: tab_names.append("📊 Code Metrics")
        if java_files: tab_names.append("☕ Architecture & Smells")
        if sprint_data: tab_names.append("🏃 Agile Analytics")
        
        if not tab_names:
            return
            
        tabs = st.tabs(tab_names)
        tab_idx = 0
        
        if python_files:
            with tabs[tab_idx]:
                if st.session_state.get('omni_analyzed', False):
                    render_python_results(python_files, show_recommendations, complexity_threshold)
                else:
                    st.info("Click 'Execute Omniscient Analysis' in the sidebar to process code metrics.")
            tab_idx += 1
            
        if java_files:
            with tabs[tab_idx]:
                if st.session_state.get('omni_analyzed', False):
                    # Process each Java file. If multiple, we show a selectbox to pick which one to view.
                    if len(java_files) > 1:
                        java_file_names = [f.name for f in java_files]
                        selected_java = st.selectbox("Select Source File to view static analysis:", java_file_names)
                        active_java_file = next(f for f in java_files if f.name == selected_java)
                    else:
                        active_java_file = java_files[0]

                    active_java_file.seek(0)
                    source_code = active_java_file.getvalue().decode("utf-8")
                    
                    # Update session state for the Java Dashboard components
                    st.session_state.file_name = active_java_file.name
                    st.session_state.source_code = source_code
                    
                    # Render basic file info
                    render_java_file_info(active_java_file.name, len(source_code), len(source_code.split('\n')))
                    
                    # Run analysis with the selected CONFIGURATIONS (passing java_config to respect user choices)
                    handle_java_analysis(source_code, java_config)
                    
                    if st.session_state.analysis_results is not None:
                        display_java_results()
                else:
                    st.info("Click 'Execute Omniscient Analysis' in the sidebar to run the AST Engine.")
            tab_idx += 1
            
        if sprint_data:
            with tabs[tab_idx]:
                if st.session_state.get('omni_analyzed', False):
                    render_agile_results(sprint_data)
                else:
                    st.info("Click 'Execute Omniscient Analysis' in the sidebar to process Agile Data.")
            tab_idx += 1

if __name__ == "__main__":
    main()
