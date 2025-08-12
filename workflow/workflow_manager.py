"""
Workflow Manager - Coordinates the feedback processing pipeline
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from models.feedback_models import (
    FeedbackDocument, CleanedDocument, SentimentAnalysis, 
    CategoryResult, InsightData, Recommendation, ProcessingStatus
)
from agents.data_collection import DataCollectionAgent
from agents.data_cleaning import DataCleaningAgent
from agents.sentiment_analysis import SentimentAnalysisAgent
from agents.categorization import CategorizationAgent
from agents.insight_generation import InsightGenerationAgent
from agents.recommendation import RecommendationAgent
from agents.report_generation import ReportGenerationAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)

class WorkflowManager:
    """
    Manages the end-to-end feedback processing workflow by coordinating
    between different specialized agents.
    """
    
    def __init__(self):
        self.agent_id = "workflow_manager"
        self.status = "idle"
        self.current_task_id = None
        self.start_time = None
        self.end_time = None
        self.processing_stats = {
            'documents_processed': 0,
            'errors_encountered': 0,
            'processing_time_seconds': 0,
            'agent_stats': {}
        }
        
        # Initialize all agents
        self.data_collection_agent = DataCollectionAgent()
        self.data_cleaning_agent = DataCleaningAgent()
        self.sentiment_analysis_agent = SentimentAnalysisAgent()
        self.categorization_agent = CategorizationAgent()
        self.insight_generation_agent = InsightGenerationAgent()
        self.recommendation_agent = RecommendationAgent()
        self.report_generation_agent = ReportGenerationAgent()
        
        # Store intermediate results
        self.cleaned_documents = []
        self.sentiment_results = []
        self.categorization_results = []
        self.insights = []
        self.recommendations = []
        self.report = None
        
    async def initialize(self):
        """Initialize all agents and resources"""
        logger.info("Initializing Workflow Manager and all agents")
        self.status = "initializing"
        
        try:
            # Initialize all agents in parallel
            await asyncio.gather(
                self.data_collection_agent.initialize(),
                self.data_cleaning_agent.initialize(),
                self.sentiment_analysis_agent.initialize(),
                self.categorization_agent.initialize(),
                self.insight_generation_agent.initialize(),
                self.recommendation_agent.initialize(),
                self.report_generation_agent.initialize()
            )
            
            self.status = "ready"
            logger.info("Workflow Manager and all agents initialized successfully")
            return {"status": "success", "message": "Workflow Manager initialized"}
            
        except Exception as e:
            self.status = "error"
            logger.error(f"Error initializing Workflow Manager: {str(e)}")
            return {"status": "error", "message": f"Initialization failed: {str(e)}"}
    
    async def process_feedback(
        self, 
        input_data: Union[Dict[str, Any], List[Dict[str, Any]]],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process feedback through the entire pipeline
        
        Args:
            input_data: Raw feedback data or list of feedback items
            task_id: Optional task ID for tracking
            
        Returns:
            Dict containing processing results and status
        """
        self.current_task_id = task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.status = "processing"
        self.processing_stats = {
            'documents_processed': 0,
            'errors_encountered': 0,
            'processing_time_seconds': 0,
            'agent_stats': {}
        }
        
        logger.info(f"Starting feedback processing for task {self.current_task_id}")
        
        try:
            # 1. Data Collection
            collection_result = await self._run_data_collection(input_data)
            if not collection_result.get('success', False):
                raise Exception(f"Data collection failed: {collection_result.get('message')}")
            
            # 2. Data Cleaning
            cleaning_result = await self._run_data_cleaning(collection_result['documents'])
            if not cleaning_result.get('success', False):
                raise Exception(f"Data cleaning failed: {cleaning_result.get('message')}")
            
            # 3. Sentiment Analysis
            sentiment_result = await self._run_sentiment_analysis(cleaning_result['cleaned_documents'])
            if not sentiment_result.get('success', False):
                raise Exception(f"Sentiment analysis failed: {sentiment_result.get('message')}")
            
            # 4. Categorization
            categorization_result = await self._run_categorization(
                cleaning_result['cleaned_documents'], 
                sentiment_result['sentiment_results']
            )
            if not categorization_result.get('success', False):
                raise Exception(f"Categorization failed: {categorization_result.get('message')}")
            
            # 5. Insight Generation
            insight_result = await self._run_insight_generation(
                cleaning_result['cleaned_documents'],
                sentiment_result['sentiment_results'],
                categorization_result['categorization_results']
            )
            if not insight_result.get('success', False):
                raise Exception(f"Insight generation failed: {insight_result.get('message')}")
            
            # 6. Recommendation Generation
            recommendation_result = await self._run_recommendation_generation(
                insight_result['insights']
            )
            if not recommendation_result.get('success', False):
                raise Exception(f"Recommendation generation failed: {recommendation_result.get('message')}")
            
            # 7. Generate Final Report
            report = await self._generate_final_report(
                cleaning_result['cleaned_documents'],
                sentiment_result['sentiment_results'],
                categorization_result['categorization_results'],
                insight_result['insights'],
                recommendation_result['recommendations']
            )
            
            # Update status and stats
            self.status = "completed"
            self.end_time = datetime.now()
            self.processing_stats['processing_time_seconds'] = (
                self.end_time - self.start_time
            ).total_seconds()
            
            logger.info(f"Successfully completed processing for task {self.current_task_id}")
            
            return {
                "status": "success",
                "task_id": self.current_task_id,
                "report": report,
                "processing_stats": self.processing_stats
            }
            
        except Exception as e:
            self.status = "error"
            self.processing_stats['errors_encountered'] += 1
            logger.error(f"Error processing feedback: {str(e)}", exc_info=True)
            
            return {
                "status": "error",
                "task_id": self.current_task_id,
                "message": str(e),
                "processing_stats": self.processing_stats
            }
    
    async def _run_data_collection(
        self, 
        input_data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Run the data collection phase"""
        logger.info("Starting data collection phase")
        
        try:
            from models.feedback_models import FeedbackDocument
            
            # Convert single document to list if needed
            if isinstance(input_data, dict):
                input_data = [input_data]
            
            # Convert input dictionaries to FeedbackDocument instances
            feedback_docs = []
            for doc_data in input_data:
                # Ensure required fields have default values if not provided
                if not isinstance(doc_data, dict):
                    doc_data = {"content": str(doc_data)}
                
                doc_data.setdefault("filename", f"document_{len(feedback_docs) + 1}.txt")
                doc_data.setdefault("content_type", "text/plain")
                doc_data.setdefault("source", "api")
                
                try:
                    feedback_doc = FeedbackDocument(**doc_data)
                    feedback_docs.append(feedback_doc)
                except Exception as e:
                    logger.error(f"Error creating FeedbackDocument: {str(e)}")
                    continue
            
            if not feedback_docs:
                raise ValueError("No valid documents to process")
            
            # Process documents through the data collection agent
            result = await self.data_collection_agent.validate_and_enrich({"documents": feedback_docs})
            
            if not result:
                raise ValueError("No documents were processed during data collection")
                
            self.processing_stats['documents_processed'] = len(result)
            self.processing_stats['agent_stats']['data_collection'] = {
                'documents_processed': len(result),
                'status': 'completed'
            }
            
            logger.info(f"Completed data collection: {len(result)} documents processed")
            
            return {
                "success": True,
                "documents": result,
                "message": f"Processed {len(result)} documents"
            }
            
        except Exception as e:
            logger.error(f"Error in data collection: {str(e)}", exc_info=True)
            self.processing_stats['errors_encountered'] += 1
            return {"success": False, "message": str(e)}
    
    async def _run_data_cleaning(
        self, 
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run the data cleaning phase"""
        logger.info("Starting data cleaning phase")
        
        try:
            # Process all documents in a batch
            result = await self.data_cleaning_agent.clean_documents({"documents": documents})
            
            if not result:
                raise ValueError("No documents were processed during data cleaning")
                
            self.cleaned_documents = result
            
            self.processing_stats['agent_stats']['data_cleaning'] = {
                'documents_cleaned': len(result),
                'status': 'completed'
            }
            
            logger.info(f"Completed data cleaning: {len(result)} documents cleaned")
            
            return {
                "success": True,
                "cleaned_documents": result,
                "message": f"Cleaned {len(result)} documents"
            }
            
        except Exception as e:
            logger.error(f"Error in data cleaning: {str(e)}", exc_info=True)
            self.processing_stats['errors_encountered'] += 1
            return {"success": False, "message": str(e)}
    
    async def _run_sentiment_analysis(
        self, 
        cleaned_documents: List[CleanedDocument]
    ) -> Dict[str, Any]:
        """Run the sentiment analysis phase"""
        logger.info("Starting sentiment analysis phase")
        
        try:
            if not cleaned_documents:
                raise ValueError("No documents provided for sentiment analysis")
                
            # Process all documents in a batch
            sentiment_results = await self.sentiment_analysis_agent.analyze_sentiment({
                'documents': cleaned_documents
            })
            
            if not sentiment_results or not isinstance(sentiment_results, list):
                logger.error(f"Unexpected sentiment results format: {type(sentiment_results)}")
                raise ValueError("Invalid sentiment analysis results returned")
                
            self.sentiment_results = sentiment_results
            
            self.processing_stats['agent_stats']['sentiment_analysis'] = {
                'documents_analyzed': len(self.sentiment_results),
                'status': 'completed',
                'success': bool(self.sentiment_results)
            }
            
            logger.info(f"Completed sentiment analysis: {len(self.sentiment_results)} documents analyzed")
            
            return {
                "success": True,
                "sentiment_results": self.sentiment_results,
                "message": f"Analyzed sentiment for {len(self.sentiment_results)} documents"
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}", exc_info=True)
            self.processing_stats['errors_encountered'] += 1
            return {"success": False, "message": str(e)}
    
    async def _run_categorization(
        self, 
        cleaned_documents: List[CleanedDocument],
        sentiment_results: List[SentimentAnalysis]
    ) -> Dict[str, Any]:
        """Run the categorization phase"""
        logger.info("Starting categorization phase")
        
        try:
            if not cleaned_documents:
                raise ValueError("No documents provided for categorization")
                
            # Prepare input data for categorization
            input_data = {
                'documents': cleaned_documents,
                'sentiment_results': sentiment_results
            }
            
            # Categorize all documents in a batch
            categorization_results = await self.categorization_agent.categorize_feedback(input_data)
            
            if not categorization_results or not isinstance(categorization_results, list):
                logger.error(f"Unexpected categorization results format: {type(categorization_results)}")
                raise ValueError("Invalid categorization results returned")
                
            self.categorization_results = categorization_results
            
            self.processing_stats['agent_stats']['categorization'] = {
                'documents_categorized': len(self.categorization_results),
                'status': 'completed',
                'success': bool(self.categorization_results)
            }
            
            logger.info(f"Completed categorization: {len(self.categorization_results)} documents categorized")
            
            return {
                "success": True,
                "categorization_results": self.categorization_results,
                "message": f"Categorized {len(self.categorization_results)} documents"
            }
            
        except Exception as e:
            logger.error(f"Error in categorization: {str(e)}", exc_info=True)
            self.processing_stats['errors_encountered'] += 1
            return {"success": False, "message": str(e)}
    
    async def _run_insight_generation(
        self,
        cleaned_documents: List[CleanedDocument],
        sentiment_results: List[SentimentAnalysis],
        categorization_results: List[CategoryResult]
    ) -> Dict[str, Any]:
        """Run the insight generation phase"""
        logger.info("Starting insight generation phase")
        
        try:
            if not cleaned_documents or not sentiment_results or not categorization_results:
                raise ValueError("Incomplete data provided for insight generation")
                
            # Prepare input data for insight generation
            input_data = {
                'documents': cleaned_documents,
                'sentiment_results': sentiment_results,
                'categorization_results': categorization_results
            }
            
            # Generate insights
            insights = await self.insight_generation_agent.generate_insights(input_data)
            
            if not isinstance(insights, list):
                logger.error(f"Unexpected insights format: {type(insights)}")
                raise ValueError("Invalid insights data returned")
                
            self.insights = insights
            self.processing_stats['agent_stats']['insight_generation'] = {
                'insights_generated': len(insights),
                'status': 'completed',
                'success': bool(insights)
            }
            
            logger.info(f"Generated {len(insights)} insights")
            
            return {
                "success": True,
                "insights": insights,
                "message": f"Generated {len(insights)} insights"
            }
            
        except Exception as e:
            logger.error(f"Error in insight generation: {str(e)}", exc_info=True)
            self.processing_stats['errors_encountered'] += 1
            return {"success": False, "message": str(e)}
    
    async def _run_recommendation_generation(
        self,
        insights: List[InsightData]
    ) -> Dict[str, Any]:
        """Run the recommendation generation phase"""
        logger.info("Starting recommendation generation phase")
        
        try:
            # Prepare input data for recommendation generation
            input_data = {
                'insights': insights
            }
            
            # Generate recommendations
            recommendations = await self.recommendation_agent.generate_recommendations(input_data)
            
            if not isinstance(recommendations, list):
                logger.error(f"Unexpected recommendations format: {type(recommendations)}")
                recommendations = []
            
            self.recommendations = recommendations
            self.processing_stats['agent_stats']['recommendation_generation'] = {
                'recommendations_generated': len(recommendations),
                'status': 'completed',
                'success': bool(recommendations)
            }
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            
            return {
                "success": bool(recommendations),
                "recommendations": recommendations,
                "message": f"Generated {len(recommendations)} recommendations"
            }
            
        except Exception as e:
            logger.error(f"Error in recommendation generation: {str(e)}", exc_info=True)
            self.processing_stats['errors_encountered'] += 1
            return {"success": False, "message": str(e)}
    
    async def _generate_final_report(
        self,
        cleaned_documents: List[CleanedDocument],
        sentiment_results: List[SentimentAnalysis],
        categorization_results: List[CategoryResult],
        insights: List[InsightData],
        recommendations: List[Recommendation]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive report of the analysis using the ReportGenerationAgent.
        
        Args:
            cleaned_documents: List of cleaned feedback documents
            sentiment_results: List of sentiment analysis results
            categorization_results: List of categorization results
            insights: List of generated insights
            recommendations: List of generated recommendations
            
        Returns:
            Dictionary containing the generated report data and file paths
        """
        logger.info("Generating final report using ReportGenerationAgent")
        
        try:
            # Generate the report using the ReportGenerationAgent
            report_result = await self.report_generation_agent.generate_report(
                cleaned_documents=cleaned_documents,
                sentiment_results=sentiment_results,
                categorization_results=categorization_results,
                insights=insights,
                recommendations=recommendations,
                task_id=self.current_task_id,
                output_format="all"  # Generates both HTML and JSON reports
            )
            
            if report_result["status"] != "success":
                logger.error(f"Failed to generate report: {report_result.get('message', 'Unknown error')}")
                return {
                    "status": "error",
                    "message": "Failed to generate report",
                    "details": report_result.get("message", "Unknown error")
                }
            
            # Store the report data and paths
            self.report = {
                "report_id": self.current_task_id,
                "generated_at": datetime.now().isoformat(),
                "files": report_result.get("generated_files", {}),
                "summary": {
                    "documents_processed": len(cleaned_documents),
                    "sentiment_summary": {
                        "positive": len([r for r in sentiment_results if r.overall_sentiment == "positive"]),
                        "neutral": len([r for r in sentiment_results if r.overall_sentiment == "neutral"]),
                        "negative": len([r for r in sentiment_results if r.overall_sentiment == "negative"])
                    },
                    "categories_identified": len(set(c.primary_category for c in categorization_results)),
                    "insights_generated": len(insights),
                    "recommendations_provided": len(recommendations),
                    "errors_encountered": self.processing_stats.get('errors_encountered', 0)
                },
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("Final report generated successfully")
            return self.report
            
        except Exception as e:
            logger.error(f"Error generating final report: {str(e)}", exc_info=True)
            return {
                "error": f"Failed to generate final report: {str(e)}",
                "processing_stats": self.processing_stats
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the workflow manager"""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "current_task_id": self.current_task_id,
            "processing_stats": self.processing_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the workflow manager and all agents"""
        logger.info("Shutting down Workflow Manager and all agents")
        self.status = "shutting_down"
        
        # Shutdown all agents
        await asyncio.gather(
            self.data_collection_agent.shutdown(),
            self.data_cleaning_agent.shutdown(),
            self.sentiment_analysis_agent.shutdown(),
            self.categorization_agent.shutdown(),
            self.insight_generation_agent.shutdown(),
            self.recommendation_agent.shutdown(),
            self.report_generation_agent.shutdown(),
            return_exceptions=True  # Don't let one agent's failure prevent others from shutting down
        )
        
        self.status = "shutdown"
        logger.info("Workflow Manager and all agents have been shut down successfully")
