import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import ast
import json
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class CodeMetrics:
    lines_of_code: int
    functions: int
    classes: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    function_points: float
    defect_density: float

def calculate_cognitive_complexity(node, complexity=0, nesting=0):
    """Calculate cognitive complexity for an AST node"""
    if isinstance(node, (ast.If, ast.While, ast.For)):
        complexity += (1 + nesting)
        nesting += 1
    elif isinstance(node, ast.Try):
        complexity += (1 + nesting)
    
    for child in ast.iter_child_nodes(node):
        complexity = calculate_cognitive_complexity(child, complexity, nesting)
    
    return complexity

def calculate_function_points(metrics: CodeMetrics) -> float:
    """Simplified function point calculation"""
    # This is a basic estimation - in real-world scenarios, you'd need more detailed analysis
    return (metrics.functions * 3 + metrics.classes * 5) * 0.7

def analyze_python_file(file_content: str) -> Optional[CodeMetrics]:
    """Analyze a single Python file and return comprehensive metrics"""
    try:
        tree = ast.parse(file_content)
        
        # Basic metrics
        loc = len(file_content.splitlines())
        functions = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        classes = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
        
        # Cyclomatic complexity
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        # Cognitive complexity
        cognitive = calculate_cognitive_complexity(tree)
        
        # Calculate function points and defect density
        metrics = CodeMetrics(
            lines_of_code=loc,
            functions=functions,
            classes=classes,
            cyclomatic_complexity=complexity,
            cognitive_complexity=cognitive,
            function_points=0,  # Placeholder
            defect_density=0    # Placeholder
        )
        
        metrics.function_points = calculate_function_points(metrics)
        # Assume defect density based on complexity metrics (simplified)
        metrics.defect_density = (complexity * cognitive) / (loc if loc > 0 else 1)
        
        return metrics
    except Exception as e:
        st.error(f"Error analyzing file: {str(e)}")
        return None

def calculate_cocomo(kloc: float) -> Dict[str, float]:
    """Calculate COCOMO metrics for organic projects"""
    effort = 2.4 * (kloc ** 1.05)  # person-months
    time = 2.5 * (effort ** 0.38)  # months
    staff = effort / time
    return {
        'effort': round(effort, 2),
        'time': round(time, 2),
        'staff': round(staff, 2)
    }

def analyze_agile_metrics(sprint_data: pd.DataFrame) -> Dict[str, float]:
    """Analyze Agile metrics from sprint data"""
    if sprint_data.empty:
        return {}
    
    velocity = sprint_data['completed_points'].mean() if 'completed_points' in sprint_data.columns else 0
    scope_creep = ((sprint_data['added_points'].sum() / sprint_data['planned_points'].sum()) * 100
                   if 'added_points' in sprint_data.columns and 'planned_points' in sprint_data.columns else 0)
    
    return {
        'average_velocity': round(velocity, 2),
        'scope_creep_percentage': round(scope_creep, 2)
    }

def main():
    st.set_page_config(layout="wide")
    st.title("Advanced Software Metrics Analysis Dashboard")
    
    # Sidebar for file uploads and settings
    with st.sidebar:
        st.header("Project Data Input")
        python_files = st.file_uploader("Upload Python Files", type=['py'], accept_multiple_files=True)
        sprint_data = st.file_uploader("Upload Sprint Data (JSON)", type=['json'])
        defect_data = st.file_uploader("Upload Defect Data (JSON)", type=['json'])
        
        st.header("Analysis Settings")
        show_recommendations = st.checkbox("Show Refactoring Recommendations", value=True)
        complexity_threshold = st.slider("Complexity Warning Threshold", 5, 20, 10)

    if python_files:
        st.header("Code Analysis Results")
        
        # Create columns for key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Analyze all Python files
        metrics_data = []
        total_kloc = 0
        
        for uploaded_file in python_files:
            content = uploaded_file.read().decode('utf-8')
            metrics = analyze_python_file(content)
            if metrics:
                metrics_dict = {
                    'filename': uploaded_file.name,
                    **metrics.__dict__
                }
                metrics_data.append(metrics_dict)
                total_kloc += metrics.lines_of_code / 1000

        if metrics_data:
            df = pd.DataFrame(metrics_data)
            
            # Display summary metrics
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
            
            # Detailed metrics and visualizations
            st.subheader("Detailed Metrics Analysis")
            tabs = st.tabs(["Code Metrics", "Complexity Analysis", "Quality Indicators"])
            
            with tabs[0]:
                st.dataframe(df)
                
                # LOC Distribution
                fig_loc = px.histogram(df, x='lines_of_code', 
                                     title='Lines of Code Distribution',
                                     labels={'lines_of_code': 'Lines of Code'})
                st.plotly_chart(fig_loc)
            
            with tabs[1]:
                # Complexity scatter plot
                fig_complexity = px.scatter(df, 
                                          x='cyclomatic_complexity',
                                          y='cognitive_complexity',
                                          size='lines_of_code',
                                          hover_data=['filename'],
                                          title='Complexity Analysis')
                st.plotly_chart(fig_complexity)
                
                # Refactoring recommendations
                if show_recommendations:
                    st.subheader("Refactoring Recommendations")
                    complex_files = df[df['cyclomatic_complexity'] > complexity_threshold]
                    if not complex_files.empty:
                        for _, row in complex_files.iterrows():
                            st.warning(
                                f"File '{row['filename']}' has high complexity "
                                f"(Cyclomatic: {row['cyclomatic_complexity']}, "
                                f"Cognitive: {row['cognitive_complexity']}). "
                                "Consider breaking down into smaller functions."
                            )
            
            with tabs[2]:
                # Quality metrics visualization
                quality_metrics = pd.DataFrame({
                    'Metric': ['Defect Density', 'Function Points per kLOC'],
                    'Value': [
                        df['defect_density'].mean(),
                        df['function_points'].sum() / total_kloc
                    ]
                })
                fig_quality = px.bar(quality_metrics, x='Metric', y='Value',
                                   title='Quality Indicators')
                st.plotly_chart(fig_quality)

    # Sprint data analysis
    if sprint_data:
        st.header("Agile Metrics Analysis")
        sprint_json = json.load(sprint_data)
        sprint_df = pd.DataFrame(sprint_json)
        
        if not sprint_df.empty:
            agile_metrics = analyze_agile_metrics(sprint_df)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Velocity", agile_metrics.get('average_velocity', 0))
            with col2:
                st.metric("Scope Creep", f"{agile_metrics.get('scope_creep_percentage', 0)}%")
            
            # Velocity trend
            if 'completed_points' in sprint_df.columns:
                fig_velocity = px.line(sprint_df, x=sprint_df.index, y='completed_points',
                                     title='Sprint Velocity Trend')
                st.plotly_chart(fig_velocity)
                
                # Burndown chart if we have the required data
                if all(col in sprint_df.columns for col in ['remaining_points', 'sprint_day']):
                    fig_burndown = px.line(sprint_df, x='sprint_day', y='remaining_points',
                                         title='Sprint Burndown Chart')
                    st.plotly_chart(fig_burndown)

    # Download reports
    if 'df' in locals():
        st.download_button(
            label="Download Full Metrics Report (CSV)",
            data=df.to_csv(index=False),
            file_name="metrics_report.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()