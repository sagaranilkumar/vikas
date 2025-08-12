#!/usr/bin/env python3
"""
Analytics Page for Specialist Feedback Management Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pages.utils import load_generated_reports, create_feedback_charts_from_reports

# Page configuration
st.set_page_config(
    page_title="Analytics - Specialist Feedback Management",
    page_icon="📊",
    layout="wide"
)

def main():
    """Analytics and visualization page"""
    
    # Navigation
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("main_dashboard.py")
    
    st.header("📊 Analytics Dashboard")
    
    # Load generated reports
    reports = load_generated_reports()
    
    if not reports:
        st.info("📈 No data available. Please process some feedback first.")
        
        # Navigation to upload
        if st.button("📤 Upload Feedback Data", use_container_width=True):
            st.switch_page("pages/upload.py")
        return
    
    # Create comprehensive charts from reports
    sentiment_fig, category_fig, priority_fig = create_feedback_charts_from_reports(reports)
    
    # Display charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        if sentiment_fig:
            st.plotly_chart(sentiment_fig, use_container_width=True)
        if priority_fig:
            st.plotly_chart(priority_fig, use_container_width=True)
    
    with col2:
        if category_fig:
            st.plotly_chart(category_fig, use_container_width=True)
    
    # Insights and Recommendations Analysis
    st.subheader("🎯 Insights & Recommendations Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Insight severity distribution
        insight_severity = {}
        for report in reports:
            summary = report.get('summary', {})
            severity_dist = summary.get('insight_severity', {})
            for severity, count in severity_dist.items():
                insight_severity[severity] = insight_severity.get(severity, 0) + count
        
        if insight_severity:
            fig = px.bar(
                x=list(insight_severity.keys()),
                y=list(insight_severity.values()),
                title="Insight Severity Distribution",
                color=list(insight_severity.keys()),
                color_discrete_map={
                    'high': '#DC143C',
                    'medium': '#FF8C00',
                    'low': '#32CD32'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Recommendation priority distribution
        rec_priority = {}
        for report in reports:
            summary = report.get('summary', {})
            priority_dist = summary.get('recommendation_priority', {})
            for priority, count in priority_dist.items():
                rec_priority[priority] = rec_priority.get(priority, 0) + count
        
        if rec_priority:
            fig = px.bar(
                x=list(rec_priority.keys()),
                y=list(rec_priority.values()),
                title="Recommendation Priority Distribution",
                color=list(rec_priority.keys()),
                color_discrete_map={
                    'high': '#DC143C',
                    'medium': '#FF8C00',
                    'low': '#32CD32'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed analytics
    st.subheader("📋 Reports Summary")
    
    # Reports timeline
    if reports:
        timeline_data = []
        for report in reports:
            timeline_data.append({
                'Report ID': report.get('report_id', 'N/A'),
                'Generated At': report.get('generated_at', 'N/A')[:19].replace('T', ' '),
                'Documents': report.get('document_count', 0),
                'Insights': report.get('insight_count', 0),
                'Recommendations': report.get('recommendation_count', 0)
            })
        
        df = pd.DataFrame(timeline_data)
        st.dataframe(df, use_container_width=True)
        
        # Download reports
        st.subheader("📥 Download Reports")
        for report in reports[:5]:  # Show last 5 reports
            report_id = report.get('report_id', 'unknown')
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{report_id}** - {report.get('document_count', 0)} documents")
            with col2:
                # Create download button for JSON report
                json_data = json.dumps(report, indent=2)
                st.download_button(
                    label="📄 JSON",
                    data=json_data,
                    file_name=f"{report_id}_report.json",
                    mime="application/json",
                    key=f"download_{report_id}"
                )
    
    # Navigation buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload More Data", use_container_width=True):
            st.switch_page("pages/upload.py")
    
    with col2:
        if st.button("📋 View Reports", use_container_width=True):
            st.switch_page("pages/reports.py")
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/settings.py")

if __name__ == "__main__":
    import json
    main()
