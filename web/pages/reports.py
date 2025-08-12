#!/usr/bin/env python3
"""
Reports Page for Specialist Feedback Management Application
"""

import streamlit as st
import json
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pages.utils import load_generated_reports

# Page configuration
st.set_page_config(
    page_title="Reports - Specialist Feedback Management",
    page_icon="📋",
    layout="wide"
)

def main():
    """Reports and export page"""
    
    # Navigation
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("main_dashboard.py")
    
    st.header("📋 Reports & Export")
    
    # Load generated reports
    reports = load_generated_reports()
    
    if not reports:
        st.info("📄 No reports available. Please process some feedback first.")
        
        # Navigation to upload
        if st.button("📤 Upload Feedback Data", use_container_width=True):
            st.switch_page("pages/upload.py")
        return
    
    # Report selection
    report_ids = [r.get('report_id', 'Unknown') for r in reports]
    selected_report_id = st.selectbox("Select a report:", report_ids)
    
    if selected_report_id:
        # Find the selected report
        selected_report = None
        for report in reports:
            if report.get('report_id') == selected_report_id:
                selected_report = report
                break
        
        if selected_report:
            # Display report summary
            st.subheader(f"📊 Report: {selected_report_id}")
            
            # Report metadata
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Documents", selected_report.get('document_count', 0))
            with col2:
                st.metric("Insights", selected_report.get('insight_count', 0))
            with col3:
                st.metric("Recommendations", selected_report.get('recommendation_count', 0))
            
            # Report details
            st.write(f"**Generated:** {selected_report.get('generated_at', 'N/A')[:19].replace('T', ' ')}")
            
            # Summary statistics
            st.subheader("📈 Summary Statistics")
            summary = selected_report.get('summary', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Sentiment Distribution:**")
                sentiment_dist = summary.get('sentiment_distribution', {})
                for sentiment, count in sentiment_dist.items():
                    st.write(f"- {sentiment.title()}: {count}")
            
            with col2:
                st.write("**Category Distribution:**")
                category_dist = summary.get('category_distribution', {})
                sorted_categories = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:5]
                for category, count in sorted_categories:
                    st.write(f"- {category.replace('_', ' ').title()}: {count}")

            # New quality and confidence metrics
            st.markdown("**🧪 Quality & Confidence Metrics:**")
            if summary.get('total_documents'):
                st.write(f"- Total Input Documents: {summary.get('total_documents')}")
            if summary.get('cleaned_percentage') is not None:
                try:
                    st.write(f"- Cleaned Documents: {float(summary.get('cleaned_percentage')):.2f}%")
                except Exception:
                    pass
            if summary.get('avg_sentiment_confidence') is not None:
                try:
                    st.write(f"- Avg Sentiment Confidence: {float(summary.get('avg_sentiment_confidence')) * 100:.2f}%")
                except Exception:
                    pass
            if summary.get('avg_primary_category_probability') is not None:
                try:
                    st.write(f"- Avg Primary Category Probability: {float(summary.get('avg_primary_category_probability')) * 100:.2f}%")
                except Exception:
                    pass
            
            # Insights section
            st.subheader("💡 Key Insights")
            insights = selected_report.get('insights', [])
            for i, insight in enumerate(insights[:5], 1):
                with st.expander(f"Insight {i}: {insight.get('type', 'N/A').replace('_', ' ').title()}"):
                    st.write(f"**Description:** {insight.get('description', 'N/A')}")
                    st.write(f"**Severity:** {insight.get('severity', 'N/A').title()}")
                    if insight.get('confidence'):
                        st.write(f"**Confidence:** {insight.get('confidence', 0):.2f}")
            
            # Recommendations section
            st.subheader("🎯 Recommendations")
            recommendations = selected_report.get('recommendations', [])
            for i, rec in enumerate(recommendations[:5], 1):
                with st.expander(f"Recommendation {i}: {rec.get('title', 'N/A')}"):
                    st.write(f"**Description:** {rec.get('description', 'N/A')}")
                    st.write(f"**Priority:** {rec.get('priority', 'N/A').title()}")
                    if rec.get('expected_impact'):
                        st.write(f"**Expected Impact:** {rec.get('expected_impact', 'N/A')}")
            
            # Export options
            st.subheader("📥 Export Options")
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                json_data = json.dumps(selected_report, indent=2)
                st.download_button(
                    label="📄 Download JSON Report",
                    data=json_data,
                    file_name=f"{selected_report_id}_report.json",
                    mime="application/json"
                )
            
            with col2:
                # CSV export for summary data
                summary_df = pd.DataFrame([
                    {'Metric': 'Documents', 'Count': selected_report.get('document_count', 0)},
                    {'Metric': 'Insights', 'Count': selected_report.get('insight_count', 0)},
                    {'Metric': 'Recommendations', 'Count': selected_report.get('recommendation_count', 0)}
                ])
                csv_data = summary_df.to_csv(index=False)
                st.download_button(
                    label="📈 Download CSV Summary",
                    data=csv_data,
                    file_name=f"{selected_report_id}_summary.csv",
                    mime="text/csv"
                )
    
    # Navigation buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload More Data", use_container_width=True):
            st.switch_page("pages/upload.py")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.switch_page("pages/settings.py")

if __name__ == "__main__":
    main()
