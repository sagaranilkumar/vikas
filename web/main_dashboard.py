#!/usr/bin/env python3
"""
Main Dashboard Entry Point for Customer Feedback Management Application
Multi-page Streamlit application with proper navigation.
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Page configuration
st.set_page_config(
    page_title="Customer Feedback Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard page"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Customer Feedback Management System</h1>
        <p>Intelligent analysis and insights from Customer feedback data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Import and load data functions
    from pages.utils import load_generated_reports, create_feedback_charts_from_reports
    
    # Load generated reports
    reports = load_generated_reports()
    
    # System status
    st.header("📊 System Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_documents = sum(r.get('document_count', 0) for r in reports)
    total_insights = sum(r.get('insight_count', 0) for r in reports)
    total_recommendations = sum(r.get('recommendation_count', 0) for r in reports)
    total_reports = len(reports)
    
    with col1:
        st.metric(
            label="📄 Total Documents Processed",
            value=total_documents,
            delta="Active"
        )
    
    with col2:
        st.metric(
            label="💡 Insights Generated",
            value=total_insights,
            delta="Latest batch"
        )
    
    with col3:
        st.metric(
            label="🎯 Recommendations",
            value=total_recommendations,
            delta="Ready"
        )
    
    with col4:
        st.metric(
            label="📈 Generated Reports",
            value=total_reports,
            delta="Completed"
        )
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    if reports:
        latest_report = reports[0]  # Most recent report
        
        st.markdown(f"""
        <div class="info-box">
            <h4>Latest Report Generated</h4>
            <p><strong>Report ID:</strong> {latest_report.get('report_id', 'N/A')}</p>
            <p><strong>Generated:</strong> {latest_report.get('generated_at', 'N/A')[:19].replace('T', ' ')}</p>
            <p><strong>Documents:</strong> {latest_report.get('document_count', 0)}</p>
            <p><strong>Insights:</strong> {latest_report.get('insight_count', 0)}</p>
            <p><strong>Recommendations:</strong> {latest_report.get('recommendation_count', 0)}</p>
            <hr/>
            <p><em>Quality & Confidence</em></p>
            <p><strong>Total Input Documents:</strong> {latest_report.get('summary', {}).get('total_documents', 'N/A')}</p>
            {('<p><strong>Cleaned Documents:</strong> ' + f"{latest_report.get('summary', {}).get('cleaned_percentage', 0):.2f}%" + '</p>') if latest_report.get('summary', {}).get('cleaned_percentage') is not None else ''}
            {('<p><strong>Avg Sentiment Confidence:</strong> ' + f"{(latest_report.get('summary', {}).get('avg_sentiment_confidence', 0) * 100):.2f}%" + '</p>') if latest_report.get('summary', {}).get('avg_sentiment_confidence') is not None else ''}
            {('<p><strong>Avg Primary Category Probability:</strong> ' + f"{(latest_report.get('summary', {}).get('avg_primary_category_probability', 0) * 100):.2f}%" + '</p>') if latest_report.get('summary', {}).get('avg_primary_category_probability') is not None else ''}
        </div>
        """, unsafe_allow_html=True)
        
        # Show summary statistics
        st.subheader("📈 Summary Statistics")
        summary = latest_report.get('summary', {})
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Sentiment Distribution:**")
            sentiment_dist = summary.get('sentiment_distribution', {})
            for sentiment, count in sentiment_dist.items():
                st.write(f"- {sentiment.title()}: {count}")
        
        with col2:
            st.write("**Top Categories:**")
            category_dist = summary.get('category_distribution', {})
            sorted_categories = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:5]
            for category, count in sorted_categories:
                st.write(f"- {category.replace('_', ' ').title()}: {count}")

        # New quality and confidence metrics from latest report
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
        
        # Quick charts from report data
        if reports:
            sentiment_fig, category_fig, priority_fig = create_feedback_charts_from_reports(reports)
            
            col1, col2 = st.columns(2)
            with col1:
                if sentiment_fig:
                    st.plotly_chart(sentiment_fig, use_container_width=True)
            with col2:
                if priority_fig:
                    st.plotly_chart(priority_fig, use_container_width=True)
    else:
        st.info("No reports generated yet. Upload some feedback data to get started!")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload New Feedback", use_container_width=True):
            st.switch_page("pages/upload.py")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")
    
    with col3:
        if st.button("📋 Generate Report", use_container_width=True):
            st.switch_page("pages/reports.py")

if __name__ == "__main__":
    main()
