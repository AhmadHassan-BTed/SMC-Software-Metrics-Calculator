import streamlit as st
import pandas as pd
import plotly.express as px
import json
import sys
from pathlib import Path

# Add src to path for robust imports
sys.path.append(str(Path(__file__).parent / "src"))

from metrics_calculator import analyze_python_file, calculate_cocomo, analyze_agile_metrics

def main():
    st.set_page_config(
        page_title="Software Metrics Calculator",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("🚀 Advanced Software Metrics Analysis Dashboard")
    st.markdown("---")

    with st.sidebar:
        st.header("📥 Project Data Input")
        python_files = st.file_uploader("Upload Python Files", type=['py'], accept_multiple_files=True)
        sprint_data = st.file_uploader("Upload Sprint Data (JSON)", type=['json'])
        defect_data = st.file_uploader("Upload Defect Data (JSON)", type=['json'])

        st.header("⚙️ Analysis Settings")
        show_recommendations = st.checkbox("Show Refactoring Recommendations", value=True)
        complexity_threshold = st.slider("Complexity Warning Threshold", 5, 20, 10)
        
        st.info("Upload your Python source files to see the analysis.")

    if python_files:
        st.header("📊 Code Analysis Results")

        col1, col2, col3, col4 = st.columns(4)
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

            with col1:
                st.metric("Total Files", len(metrics_data))
                st.metric("Total kLOC", round(total_kloc, 2))

            with col2:
                st.metric("Avg Cyclomatic Complexity", round(df['cyclomatic_complexity'].mean(), 2))
                st.metric("Avg Cognitive Complexity", round(df['cognitive_complexity'].mean(), 2))

            with col3:
                st.metric("Total Function Points", round(df['function_points'].sum(), 2))
                st.metric("Avg Defect Density", round(df['defect_density'].mean(), 4))

            with col4:
                cocomo = calculate_cocomo(total_kloc)
                st.metric("Estimated Effort (person-months)", cocomo['effort'])
                st.metric("Estimated Duration (months)", cocomo['time'])
                st.metric("Estimated Team Size (persons)", cocomo['staff'])

            st.markdown("---")
            st.subheader("🔍 Detailed Metrics Analysis")
            tabs = st.tabs(["📝 Code Metrics", "🧠 Complexity Analysis", "📉 Quality Indicators"])

            with tabs[0]:
                st.dataframe(df, use_container_width=True)
                fig_loc = px.histogram(df, x='lines_of_code',
                                       title='Lines of Code Distribution',
                                       labels={'lines_of_code': 'Lines of Code'},
                                       color_discrete_sequence=['#636EFA'])
                st.plotly_chart(fig_loc, use_container_width=True)

            with tabs[1]:
                fig_complexity = px.scatter(df,
                                          x='cyclomatic_complexity',
                                          y='cognitive_complexity',
                                          size='lines_of_code',
                                          hover_data=['filename'],
                                          title='Cyclomatic vs Cognitive Complexity',
                                          color='cyclomatic_complexity',
                                          color_continuous_scale='Viridis')
                st.plotly_chart(fig_complexity, use_container_width=True)

                if show_recommendations:
                    st.subheader("💡 Refactoring Recommendations")
                    complex_files = df[df['cyclomatic_complexity'] > complexity_threshold]
                    if not complex_files.empty:
                        for _, row in complex_files.iterrows():
                            st.warning(
                                f"**File '{row['filename']}'** has high complexity "
                                f"(Cyclomatic: {row['cyclomatic_complexity']}, "
                                f"Cognitive: {row['cognitive_complexity']}). "
                                "Consider breaking down into smaller, more modular functions."
                            )
                    else:
                        st.success("All files are within the complexity threshold!")

            with tabs[2]:
                quality_metrics = pd.DataFrame({
                    'Metric': ['Defect Density', 'Function Points per kLOC'],
                    'Value': [
                        df['defect_density'].mean(),
                        df['function_points'].sum() / total_kloc if total_kloc > 0 else 0
                    ]
                })
                fig_quality = px.bar(quality_metrics, x='Metric', y='Value',
                                   title='Quality Indicators',
                                   color='Metric',
                                   color_discrete_sequence=['#EF553B', '#00CC96'])
                st.plotly_chart(fig_quality, use_container_width=True)

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

                if 'completed_points' in sprint_df.columns:
                    fig_velocity = px.line(sprint_df, x=sprint_df.index, y='completed_points',
                                         title='Sprint Velocity Trend',
                                         markers=True)
                    st.plotly_chart(fig_velocity, use_container_width=True)

                if all(col in sprint_df.columns for col in ['remaining_points', 'sprint_day']):
                    fig_burndown = px.line(sprint_df, x='sprint_day', y='remaining_points',
                                         title='Sprint Burndown Chart',
                                         markers=True)
                    st.plotly_chart(fig_burndown, use_container_width=True)
        except Exception as e:
            st.error(f"Error analyzing agile data: {str(e)}")

if __name__ == "__main__":
    main()
