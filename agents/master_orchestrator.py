"""
Master Orchestrator Agent - Coordinates the entire feedback processing pipeline
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4

from models.feedback_models import (
    FeedbackDocument, ProcessingResult, AgentTask, ProcessingStatus,
    SentimentAnalysis, CategoryResult, InsightData, Recommendation
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class MasterOrchestratorAgent:
    """
    Master Orchestrator Agent that coordinates the entire feedback processing pipeline.
    Manages task delegation, workflow orchestration, and result aggregation.
    """
    
    def __init__(self):
        self.agent_id = "master_orchestrator"
        self.agents: Dict[str, Any] = {}
        self.active_tasks: Dict[str, AgentTask] = {}
        self.processing_queue = asyncio.Queue()
        
    async def initialize(self, agents: Dict[str, Any]):
        """Initialize the orchestrator with specialized agents and knowledge graph"""
        self.agents = agents
        
        # Initialize all agents
        for agent_name, agent in self.agents.items():
            await agent.initialize()
            logger.info(f"Initialized agent: {agent_name}")
        
        logger.info("Master Orchestrator initialized successfully")
    
    async def process_feedback_pipeline(self, documents: List[FeedbackDocument]) -> ProcessingResult:
        """
        Main pipeline for processing feedback documents through all agents
        """
        start_time = datetime.now()
        batch_id = f"batch_{uuid4().hex[:8]}"
        
        logger.info(f"Starting feedback processing pipeline for batch {batch_id}")
        logger.info(f"Processing {len(documents)} documents")
        
        try:
            # Initialize processing result
            result = ProcessingResult(
                batch_id=batch_id,
                total_documents=len(documents),
                processed_documents=0
            )
            
            # Step 1: Data Collection (already have documents, but validate and enrich)
            logger.info("Step 1: Data Collection and Validation")
            validated_documents = await self._execute_agent_task(
                'data_collection', 'validate_and_enrich', {'documents': documents}
            )
            
            # Step 2: Data Cleaning
            logger.info("Step 2: Data Cleaning and Preprocessing")
            cleaned_documents = await self._execute_agent_task(
                'data_cleaning', 'clean_documents', {'documents': validated_documents}
            )
            
            # Step 3: Sentiment Analysis
            logger.info("Step 3: Sentiment Analysis")
            sentiment_results = await self._execute_agent_task(
                'sentiment_analysis', 'analyze_sentiment', {'documents': cleaned_documents}
            )
            result.sentiment_results = sentiment_results
            
            # Step 4: Categorization
            logger.info("Step 4: Feedback Categorization")
            categorization_results = await self._execute_agent_task(
                'categorization', 'categorize_feedback', {'documents': cleaned_documents}
            )
            result.categorization_results = categorization_results
            
            # Step 5: Insight Generation
            logger.info("Step 5: Insight Generation")
            insights = await self._execute_agent_task(
                'insight_generation', 'generate_insights', {
                    'documents': cleaned_documents,
                    'sentiment_results': sentiment_results,
                    'categorization_results': categorization_results
                }
            )
            result.insights = insights
            
            # Step 6: Recommendation Generation
            logger.info("Step 6: Recommendation Generation")
            recommendations = await self._execute_agent_task(
                'recommendation', 'generate_recommendations', {
                    'insights': insights,
                    'sentiment_results': sentiment_results,
                    'categorization_results': categorization_results
                }
            )
            result.recommendations = recommendations
            
            # Step 7: Report Generation
            logger.info("Step 7: Final Report Generation")
            final_report = await self._execute_agent_task(
                'report_generation', 'generate_report', {
                    'batch_id': batch_id,
                    'documents': cleaned_documents,
                    'sentiment_results': sentiment_results,
                    'categorization_results': categorization_results,
                    'insights': insights,
                    'recommendations': recommendations
                }
            )
            
            # Calculate summary statistics
            result.processed_documents = len(documents)
            result.sentiment_distribution = self._calculate_sentiment_distribution(sentiment_results)
            result.category_distribution = self._calculate_category_distribution(categorization_results)
            result.processing_time_seconds = (datetime.now() - start_time).total_seconds()
            result.average_confidence = self._calculate_average_confidence(sentiment_results, categorization_results)
            result.data_quality_score = self._calculate_data_quality_score(cleaned_documents)
            
            
            logger.info(f"Pipeline completed successfully for batch {batch_id}")
            logger.info(f"Processing time: {result.processing_time_seconds:.2f} seconds")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline processing failed for batch {batch_id}: {str(e)}")
            raise
    
    async def _execute_agent_task(self, agent_name: str, task_type: str, input_data: Dict[str, Any]) -> Any:
        """Execute a task on a specific agent"""
        if agent_name not in self.agents:
            raise ValueError(f"Agent {agent_name} not found")
        
        task_id = f"{agent_name}_{uuid4().hex[:8]}"
        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            input_data=input_data,
            status=ProcessingStatus.PROCESSING,
            started_at=datetime.now()
        )
        
        self.active_tasks[task_id] = task
        
        try:
            agent = self.agents[agent_name]
            
            # Execute the task based on task type
            if hasattr(agent, task_type):
                result = await getattr(agent, task_type)(input_data)
            else:
                raise ValueError(f"Task type {task_type} not supported by agent {agent_name}")
            
            task.status = ProcessingStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            
            logger.debug(f"Task {task_id} completed successfully")
            return result
            
        except Exception as e:
            task.status = ProcessingStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            logger.error(f"Task {task_id} failed: {str(e)}")
            raise
    
    def _calculate_sentiment_distribution(self, sentiment_results: List[SentimentAnalysis]) -> Dict[str, int]:
        """Calculate distribution of sentiments"""
        distribution = {}
        for result in sentiment_results:
            sentiment = result.overall_sentiment.value
            distribution[sentiment] = distribution.get(sentiment, 0) + 1
        return distribution
    
    def _calculate_category_distribution(self, categorization_results: List[CategoryResult]) -> Dict[str, int]:
        """Calculate distribution of categories"""
        distribution = {}
        for result in categorization_results:
            category = result.primary_category.value
            distribution[category] = distribution.get(category, 0) + 1
        return distribution
    
    def _calculate_average_confidence(self, sentiment_results: List[SentimentAnalysis], 
                                    categorization_results: List[CategoryResult]) -> float:
        """Calculate average confidence across all results"""
        total_confidence = 0
        total_count = 0
        
        for result in sentiment_results:
            total_confidence += result.confidence
            total_count += 1
        
        for result in categorization_results:
            if result.category_confidence:
                total_confidence += max(result.category_confidence.values())
                total_count += 1
        
        return total_confidence / total_count if total_count > 0 else 0.0
    
    def _calculate_data_quality_score(self, cleaned_documents: List[Any]) -> float:
        """Calculate overall data quality score"""
        if not cleaned_documents:
            return 0.0
        
        total_score = 0
        for doc in cleaned_documents:
            if hasattr(doc, 'quality_score'):
                total_score += doc.quality_score
            else:
                total_score += 0.8  # Default quality score
        
        return total_score / len(cleaned_documents)
    
    async def _update_knowledge_graph(self, result: ProcessingResult):
        """Update knowledge graph with processing results"""
        if not self.knowledge_graph:
            return
        
        try:
            # Add insights as nodes
            for insight in result.insights:
                await self.knowledge_graph.add_insight_node(insight)
            
            # Add recommendations as nodes
            for recommendation in result.recommendations:
                await self.knowledge_graph.add_recommendation_node(recommendation)
            
            # Create relationships between insights and recommendations
            await self.knowledge_graph.create_insight_recommendation_relationships(
                result.insights, result.recommendations
            )
            
            logger.debug("Knowledge graph updated successfully")
            
        except Exception as e:
            logger.warning(f"Failed to update knowledge graph: {str(e)}")
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            'orchestrator_id': self.agent_id,
            'active_tasks': len(self.active_tasks),
            'agents': {}
        }
        
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'get_status'):
                status['agents'][agent_name] = agent.get_status()
            else:
                status['agents'][agent_name] = {'status': 'active'}
        
        return status
    
    async def shutdown(self):
        """Shutdown the orchestrator and all agents"""
        logger.info("Shutting down Master Orchestrator...")
        
        # Shutdown all agents
        for agent_name, agent in self.agents.items():
            if hasattr(agent, 'shutdown'):
                await agent.shutdown()
                logger.info(f"Agent {agent_name} shutdown completed")
        
        logger.info("Master Orchestrator shutdown completed")
