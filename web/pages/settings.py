#!/usr/bin/env python3
"""
Settings Page for Specialist Feedback Management Application
"""

import streamlit as st
import json
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pages.utils import load_generated_reports

# Page configuration
st.set_page_config(
    page_title="Settings - Specialist Feedback Management",
    page_icon="⚙️",
    layout="wide"
)

def main():
    """Settings and configuration page"""
    
    # Navigation
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("main_dashboard.py")
    
    st.header("⚙️ Settings & Configuration")
    
    # System Information
    st.subheader("📊 System Information")
    
    # Load reports for system stats
    reports = load_generated_reports()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reports", len(reports))
    with col2:
        total_docs = sum(r.get('document_count', 0) for r in reports)
        st.metric("Total Documents Processed", total_docs)
    with col3:
        total_insights = sum(r.get('insight_count', 0) for r in reports)
        st.metric("Total Insights Generated", total_insights)
    
    # Data Management
    st.subheader("📁 Data Management")
    
    # Reports directory info
    reports_dir = Path("reports")
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.json"))
        html_files = list(reports_dir.glob("*.html"))
        
        st.write(f"**Reports Directory:** `{reports_dir.absolute()}`")
        st.write(f"- JSON Reports: {len(report_files)}")
        st.write(f"- HTML Reports: {len(html_files)}")
        
        # Clear reports option
        if st.button("🗑️ Clear All Reports", type="secondary"):
            if st.checkbox("I understand this will delete all generated reports"):
                try:
                    for file in report_files + html_files:
                        file.unlink()
                    st.success("✅ All reports cleared successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error clearing reports: {e}")
    else:
        st.info("📁 Reports directory not found. Process some feedback to generate reports.")
    
    # Sample data info
    st.subheader("🎯 Sample Data")
    sample_file = Path("sample_data/sample.jsonl")
    if sample_file.exists():
        st.write(f"**Sample Data File:** `{sample_file.absolute()}`")
        try:
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_count = sum(1 for line in f if line.strip())
            st.write(f"- Sample Items: {sample_count}")
        except Exception as e:
            st.write(f"- Error reading sample file: {e}")
    else:
        st.info("🎯 Sample data file not found.")
    
    # Configuration
    st.subheader("⚙️ Configuration")
    
    # Environment variables
    env_file = Path(".env")
    if env_file.exists():
        st.write("**Environment Configuration:** ✅ `.env` file found")
    else:
        st.write("**Environment Configuration:** ⚠️ `.env` file not found")
        if st.button("📝 Create .env Template"):
            env_template = """# API Configuration
OPENAI_API_KEY=your_openai_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Processing Configuration
MAX_CONCURRENT_TASKS=5
BATCH_SIZE=100
CONFIDENCE_THRESHOLD=0.7

# Output Configuration
OUTPUT_FORMAT=json
REPORT_TEMPLATE=default

# Dashboard Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=localhost
"""
            try:
                with open(".env", 'w') as f:
                    f.write(env_template)
                st.success("✅ .env template created successfully!")
            except Exception as e:
                st.error(f"❌ Error creating .env file: {e}")
    
    # Dashboard Configuration
    st.subheader("🌐 Dashboard Configuration")
    
    streamlit_config = Path("web/.streamlit/config.toml")
    if streamlit_config.exists():
        st.write("**Streamlit Config:** ✅ Configuration file found")
        try:
            with open(streamlit_config, 'r') as f:
                config_content = f.read()
            with st.expander("View Configuration"):
                st.code(config_content, language="toml")
        except Exception as e:
            st.write(f"Error reading config: {e}")
    else:
        st.write("**Streamlit Config:** ⚠️ Configuration file not found")
    
    # System Health
    st.subheader("🏥 System Health")
    
    # Check dependencies
    try:
        import streamlit
        st.write(f"✅ Streamlit: {streamlit.__version__}")
    except ImportError:
        st.write("❌ Streamlit: Not installed")
    
    try:
        import plotly
        st.write(f"✅ Plotly: {plotly.__version__}")
    except ImportError:
        st.write("❌ Plotly: Not installed")
    
    try:
        import pandas
        st.write(f"✅ Pandas: {pandas.__version__}")
    except ImportError:
        st.write("❌ Pandas: Not installed")
    
    # Navigation buttons
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload Data", use_container_width=True):
            st.switch_page("pages/upload.py")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/analytics.py")
    
    with col3:
        if st.button("📋 View Reports", use_container_width=True):
            st.switch_page("pages/reports.py")

if __name__ == "__main__":
    main()
