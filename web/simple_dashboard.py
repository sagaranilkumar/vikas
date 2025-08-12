#!/usr/bin/env python3
"""
Simplified Streamlit Web Dashboard for Specialist Feedback Management Application
Minimal dependencies version for quick testing and deployment.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.workflow_manager import WorkflowManager

# Page configuration
st.set_page_config(
    page_title="Specialist Feedback Management",
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_manager' not in st.session_state:
    st.session_state.workflow_manager = None
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = []

async def initialize_workflow():
    """Initialize the workflow manager"""
    if st.session_state.workflow_manager is None:
        workflow_manager = WorkflowManager()
        await workflow_manager.initialize()
        st.session_state.workflow_manager = workflow_manager
    return st.session_state.workflow_manager

def load_sample_data():
    """Load sample data for demonstration"""
    sample_file = Path("sample_data/sample.jsonl")
    if sample_file.exists():
        sample_data = []
        with open(sample_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    sample_data.append(json.loads(line))
        return sample_data
    return []

def load_generated_reports():
    """Load generated reports from the reports directory"""
    reports_dir = Path("reports")
    if not reports_dir.exists():
        return []
    
    reports = []
    for json_file in reports_dir.glob("*_report.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                reports.append(report_data)
        except Exception as e:
            st.error(f"Error loading report {json_file}: {e}")
    
    return sorted(reports, key=lambda x: x.get('generated_at', ''), reverse=True)

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Specialist Feedback Management System</h1>
        <p>Intelligent analysis and insights from specialist feedback data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📋 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Dashboard", "📤 Upload Feedback", "📊 Analytics"]
    )
    
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "📤 Upload Feedback":
        upload_page()
    elif page == "📊 Analytics":
        analytics_page()

def dashboard_page():
    """Main dashboard overview page"""
    st.header("📊 System Overview")
    
    # Load generated reports
    reports = load_generated_reports()
    
    # System status
    col1, col2, col3, col4 = st.columns(4)
    
    total_documents = sum(r.get('document_count', 0) for r in reports)
    total_insights = sum(r.get('insight_count', 0) for r in reports)
    total_recommendations = sum(r.get('recommendation_count', 0) for r in reports)
    total_reports = len(reports)
    
    with col1:
        st.metric(
            label="📄 Total Documents",
            value=total_documents,
        )
    
    with col2:
        st.metric(
            label="💡 Insights Generated",
            value=total_insights,
        )
    
    with col3:
        st.metric(
            label="🎯 Recommendations",
            value=total_recommendations,
        )
    
    with col4:
        st.metric(
            label="📈 Generated Reports",
            value=total_reports,
        )
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    if reports:
        latest_report = reports[0]  # Most recent report
        
        st.success(f"""
        **Latest Report Generated**
        - **Report ID:** {latest_report.get('report_id', 'N/A')}
        - **Generated:** {latest_report.get('generated_at', 'N/A')[:19].replace('T', ' ')}
        - **Documents:** {latest_report.get('document_count', 0)}
        - **Insights:** {latest_report.get('insight_count', 0)}
        - **Recommendations:** {latest_report.get('recommendation_count', 0)}
        """)
        
        # Show top insights and recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Key Insights:**")
            insights = latest_report.get('insights', [])[:3]
            for i, insight in enumerate(insights, 1):
                st.write(f"{i}. {insight.get('description', 'N/A')[:100]}...")
        
        with col2:
            st.write("**💡 Top Recommendations:**")
            recommendations = latest_report.get('recommendations', [])[:3]
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec.get('title', 'N/A')}")
                
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
    else:
        st.info("No reports generated yet. Upload some feedback data to get started!")

def upload_page():
    """Upload feedback data page"""
    st.header("📤 Upload Feedback Data")
    
    # Upload options
    upload_method = st.radio(
        "Choose upload method:",
        ["📁 Upload File", "🎯 Use Sample Data"]
    )
    
    if upload_method == "📁 Upload File":
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
                
                if st.button("🔄 Process Feedback", type="primary"):
                    process_feedback_data(feedback_data)
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    elif upload_method == "🎯 Use Sample Data":
        st.subheader("🎯 Sample Data")
        
        sample_data = load_sample_data()
        if sample_data:
            st.success(f"✅ {len(sample_data)} sample feedback items available")
            
            if st.button("🔄 Process Sample Data", type="primary"):
                process_feedback_data(sample_data)
        else:
            st.warning("⚠️ No sample data found. Please check sample_data/sample.jsonl")

def process_feedback_data(feedback_data):
    """Process feedback data through the pipeline"""
    try:
        with st.spinner("🔄 Processing feedback data..."):
            # Initialize workflow manager
            workflow_manager = asyncio.run(initialize_workflow())
            
            # Generate task ID
            task_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Process the data
            result = asyncio.run(workflow_manager.process_feedback(
                input_data=feedback_data,
                task_id=task_id
            ))
            
            # Store results
            st.session_state.processing_results.append(result)
            
            # Show success message
            st.success(f"""
            ✅ **Processing Complete!**
            - **Task ID:** {task_id}
            - **Documents Processed:** {len(result.get('cleaned_documents', []))}
            - **Insights Generated:** {len(result.get('insights', []))}
            - **Recommendations:** {len(result.get('recommendations', []))}
            """)
            
    except Exception as e:
        st.error(f"❌ Error processing feedback: {str(e)}")

def analytics_page():
    """Analytics and visualization page"""
    st.header("📊 Analytics Dashboard")
    
    # Load generated reports
    reports = load_generated_reports()
    
    if not reports:
        st.info("📈 No data available. Please process some feedback first.")
        return
    
    # Aggregate data from all reports
    sentiment_data = {}
    category_data = {}
    
    for report in reports:
        # Process sentiment data from summary
        summary = report.get('summary', {})
        sentiment_dist = summary.get('sentiment_distribution', {})
        for sentiment, count in sentiment_dist.items():
            sentiment_data[sentiment] = sentiment_data.get(sentiment, 0) + count
        
        # Process category data from summary
        category_dist = summary.get('category_distribution', {})
        for category, count in category_dist.items():
            category_data[category] = category_data.get(category, 0) + count
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        if sentiment_data:
            fig = px.pie(
                values=list(sentiment_data.values()),
                names=[name.title() for name in sentiment_data.keys()],
                title="Overall Sentiment Distribution",
                color_discrete_map={
                    'Positive': '#2E8B57',
                    'Neutral': '#4682B4', 
                    'Negative': '#DC143C'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if category_data:
            # Sort categories by count for better visualization
            sorted_categories = dict(sorted(category_data.items(), key=lambda x: x[1], reverse=True))
            fig = px.bar(
                x=list(sorted_categories.values()),
                y=[cat.replace('_', ' ').title() for cat in sorted_categories.keys()],
                orientation='h',
                title="Feedback Categories Distribution"
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    
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
    
    # Reports summary table
    st.subheader("📋 Reports Summary")
    
    if reports:
        summary_data = []
        for report in reports:
            summary_data.append({
                'Report ID': report.get('report_id', 'N/A'),
                'Generated At': report.get('generated_at', 'N/A')[:19].replace('T', ' '),
                'Documents': report.get('document_count', 0),
                'Insights': report.get('insight_count', 0),
                'Recommendations': report.get('recommendation_count', 0)
            })
        
        df = pd.DataFrame(summary_data)
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

if __name__ == "__main__":
    main()
