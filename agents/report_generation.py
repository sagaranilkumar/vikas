"""
Report Generation Agent - Generates comprehensive reports from processed feedback data
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging

from models.feedback_models import (
    CleanedDocument, SentimentAnalysis, CategoryResult, 
    InsightData, Recommendation, ProcessingStatus, ProcessingResult
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ReportGenerationAgent:
    """
    Agent responsible for generating comprehensive reports from processed feedback data.
    Handles formatting, visualization, and output of analysis results.
    """
    
    def __init__(self, output_dir: str = "./reports"):
        """Initialize the ReportGenerationAgent"""
        self.agent_id = "report_generation_agent"
        self.status = "idle"
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / "assets"
        
        # Create output directories if they don't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the agent and any required resources"""
        self.status = "initializing"
        logger.info(f"Initializing {self.agent_id}")
        
        try:
            # Any initialization code would go here
            self.status = "ready"
            logger.info(f"{self.agent_id} initialized successfully")
            return {"status": "success", "message": f"{self.agent_id} initialized"}
            
        except Exception as e:
            self.status = "error"
            error_msg = f"Error initializing {self.agent_id}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    async def generate_report(
        self,
        cleaned_documents: List[CleanedDocument],
        sentiment_results: List[SentimentAnalysis],
        categorization_results: List[CategoryResult],
        insights: List[InsightData],
        recommendations: List[Recommendation],
        task_id: Optional[str] = None,
        output_format: str = "all"
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive report from processed feedback data
        
        Args:
            cleaned_documents: List of cleaned feedback documents
            sentiment_results: List of sentiment analysis results
            categorization_results: List of categorization results
            insights: List of generated insights
            recommendations: List of generated recommendations
            task_id: Optional task ID for tracking
            output_format: Format of the report ('html', 'json', or 'all')
            
        Returns:
            Dictionary containing report data and paths to generated files
        """
        self.status = "processing"
        task_id = task_id or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()
        
        try:
            logger.info(f"Generating report for task {task_id}")
            
            # Prepare report data
            report_data = await self._prepare_report_data(
                cleaned_documents=cleaned_documents,
                sentiment_results=sentiment_results,
                categorization_results=categorization_results,
                insights=insights,
                recommendations=recommendations,
                task_id=task_id
            )
            
            # Generate the requested report formats
            generated_files = {}
            
            if output_format in ['html', 'all']:
                html_report = await self._generate_html_report(report_data, task_id)
                generated_files['html'] = html_report
            
            if output_format in ['json', 'all']:
                json_report = await self._generate_json_report(report_data, task_id)
                generated_files['json'] = json_report
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            self.status = "completed"
            logger.info(f"Report generation completed for task {task_id} in {processing_time:.2f} seconds")
            
            return {
                "status": "success",
                "task_id": task_id,
                "processing_time_seconds": processing_time,
                "generated_files": generated_files,
                "report_data": report_data
            }
            
        except Exception as e:
            self.status = "error"
            error_msg = f"Error generating report: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "task_id": task_id,
                "message": error_msg
            }
    
    async def _prepare_report_data(
        self,
        cleaned_documents: List[CleanedDocument],
        sentiment_results: List[SentimentAnalysis],
        categorization_results: List[CategoryResult],
        insights: List[InsightData],
        recommendations: List[Recommendation],
        task_id: str
    ) -> Dict[str, Any]:
        """Prepare data for the report"""
        logger.info("Preparing report data")
        
        # Basic report metadata
        report_data = {
            "report_id": task_id,
            "generated_at": datetime.now().isoformat(),
            "document_count": len(cleaned_documents),
            "insight_count": len(insights),
            "recommendation_count": len(recommendations)
        }
        
        # Add summary statistics
        report_data["summary"] = self._generate_summary(
            sentiment_results, 
            categorization_results,
            insights,
            recommendations
        )
        
        # Add detailed data sections
        report_data["sentiment_analysis"] = [
            {
                "document_id": s.document_id,
                "sentiment": s.overall_sentiment,
                "score": s.sentiment_score,
                "confidence": s.confidence,
                "key_phrases": s.key_phrases
            }
            for s in sentiment_results
        ]
        
        report_data["categorization"] = [
            {
                "document_id": c.document_id,
                "primary_category": c.primary_category,
                "secondary_categories": c.secondary_categories,
                "category_confidence": c.category_confidence,
                "keywords": c.keywords,
                "topics": c.topics
            }
            for c in categorization_results
        ]
        
        report_data["insights"] = [
            {
                "id": f"insight_{idx}",
                "type": i.insight_type,
                "description": i.description,
                "severity": getattr(i, "severity", "medium"),
                "frequency": getattr(i, "frequency", 1),
                "trend_direction": getattr(i, "trend_direction", None),
                "affected_areas": getattr(i, "affected_areas", []),
                "supporting_evidence": getattr(i, "supporting_evidence", [])
            }
            for idx, i in enumerate(insights)
        ]
        
        report_data["recommendations"] = [
            {
                "id": f"recommendation_{idx}",
                "title": r.title,
                "description": r.description,
                "priority": r.priority,
                "category": r.category,
                "effort": r.implementation_effort,
                "expected_impact": r.expected_impact,
                "timeline": r.timeline,
                "resources": r.resources_required,
                "success_metrics": r.success_metrics,
                "related_insights": r.related_insights
            }
            for idx, r in enumerate(recommendations)
        ]
        
        return report_data
    
    def _generate_summary(
        self,
        sentiment_results: List[SentimentAnalysis],
        categorization_results: List[CategoryResult],
        insights: List[InsightData],
        recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the report"""
        # Sentiment distribution and average confidence
        sentiment_counts = {}
        total_sentiment_confidence = 0.0
        valid_sentiment_count = 0
        
        for sent in sentiment_results:
            sentiment = sent.overall_sentiment
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            if hasattr(sent, 'confidence') and sent.confidence is not None:
                total_sentiment_confidence += sent.confidence
                valid_sentiment_count += 1
        
        avg_sentiment_confidence = (
            total_sentiment_confidence / valid_sentiment_count 
            if valid_sentiment_count > 0 else None
        )
        
        # Category distribution and average primary category probability
        category_counts = {}
        total_primary_prob = 0.0
        valid_primary_count = 0
        
        for cat_result in categorization_results:
            primary_category = cat_result.primary_category
            category_counts[primary_category] = category_counts.get(primary_category, 0) + 1
            
            # Calculate average probability for primary category
            if hasattr(cat_result, 'category_confidence') and cat_result.category_confidence:
                primary_key = (
                    primary_category.value 
                    if hasattr(primary_category, 'value') 
                    else str(primary_category)
                )
                if primary_key in cat_result.category_confidence:
                    prob = cat_result.category_confidence[primary_key]
                    if isinstance(prob, (int, float)) and 0 <= prob <= 1:
                        total_primary_prob += prob
                        valid_primary_count += 1
        
        avg_primary_prob = (
            total_primary_prob / valid_primary_count 
            if valid_primary_count > 0 else None
        )
        
        # Insight severity distribution
        severity_counts = {}
        for insight in insights:
            severity = getattr(insight, "severity", "medium").lower()
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Recommendation priority distribution
        priority_counts = {}
        for rec in recommendations:
            priority = rec.priority.lower()
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Calculate cleaned percentage
        total_documents = len(sentiment_results)
        cleaned_percentage = (
            (len(sentiment_results) / total_documents) * 100 
            if total_documents > 0 else 100.0
        )
        
        return {
            "sentiment_distribution": sentiment_counts,
            "category_distribution": category_counts,
            "insight_severity": severity_counts,
            "recommendation_priority": priority_counts,
            "total_documents": total_documents,
            "total_insights": len(insights),
            "total_recommendations": len(recommendations),
            "cleaned_percentage": cleaned_percentage,
            "avg_sentiment_confidence": avg_sentiment_confidence,
            "avg_primary_category_probability": avg_primary_prob
        }
    
    async def _generate_html_report(
        self, 
        report_data: Dict[str, Any],
        task_id: str
    ) -> Dict[str, str]:
        """Generate an HTML report with visualizations"""
        try:
            # For now, we'll just create a simple HTML report
            # In a real implementation, this would use a template engine like Jinja2
            # and include visualizations using libraries like Plotly or Chart.js
            
            # Generate insights and recommendations HTML
            insights_html = self._generate_insights_html(report_data["insights"])
            recommendations_html = self._generate_recommendations_html(report_data["recommendations"])
            
            # Format metrics with proper rounding and percentage signs
            cleaned_pct = f"{report_data['summary'].get('cleaned_percentage', 0):.1f}%" if report_data['summary'].get('cleaned_percentage') is not None else 'N/A'
            sent_conf = f"{report_data['summary'].get('avg_sentiment_confidence', 0) * 100 if report_data['summary'].get('avg_sentiment_confidence') is not None else 0:.1f}%" if report_data['summary'].get('avg_sentiment_confidence') is not None else 'N/A'
            cat_prob = f"{report_data['summary'].get('avg_primary_category_probability', 0) * 100 if report_data['summary'].get('avg_primary_category_probability') is not None else 0:.1f}%" if report_data['summary'].get('avg_primary_category_probability') is not None else 'N/A'
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Feedback Analysis Report - {report_data['report_id']}</title>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        line-height: 1.6; 
                        margin: 0; 
                        padding: 20px;
                        color: #333;
                    }}
                    .header {{ 
                        text-align: center; 
                        margin-bottom: 30px;
                        padding: 20px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }}
                    .section {{ 
                        margin-bottom: 30px;
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    }}
                    .section h2 {{ 
                        border-bottom: 2px solid #eee; 
                        padding-bottom: 10px;
                        color: #444;
                        margin-top: 0;
                    }}
                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                        gap: 20px;
                        margin: 20px 0;
                    }}
                    .metric-card {{ 
                        background: #f8f9fa;
                        border-left: 4px solid #4CAF50;
                        padding: 20px;
                        margin: 0;
                        border-radius: 6px;
                        transition: transform 0.2s, box-shadow 0.2s;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    }}
                    .metric-card:hover {{
                        transform: translateY(-3px);
                        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                    }}
                    .metric-card h3 {{
                        margin: 0 0 10px 0;
                        font-size: 0.95em;
                        color: #666;
                        font-weight: 600;
                    }}
                    .metric-card .value {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #2c3e50;
                        margin: 5px 0;
                    }}
                    .metric-card .subtext {{
                        font-size: 0.8em;
                        color: #7f8c8d;
                        margin: 0;
                    }}
                    .insight, .recommendation {{ 
                        background: #f8f9fa; 
                        border-left: 4px solid #2196F3; 
                        padding: 15px 20px; 
                        margin: 15px 0;
                        border-radius: 4px;
                        transition: transform 0.2s, box-shadow 0.2s;
                    }}
                    .insight:hover, .recommendation:hover {{
                        transform: translateX(5px);
                        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
                    }}
                    .priority-high {{ border-left-color: #e74c3c; }}
                    .priority-medium {{ border-left-color: #f39c12; }}
                    .priority-low {{ border-left-color: #2ecc71; }}
                    .quality-metrics {{
                        margin-top: 20px;
                        padding: 15px;
                        background: #f0f7ff;
                        border-radius: 6px;
                        border-left: 4px solid #3498db;
                    }}
                    .quality-metrics h3 {{
                        margin-top: 0;
                        color: #2980b9;
                    }}
                    .quality-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 15px;
                        margin-top: 10px;
                    }}
                    .quality-metric {{
                        background: white;
                        padding: 12px;
                        border-radius: 4px;
                        text-align: center;
                        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                    }}
                    .quality-metric .value {{
                        font-size: 1.5em;
                        font-weight: bold;
                        color: #2c3e50;
                    }}
                    .quality-metric .label {{
                        font-size: 0.8em;
                        color: #7f8c8d;
                        margin-top: 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1 style="margin: 0 0 10px 0;">Feedback Analysis Report</h1>
                    <p style="margin: 5px 0; opacity: 0.9;">Generated on: {report_data['generated_at']}</p>
                    <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.8;">Report ID: {task_id}</p>
                </div>
                
                <div class="section">
                    <h2>Summary</h2>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <h3>Documents Processed</h3>
                            <div class="value">{report_data['document_count']}</div>
                            <p class="subtext">Total feedback documents analyzed</p>
                        </div>
                        <div class="metric-card">
                            <h3>Key Insights</h3>
                            <div class="value">{report_data['insight_count']}</div>
                            <p class="subtext">Important patterns identified</p>
                        </div>
                        <div class="metric-card">
                            <h3>Recommendations</h3>
                            <div class="value">{report_data['recommendation_count']}</div>
                            <p class="subtext">Actionable suggestions</p>
                        </div>
                    </div>
                    
                    <div class="quality-metrics">
                        <h3>Data Quality & Confidence</h3>
                        <div class="quality-grid">
                            <div class="quality-metric">
                                <div class="value">{cleaned_pct}</div>
                                <div class="label">Documents Cleaned</div>
                            </div>
                            <div class="quality-metric">
                                <div class="value">{sent_conf}</div>
                                <div class="label">Avg. Sentiment Confidence</div>
                            </div>
                            <div class="quality-metric">
                                <div class="value">{cat_prob}</div>
                                <div class="label">Avg. Category Confidence</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Key Insights</h2>
                    {insights_html}
                </div>
                
                <div class="section">
                    <h2>Recommendations</h2>
                    {recommendations_html}
                </div>
            </body>
            </html>
            """
            
            # Save the HTML file
            report_path = self.output_dir / f"{task_id}_report.html"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML report generated: {report_path}")
            return {"path": str(report_path), "format": "html"}
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    def _generate_insights_html(self, insights: List[Dict[str, Any]]) -> str:
        """Generate HTML for insights section"""
        if not insights:
            return "<p>No insights generated.</p>"
            
        html_parts = []
        for insight in insights:
            html_parts.append(f"""
                <div class="insight">
                    <h3>{insight['type']}</h3>
                    <p><strong>Severity:</strong> {insight['severity'].title()}</p>
                    <p>{insight['description']}</p>
                    {f"<p><strong>Affected Areas:</strong> {', '.join(insight['affected_areas'])}</p>" if insight.get('affected_areas') else ""}
                </div>
            """)
            
        return "\n".join(html_parts)
    
    def _generate_recommendations_html(self, recommendations: List[Dict[str, Any]]) -> str:
        """Generate HTML for recommendations section"""
        if not recommendations:
            return "<p>No recommendations generated.</p>"
            
        html_parts = []
        for rec in recommendations:
            priority_class = f"priority-{rec['priority'].lower()}" if 'priority' in rec else ""
            html_parts.append(f"""
                <div class="recommendation {priority_class}">
                    <h3>{rec['title']}</h3>
                    <p>{rec['description']}</p>
                    <div style="display: flex; gap: 20px; margin-top: 10px;">
                        {f"<div><strong>Priority:</strong> {rec['priority'].title()}</div>" if 'priority' in rec else ""}
                        {f"<div><strong>Effort:</strong> {rec['effort'].title()}</div>" if 'effort' in rec else ""}
                        {f"<div><strong>Timeline:</strong> {rec['timeline']}</div>" if 'timeline' in rec else ""}
                    </div>
                </div>
            """)
            
        return "\n".join(html_parts)
    
    async def _generate_json_report(
        self, 
        report_data: Dict[str, Any],
        task_id: str
    ) -> Dict[str, str]:
        """Generate a JSON report"""
        try:
            report_path = self.output_dir / f"{task_id}_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            logger.info(f"JSON report generated: {report_path}")
            return {"path": str(report_path), "format": "json"}
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}", exc_info=True)
            return {"status": "error", "message": str(e)}
    
    async def shutdown(self):
        """Clean up resources"""
        self.status = "shutdown"
        logger.info(f"{self.agent_id} shutdown complete")
