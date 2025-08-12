"""
Test script for verifying the ReportGenerationAgent functionality
"""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4

# Add the project root to the Python path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.feedback_models import (
    CleanedDocument, SentimentAnalysis, CategoryResult,
    InsightData, Recommendation, SentimentType, FeedbackCategory
)
from agents.report_generation import ReportGenerationAgent

# Create output directory for test reports
TEST_OUTPUT_DIR = Path(__file__).parent.parent / "output" / "test_reports"
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def generate_test_data():
    """Generate test data for report generation"""
    # Generate sample cleaned documents
    cleaned_docs = [
        CleanedDocument(
            original_id=f"doc_{i}",
            cleaned_content=f"This is a sample cleaned document {i} with some content about technical issues.",
            language="en",
            word_count=150 + i * 10,
            quality_score=0.8 + (i * 0.01)
        )
        for i in range(1, 6)
    ]
    
    # Generate sample sentiment analysis results
    sentiment_results = [
        SentimentAnalysis(
            document_id=f"doc_{i}",
            overall_sentiment=SentimentType.POSITIVE if i % 3 == 0 else 
                            (SentimentType.NEGATIVE if i % 3 == 1 else SentimentType.NEUTRAL),
            sentiment_score=0.7 if i % 3 == 0 else (-0.5 if i % 3 == 1 else 0.1),
            confidence=0.85 + (i * 0.01),
            key_phrases=["technical issue", "performance", f"example {i}"],
            emotional_indicators=["frustrated" if i % 3 == 1 else "satisfied" if i % 3 == 0 else "neutral"]
        )
        for i in range(1, 6)
    ]
    
    # Generate sample categorization results
    categories = list(FeedbackCategory)
    categorization_results = [
        CategoryResult(
            document_id=f"doc_{i}",
            primary_category=categories[i % len(categories)],
            secondary_categories=[c for j, c in enumerate(categories) if j % 2 == 0 and j != i % len(categories)][:2],
            category_confidence={
                categories[j % len(categories)].value: 0.7 + (j * 0.05) 
                for j in range(3)
            },
            keywords=["technical", "issue", f"example{i}"],
            topics=["performance", "reliability"]
        )
        for i in range(1, 6)
    ]
    
    # Generate sample insights
    insights = [
        InsightData(
            insight_type="performance_issue",
            description=f"Document {i} shows potential performance issues that need attention.",
            supporting_evidence=[f"Evidence {j} for insight {i}" for j in range(1, 3)],
            severity="high" if i % 2 == 0 else "medium",
            affected_areas=["API response time", "Database queries"]
        )
        for i in range(1, 4)
    ]
    
    # Generate sample recommendations
    recommendations = [
        Recommendation(
            title=f"Recommendation {i} for improvement",
            description=f"Detailed description of recommendation {i} with implementation steps.",
            priority="high" if i % 3 == 0 else ("medium" if i % 3 == 1 else "low"),
            category="performance",
            implementation_effort="medium",
            expected_impact="high",
            timeline="short-term" if i % 2 == 0 else "medium-term",
            resources_required=["Development team", "QA team"],
            success_metrics=[f"Metric {i} improvement" for i in range(1, 3)],
            related_insights=[f"insight_{i}"]
        )
        for i in range(1, 4)
    ]
    
    return {
        "cleaned_documents": cleaned_docs,
        "sentiment_results": sentiment_results,
        "categorization_results": categorization_results,
        "insights": insights,
        "recommendations": recommendations
    }

async def test_report_generation():
    """Test the report generation process"""
    print("Starting report generation test...")
    
    # Initialize the report generation agent
    report_agent = ReportGenerationAgent(output_dir=str(TEST_OUTPUT_DIR))
    await report_agent.initialize()
    
    try:
        # Generate test data
        test_data = await generate_test_data()
        
        # Generate report
        task_id = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Generating report with task ID: {task_id}")
        
        report_result = await report_agent.generate_report(
            cleaned_documents=test_data["cleaned_documents"],
            sentiment_results=test_data["sentiment_results"],
            categorization_results=test_data["categorization_results"],
            insights=test_data["insights"],
            recommendations=test_data["recommendations"],
            task_id=task_id,
            output_format="all"
        )
        
        print("\nReport Generation Results:")
        print(f"Status: {report_result.get('status', 'unknown')}")
        
        if report_result.get("status") == "success":
            print("\nGenerated Files:")
            for file_type, file_info in report_result.get("generated_files", {}).items():
                print(f"- {file_type.upper()}: {file_info.get('path')}")
            
            print("\nReport Summary:")
            print(f"Documents Processed: {report_result.get('summary', {}).get('documents_processed', 0)}")
            print(f"Insights Generated: {report_result.get('summary', {}).get('insights_generated', 0)}")
            print(f"Recommendations: {report_result.get('summary', {}).get('recommendations_provided', 0)}")
            
            # Print the location of the generated files
            print("\nYou can find the generated reports in:")
            print(f"- HTML Report: {TEST_OUTPUT_DIR / f'{task_id}_report.html'}")
            print(f"- JSON Report: {TEST_OUTPUT_DIR / f'{task_id}_report.json'}")
        else:
            print(f"Error: {report_result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error during report generation: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Clean up
        await report_agent.shutdown()

if __name__ == "__main__":
    asyncio.run(test_report_generation())
