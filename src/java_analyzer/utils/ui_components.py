"""
UI Components
Streamlit dashboard and chart rendering components
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, Any
from utils.helpers import calculate_quality_score


def render_executive_summary(df: pd.DataFrame, metrics: Dict[str, Any]):
    """
    Render the executive dashboard with key metrics.
    
    Args:
        df: DataFrame containing detected issues
        metrics: Dictionary of code metrics
    """
    st.markdown("### 📊 Executive Dashboard")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Issues", len(df), 
                 delta=None if len(df) == 0 else f"-{len(df)} needed",
                 delta_color="inverse")
    
    with col2:
        critical_count = len(df[df['Severity'] == 'Critical'])
        st.metric("Critical", critical_count,
                 delta="Urgent" if critical_count > 0 else "Clear",
                 delta_color="inverse" if critical_count > 0 else "off")
    
    with col3:
        high_count = len(df[df['Severity'] == 'High'])
        st.metric("High Priority", high_count,
                 delta="Review" if high_count > 0 else "Good",
                 delta_color="inverse" if high_count > 0 else "off")
    
    with col4:
        severity_weights = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
        avg_sev = df['Severity'].map(severity_weights).mean() if len(df) > 0 else 0
        st.metric("Risk Index", f"{avg_sev:.2f}/4.00",
                 delta="High Risk" if avg_sev > 2.5 else "Acceptable",
                 delta_color="inverse" if avg_sev > 2.5 else "normal")
    
    with col5:
        quality_score = calculate_quality_score(len(df), critical_count)
        st.metric("Quality Score", f"{quality_score}/100",
                 delta="Pass" if quality_score > 70 else "Fail",
                 delta_color="normal" if quality_score > 70 else "inverse")


def render_code_metrics(metrics: Dict[str, Any]):
    """
    Render code metrics analysis section.
    
    Args:
        metrics: Dictionary of code metrics
    """
    st.markdown("### 📈 Code Metrics Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Structure Metrics**")
        st.metric("Total Classes", metrics['total_classes'])
        st.metric("Total Methods", metrics['total_methods'])
        st.metric("Total Fields", metrics['total_fields'])
    
    with col2:
        st.markdown("**Line Metrics**")
        st.metric("Total Lines", metrics['total_lines'])
        st.metric("Code Lines", metrics['code_lines'])
        st.metric("Comment Lines", metrics['comment_lines'])
        if metrics['total_lines'] > 0:
            comment_ratio = (metrics['comment_lines'] / metrics['total_lines']) * 100
            st.metric("Comment Ratio", f"{comment_ratio:.1f}%")
    
    with col3:
        st.markdown("**Complexity Metrics**")
        st.metric("Avg Method Length", f"{metrics['avg_method_length']:.1f}")
        st.metric("Max Method Length", metrics['max_method_length'])
        st.metric("Avg Complexity", f"{metrics['avg_complexity']:.1f}")
        st.metric("Max Complexity", metrics['max_complexity'])


def render_visualizations(df: pd.DataFrame):
    """
    Render interactive charts and visualizations.
    
    Args:
        df: DataFrame containing detected issues
    """
    st.markdown("### 📉 Visual Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Distribution", "Severity", "Categories", "Trends"])
    
    with tab1:
        _render_distribution_charts(df)
    
    with tab2:
        _render_severity_charts(df)
    
    with tab3:
        _render_category_charts(df)
    
    with tab4:
        _render_trend_charts(df)


def _render_distribution_charts(df: pd.DataFrame):
    """Render distribution pie charts."""
    col1, col2 = st.columns(2)
    
    with col1:
        if len(df) > 0:
            fig = px.pie(df, names='Type', hole=0.4, title="Issue Type Distribution",
                       color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No issues detected")
    
    with col2:
        if len(df) > 0:
            category_counts = df['Category'].value_counts().reset_index()
            category_counts.columns = ['Category', 'Count']
            fig = px.pie(category_counts, names='Category', values='Count', hole=0.4,
                       title="Category Distribution",
                       color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No issues detected")


def _render_severity_charts(df: pd.DataFrame):
    """Render severity analysis charts."""
    if len(df) > 0:
        severity_order = ["Critical", "High", "Medium", "Low"]
        df['Severity'] = pd.Categorical(df['Severity'], categories=severity_order, ordered=True)
        severity_counts = df.groupby('Severity', observed=False).size().reset_index(name='Count')
        
        fig = px.bar(severity_counts, x='Severity', y='Count', 
                    title="Severity Profile",
                    color='Severity',
                    color_discrete_map={
                        "Critical": "#DC3545", 
                        "High": "#FD7E14", 
                        "Medium": "#FFC107", 
                        "Low": "#28A745"
                    })
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Severity heatmap
        severity_by_category = df.groupby(['Category', 'Severity'], observed=False).size().reset_index(name='Count')
        fig2 = px.density_heatmap(severity_by_category, x='Category', y='Severity', z='Count',
                                 title="Severity Distribution by Category",
                                 color_continuous_scale='Reds')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.success("✅ No severity issues found - Excellent code quality!")


def _render_category_charts(df: pd.DataFrame):
    """Render category-based charts."""
    if len(df) > 0:
        category_severity = df.groupby(['Category', 'Severity'], observed=False).size().reset_index(name='Count')
        fig = px.bar(category_severity, x='Category', y='Count', color='Severity',
                    title="Issues by Category and Severity",
                    color_discrete_map={
                        "Critical": "#DC3545", 
                        "High": "#FD7E14", 
                        "Medium": "#FFC107", 
                        "Low": "#28A745"
                    },
                    barmode='stack')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data available")


def _render_trend_charts(df: pd.DataFrame):
    """Render trend analysis charts."""
    if len(df) > 0:
        type_counts = df['Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        type_counts = type_counts.sort_values('Count', ascending=True)
        
        fig = px.bar(type_counts, x='Count', y='Type', orientation='h',
                    title="Top Code Smells Detected",
                    color='Count',
                    color_continuous_scale='Reds')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("🎉 No trends to worry about - clean codebase!")


def render_detailed_findings(df: pd.DataFrame):
    """
    Render detailed findings table with filters and export options.
    
    Args:
        df: DataFrame containing detected issues
    """
    st.markdown("### 🔍 Detailed Findings")
    
    if len(df) > 0:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.multiselect("Filter by Severity", 
                                           options=df['Severity'].unique(),
                                           default=df['Severity'].unique())
        with col2:
            category_filter = st.multiselect("Filter by Category",
                                           options=df['Category'].unique(),
                                           default=df['Category'].unique())
        with col3:
            type_filter = st.multiselect("Filter by Type",
                                        options=df['Type'].unique(),
                                        default=df['Type'].unique())
        
        filtered_df = df[
            (df['Severity'].isin(severity_filter)) &
            (df['Category'].isin(category_filter)) &
            (df['Type'].isin(type_filter))
        ]
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=400)
        
        # Export options
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export CSV", csv, 
                             f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
                             "text/csv", use_container_width=True)
        with col2:
            json_data = filtered_df.to_json(orient='records', indent=2)
            st.download_button("📥 Export JSON", json_data,
                             f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                             "application/json", use_container_width=True)
    else:
        st.success("✨ No issues found! Your code meets all quality standards.")


def render_source_code_viewer(source_code: str):
    """
    Render source code viewer in an expandable section.
    
    Args:
        source_code: The Java source code to display
    """
    with st.expander("📝 Source Code Viewer"):
        st.code(source_code, language='java', line_numbers=True)


def render_summary_report(df: pd.DataFrame, metrics: Dict[str, Any], file_name: str):
    """
    Render executive summary report with download option.
    
    Args:
        df: DataFrame containing detected issues
        metrics: Dictionary of code metrics
        file_name: Name of the analyzed file
    """
    if len(df) > 0:
        st.markdown("---")
        st.markdown("### 📋 Executive Summary Report")
        
        report = f"""
