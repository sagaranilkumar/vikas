#!/usr/bin/env python3
"""
Streamlit Web Dashboard for Specialist Feedback Management Application
Provides a user-friendly interface for uploading feedback, monitoring processing, and viewing reports.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow.workflow_manager import WorkflowManager
from models.feedback_models import FeedbackDocument

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
    .error-box {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
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
</style>
""", unsafe_allow_html=True)

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

def create_feedback_charts(results):
    """Create visualization charts from processing results"""
    if not results:
        return None, None, None
    
    # Aggregate data
    sentiment_data = {}
    category_data = {}
    priority_data = {}
    
    for result in results:
        # Process sentiment data
        for sentiment_result in result.get('sentiment_results', []):
            sentiment = sentiment_result.get('overall_sentiment', 'unknown')
            sentiment_data[sentiment] = sentiment_data.get(sentiment, 0) + 1
        
        # Process category data
        for category_result in result.get('categorization_results', []):
            category = category_result.get('primary_category', 'unknown')
            category_data[category] = category_data.get(category, 0) + 1
        
        # Process priority data
        for rec in result.get('recommendations', []):
            priority = rec.get('priority', 'unknown')
            priority_data[priority] = priority_data.get(priority, 0) + 1
    
    # Create charts
    sentiment_fig = None
    if sentiment_data:
        sentiment_fig = px.pie(
            values=list(sentiment_data.values()),
            names=list(sentiment_data.keys()),
            title="Sentiment Distribution"
        )
    
    category_fig = None
    if category_data:
        category_fig = px.bar(
            x=list(category_data.keys()),
            y=list(category_data.values()),
            title="Category Distribution"
        )
    
    priority_fig = None
    if priority_data:
        priority_fig = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="Recommendation Priority"
        )
    
    return sentiment_fig, category_fig, priority_fig

def create_feedback_charts_from_reports(reports):
    """Create visualization charts from generated reports"""
    if not reports:
        return None, None, None
    
    # Aggregate data from all reports
    sentiment_data = {}
    category_data = {}
    priority_data = {}
    
    for report in reports:
        summary = report.get('summary', {})
        
        # Process sentiment data from summary
        sentiment_dist = summary.get('sentiment_distribution', {})
        for sentiment, count in sentiment_dist.items():
            sentiment_data[sentiment] = sentiment_data.get(sentiment, 0) + count
        
        # Process category data from summary
        category_dist = summary.get('category_distribution', {})
        for category, count in category_dist.items():
            category_data[category] = category_data.get(category, 0) + count
        
        # Process priority data from summary
        priority_dist = summary.get('recommendation_priority', {})
        for priority, count in priority_dist.items():
            priority_data[priority] = priority_data.get(priority, 0) + count
    
    # Create charts
    sentiment_fig = None
    if sentiment_data:
        sentiment_fig = px.pie(
            values=list(sentiment_data.values()),
            names=[name.title() for name in sentiment_data.keys()],
            title="Overall Sentiment Distribution",
            color_discrete_map={
                'Positive': '#2E8B57',
                'Neutral': '#4682B4', 
                'Negative': '#DC143C'
            }
        )
    
    category_fig = None
    if category_data:
        sorted_categories = dict(sorted(category_data.items(), key=lambda x: x[1], reverse=True))
        category_fig = px.bar(
            x=list(sorted_categories.values()),
            y=[cat.replace('_', ' ').title() for cat in sorted_categories.keys()],
            orientation='h',
            title="Feedback Categories Distribution"
        )
        category_fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    priority_fig = None
    if priority_data:
        priority_fig = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="Recommendation Priority Distribution",
            color=list(priority_data.keys()),
            color_discrete_map={
                'high': '#DC143C',
                'medium': '#FF8C00',
                'low': '#32CD32'
            }
        )
    
    return sentiment_fig, category_fig, priority_fig

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
        ["🏠 Dashboard", "📤 Upload Feedback", "📊 Analytics", "📋 Reports", "⚙️ Settings"]
    )
    
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "📤 Upload Feedback":
        upload_page()
    elif page == "📊 Analytics":
        analytics_page()
    elif page == "📋 Reports":
        reports_page()
    elif page == "⚙️ Settings":
        settings_page()

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
        st.info("No processing results yet. Upload some feedback data to get started!")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📤 Upload New Feedback", use_container_width=True):
            st.info("📤 Navigate to 'Upload Feedback' page using the sidebar to upload new data.")
    
    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("📊 Navigate to 'Analytics' page using the sidebar to view detailed analytics.")
    
    with col3:
        if st.button("📋 Generate Report", use_container_width=True):
            st.info("📋 Navigate to 'Reports' page using the sidebar to view and export reports.")

