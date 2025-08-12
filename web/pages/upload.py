#!/usr/bin/env python3
"""
Upload Feedback Page for Specialist Feedback Management Application
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflow.workflow_manager import WorkflowManager
from pages.utils import load_sample_data

# Page configuration
st.set_page_config(
    page_title="Upload Feedback - Specialist Feedback Management",
    page_icon="📤",
    layout="wide"
)

# Initialize session state
if 'workflow_manager' not in st.session_state:
    st.session_state.workflow_manager = None
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []
if 'current_task_id' not in st.session_state:
    st.session_state.current_task_id = None

async def initialize_workflow():
    """Initialize the workflow manager"""
    if st.session_state.workflow_manager is None:
        workflow_manager = WorkflowManager()
        await workflow_manager.initialize()
        st.session_state.workflow_manager = workflow_manager
    return st.session_state.workflow_manager

def process_feedback_data(feedback_data):
    """Process feedback data through the pipeline"""
    try:
        with st.spinner("🔄 Processing feedback data..."):
            # Initialize workflow manager
            workflow_manager = asyncio.run(initialize_workflow())
            
            # Generate task ID
            task_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.current_task_id = task_id
            
            # Process the data
            result = asyncio.run(workflow_manager.process_feedback(
                input_data=feedback_data,
                task_id=task_id
            ))
            
            # Store results
            st.session_state.processing_results.append(result)
            
            # Show success message
            st.markdown(f"""
            <div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; padding: 1rem; margin: 1rem 0;">
                <h4>✅ Processing Complete!</h4>
                <p><strong>Task ID:</strong> {task_id}</p>
                <p><strong>Documents Processed:</strong> {len(result.get('cleaned_documents', []))}</p>
                <p><strong>Insights Generated:</strong> {len(result.get('insights', []))}</p>
                <p><strong>Recommendations:</strong> {len(result.get('recommendations', []))}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show processing summary
            st.subheader("📊 Processing Summary")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**📄 Documents Processed:**")
                st.write(f"- Total: {len(result.get('cleaned_documents', []))}")
                st.write(f"- Task ID: {task_id}")
                
            with col2:
                st.write("**🎯 Results Generated:**")
                st.write(f"- Insights: {len(result.get('insights', []))}")
                st.write(f"- Recommendations: {len(result.get('recommendations', []))}")
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Analytics", use_container_width=True):
                    st.switch_page("pages/analytics.py")
            with col2:
                if st.button("📋 View Reports", use_container_width=True):
                    st.switch_page("pages/reports.py")
            
    except Exception as e:
        st.error(f"❌ Error processing feedback: {str(e)}")

def main():
    """Upload feedback data page"""
    
    # Navigation
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.switch_page("main_dashboard.py")
    
    st.header("📤 Upload Feedback Data")
    
    # Upload options
    upload_method = st.radio(
        "Choose upload method:",
        ["📁 Upload File", "📝 Manual Entry", "🎯 Use Sample Data"]
    )
    
    if upload_method == "📁 Upload File":
        st.subheader("📁 File Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a JSONL file",
            type=['jsonl', 'json'],
            help="Upload a JSONL file with feedback documents"
        )
        
        if uploaded_file is not None:
            try:
                content = uploaded_file.read().decode('utf-8')
                feedback_data = []
                
                if uploaded_file.name.endswith('.jsonl'):
                    for line in content.split('\n'):
                        if line.strip():
                            feedback_data.append(json.loads(line))
                else:
                    feedback_data = [json.loads(content)]
                
                st.success(f"✅ Loaded {len(feedback_data)} feedback items")
                
                # Preview data
                if feedback_data:
                    st.subheader("📋 Data Preview")
                    df = pd.DataFrame(feedback_data[:5])  # Show first 5 items
                    st.dataframe(df)
                
                # Process button
                if st.button("🔄 Process Feedback", type="primary"):
                    process_feedback_data(feedback_data)
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    elif upload_method == "📝 Manual Entry":
        st.subheader("✍️ Enter Feedback Manually")
        
        with st.form("manual_feedback_form"):
            filename = st.text_input("Filename", value="manual_feedback.txt")
            content = st.text_area("Feedback Content", height=150)
            source = st.selectbox("Source", ["expert_report", "internal_assessment", "peer_review", "technical_review", "process_evaluation", "quality_audit", "other"])
            
            submitted = st.form_submit_button("➕ Add Feedback")
            
            if submitted and content:
                feedback_item = {
                    "id": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "filename": filename,
                    "content": content,
                    "content_type": "text/plain",
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {
                        "manual_entry": True,
                        "entry_time": datetime.now().isoformat()
                    }
                }
                
                st.success("✅ Feedback item created successfully!")
                
                # Show preview
                st.subheader("📋 Preview")
                st.json(feedback_item)
                
                # Process button
                if st.button("🔄 Process This Feedback", type="primary"):
                    process_feedback_data([feedback_item])
    
    elif upload_method == "🎯 Use Sample Data":
        st.subheader("🎯 Sample Data")
        
        sample_data = load_sample_data()
        if sample_data:
            st.success(f"✅ {len(sample_data)} sample feedback items available")
            
            # Show sample preview
            st.subheader("📋 Sample Data Preview")
            df = pd.DataFrame(sample_data[:3])  # Show first 3 items
            st.dataframe(df)
            
            if st.button("🔄 Process Sample Data", type="primary"):
                process_feedback_data(sample_data)
        else:
            st.warning("⚠️ No sample data found. Please check sample_data/sample.jsonl")

if __name__ == "__main__":
    main()