**Analysis Report - {file_name}**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Quality Metrics:**
- Total Issues: {len(df)}
- Critical: {len(df[df['Severity'] == 'Critical'])}
- High: {len(df[df['Severity'] == 'High'])}
- Medium: {len(df[df['Severity'] == 'Medium'])}
- Low: {len(df[df['Severity'] == 'Low'])}

**Code Metrics:**
- Classes: {metrics['total_classes']}
- Methods: {metrics['total_methods']}
- Lines of Code: {metrics['code_lines']}
- Average Complexity: {metrics['avg_complexity']:.2f}

**Recommendations:**
{'- Address Critical issues immediately' if len(df[df['Severity'] == 'Critical']) > 0 else '- No critical issues found'}
{'- Review High priority items' if len(df[df['Severity'] == 'High']) > 0 else '- Code quality is acceptable'}
        """
        
        st.text_area("Report Summary", report, height=300)
        st.download_button("📥 Download Full Report", report, 
                         f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                         use_container_width=True)


def render_landing_page():
    """Render the landing page with instructions."""
    st.markdown("### 🎯 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 📤 Step 1: Upload
        Select your Java source file from the sidebar to begin analysis.
        """)
    
    with col2:
        st.markdown("""
        #### ⚙️ Step 2: Configure
        Choose which analyzers to run based on your needs.
        """)
    
    with col3:
        st.markdown("""
        #### 🚀 Step 3: Analyze
        Click "Run Deep Analysis" to get comprehensive insights.
        """)
    
    st.markdown("---")
    st.markdown("### 🔍 What We Analyze")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Design Smells:**
        - God Class Detection
        - Swiss Army Knife Pattern
        - Data Class Identification
        - Feature Envy
        - Lazy Class
        
        **Implementation Smells:**
        - High Cyclomatic Complexity
        - Long Methods
        - Long Parameter Lists
        - Empty Catch Blocks
        - Magic Numbers
        - Deep Nesting
        """)
    
    with col2:
        st.markdown("""
        **Naming Conventions:**
        - Class Name Validation
        - Method Name Standards
        - Identifier Length Checks
        
        **Documentation:**
        - Javadoc Coverage
        - Public API Documentation
        - Class Documentation
        
        **Metrics:**
        - Lines of Code Analysis
        - Comment Ratio
        - Method Complexity
        - Class Structure
        """)
    
    st.info("👆 Upload a Java file from the sidebar to start your comprehensive code analysis")