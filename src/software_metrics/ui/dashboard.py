import streamlit as st
import pandas as pd
import json
from software_metrics.ui.components.sidebar import render_sidebar
from software_metrics.ui.components.charts import (
    render_loc_distribution, 
    render_complexity_scatter, 
    render_quality_bar,
    render_agile_charts
)
from software_metrics.ui.components.metrics_cards import render_summary_metrics, render_recommendations
from software_metrics.calculators.code_analyzer import analyze_python_file
from software_metrics.calculators.estimation import calculate_cocomo
from software_metrics.calculators.agile import analyze_agile_metrics

def run_app():
    

    st.title("🚀 Advanced Software Metrics Analysis Dashboard")
    st.markdown("---")

    python_files, sprint_data, defect_data, show_recommendations, complexity_threshold = render_sidebar()

    if python_files:
        st.header("📊 Code Analysis Results")
        metrics_data = []
        total_kloc = 0

        for uploaded_file in python_files:
            try:
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
            st.subheader("🔍 Detailed Metrics Analysis")
            tabs = st.tabs(["📝 Code Metrics", "🧠 Complexity Analysis", "📉 Quality Indicators"])

            with tabs[0]:
                st.dataframe(df, use_container_width=True)
                render_loc_distribution(df)

            with tabs[1]:
                render_complexity_scatter(df)
                if show_recommendations:
                    render_recommendations(df, complexity_threshold)

            with tabs[2]:
                render_quality_bar(df, total_kloc)

            st.download_button(
                label="📥 Download Full Metrics Report (CSV)",
                data=df.to_csv(index=False),
                file_name="metrics_report.csv",
                mime="text/csv"
            )

    if sprint_data:
        st.markdown("---")
        st.header("🏃 Agile Metrics Analysis")
        try:
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