def upload_page():
    """Upload feedback data page"""
    st.header("📤 Upload Feedback Data")
    
    # Upload options
    upload_method = st.radio(
        "Choose upload method:",
        ["📁 Upload File", "📝 Manual Entry", "🎯 Use Sample Data"]
    )
    
    if upload_method == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Choose a JSONL file",
            type=['jsonl', 'json'],
            help="Upload a JSONL file with feedback documents"
        )
        
        if uploaded_file is not None:
            try:
                # Read uploaded file
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
                        "entry_method": "manual",
                        "created_by": "dashboard_user"
                    }
                }
                
                process_feedback_data([feedback_item])
    
    elif upload_method == "🎯 Use Sample Data":
        st.subheader("🎯 Sample Data")
        st.info("Use pre-loaded sample data to test the system")
        
        sample_data = load_sample_data()
        if sample_data:
            st.success(f"✅ {len(sample_data)} sample feedback items available")
            
            # Show sample preview
            if st.checkbox("👀 Preview Sample Data"):
                df = pd.DataFrame(sample_data[:5])
                st.dataframe(df)
            
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
            <div class="success-box">
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
                st.write("**🎯 Key Insights:**")
                insights = result.get('insights', [])[:3]  # Show top 3
                for i, insight in enumerate(insights, 1):
                    st.write(f"{i}. {insight.get('description', 'N/A')[:100]}...")
            
            with col2:
                st.write("**💡 Top Recommendations:**")
                recommendations = result.get('recommendations', [])[:3]  # Show top 3
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec.get('title', 'N/A')}")
            
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

def reports_page():
    """Reports and export page"""
    st.header("📋 Reports & Export")
    
    # Load generated reports
    reports = load_generated_reports()
    
    if not reports:
        st.info("📄 No reports available. Please process some feedback first.")
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
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📄 Documents", len(selected_result.get('cleaned_documents', [])))
            with col2:
                st.metric("💡 Insights", len(selected_result.get('insights', [])))
            with col3:
                st.metric("🎯 Recommendations", len(selected_result.get('recommendations', [])))
            
            # Detailed sections
            tab1, tab2, tab3 = st.tabs(["💡 Insights", "🎯 Recommendations", "📊 Data"])
            
            with tab1:
                insights = selected_result.get('insights', [])
                for i, insight in enumerate(insights, 1):
                    st.write(f"**{i}. {insight.get('insight_type', 'Unknown').replace('_', ' ').title()}**")
                    st.write(insight.get('description', 'No description available'))
                    st.write("---")
            
            with tab2:
                recommendations = selected_result.get('recommendations', [])
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"**{i}. {rec.get('title', 'No title')}**")
                    st.write(f"*Priority: {rec.get('priority', 'Medium')} | Timeline: {rec.get('timeline', 'Unknown')}*")
                    st.write(rec.get('description', 'No description available'))
                    st.write("---")
            
            with tab3:
                # Export options
                st.subheader("📤 Export Options")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📄 Export as JSON"):
                        json_data = json.dumps(selected_result, indent=2, default=str)
                        st.download_button(
                            label="⬇️ Download JSON",
                            data=json_data,
                            file_name=f"report_{selected_task}.json",
                            mime="application/json"
                        )
                
                with col2:
                    if st.button("📊 Export as CSV"):
                        # Create CSV data
                        csv_data = []
                        for insight in selected_result.get('insights', []):
                            csv_data.append({
                                'Type': 'Insight',
                                'Category': insight.get('insight_type', ''),
                                'Description': insight.get('description', ''),
                                'Severity': insight.get('severity', ''),
                            })
                        
                        for rec in selected_result.get('recommendations', []):
                            csv_data.append({
                                'Type': 'Recommendation',
                                'Category': rec.get('category', ''),
                                'Description': rec.get('title', ''),
                                'Priority': rec.get('priority', ''),
                            })
                        
                        if csv_data:
                            df = pd.DataFrame(csv_data)
                            csv_string = df.to_csv(index=False)
                            st.download_button(
                                label="⬇️ Download CSV",
                                data=csv_string,
                                file_name=f"report_{selected_task}.csv",
                                mime="text/csv"
                            )

def settings_page():
    """Settings and configuration page"""
    st.header("⚙️ Settings")
    
    st.subheader("🔧 System Configuration")
    
    # Processing settings
    with st.expander("🔄 Processing Settings"):
        st.slider("Batch Size", min_value=10, max_value=1000, value=100)
        st.selectbox("Default Output Format", ["JSON", "HTML", "Both"])
        st.checkbox("Enable Detailed Logging", value=True)
    
    # Data settings
    with st.expander("📊 Data Settings"):
        st.text_input("Default Output Directory", value="./output")
        st.checkbox("Auto-save Results", value=True)
        st.slider("Max Results to Keep", min_value=10, max_value=100, value=50)
    
    # System info
    st.subheader("ℹ️ System Information")
    
    info_data = {
        "System Status": "✅ Operational",
        "Pipeline Version": "1.0.0",
        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Total Processing Tasks": len(st.session_state.processing_results)
    }
    
    for key, value in info_data.items():
        st.write(f"**{key}:** {value}")
    
    # Clear data
    st.subheader("🗑️ Data Management")
    if st.button("🗑️ Clear All Results", type="secondary"):
        if st.checkbox("⚠️ I understand this will delete all processing results"):
            st.session_state.processing_results = []
            st.success("✅ All results cleared!")

if __name__ == "__main__":
    main()
