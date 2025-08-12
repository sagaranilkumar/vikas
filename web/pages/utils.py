#!/usr/bin/env python3
"""
Utility functions for the Streamlit dashboard pages
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
