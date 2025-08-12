"""
Specialist Feedback Management System - Main Application
Multi-Agent AI System for Processing and Analyzing Specialist Feedback
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import streamlit as st
from dotenv import load_dotenv
import os

from agents.master_orchestrator import MasterOrchestratorAgent
from agents.data_collection import DataCollectionAgent
from agents.data_cleaning import DataCleaningAgent
from agents.sentiment_analysis import SentimentAnalysisAgent
from agents.categorization import CategorizationAgent
from agents.insight_generation import InsightGenerationAgent
from agents.recommendation import RecommendationAgent
from agents.report_generation import ReportGenerationAgent
from models.feedback_models import FeedbackDocument, ProcessingResult
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger(__name__)

class SpecialistFeedbackSystem:
    """Main application class for the Specialist Feedback Management System"""
    
    def __init__(self):
        self.master_orchestrator = MasterOrchestratorAgent()
        self.processing_status = {}
        
    async def initialize(self):
        """Initialize the system components"""
        logger.info("Initializing Specialist Feedback Management System...")
        
        # Initialize master orchestrator with all agents
        agents = {
            'data_collection': DataCollectionAgent(),
            'data_cleaning': DataCleaningAgent(),
            'sentiment_analysis': SentimentAnalysisAgent(),
            'categorization': CategorizationAgent(),
            'insight_generation': InsightGenerationAgent(),
            'recommendation': RecommendationAgent(),
            'report_generation': ReportGenerationAgent()
        }
        
        await self.master_orchestrator.initialize(agents)
        logger.info("System initialization completed successfully")
    
    async def process_feedback_batch(self, documents: List[FeedbackDocument]) -> str:
        """Process a batch of feedback documents"""
        batch_id = f"batch_{len(self.processing_status) + 1}"
        self.processing_status[batch_id] = {
            'status': 'processing',
            'total_documents': len(documents),
            'processed_documents': 0,
            'results': None
        }
        
        try:
            logger.info(f"Starting processing of batch {batch_id} with {len(documents)} documents")
            
            # Process through master orchestrator
            results = await self.master_orchestrator.process_feedback_pipeline(documents)
            
            self.processing_status[batch_id].update({
                'status': 'completed',
                'processed_documents': len(documents),
                'results': results
            })
            
            logger.info(f"Batch {batch_id} processing completed successfully")
            return batch_id
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_id}: {str(e)}")
            self.processing_status[batch_id].update({
                'status': 'failed',
                'error': str(e)
            })
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    def get_processing_status(self, batch_id: str) -> Dict:
        """Get the processing status of a batch"""
        return self.processing_status.get(batch_id, {'status': 'not_found'})

# Initialize the system
feedback_system = SpecialistFeedbackSystem()

# FastAPI application
app = FastAPI(
    title="Specialist Feedback Management System",
    description="Agentic AI-powered system for processing specialist feedback",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    await feedback_system.initialize()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with system information"""
    return """
    <html>
        <head>
            <title>Specialist Feedback Management System</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { color: #2c3e50; }
                .feature { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1 class="header">Specialist Feedback Management System</h1>
            <p>Agentic AI-powered multi-agent system for processing specialist feedback</p>
            
            <h2>Features</h2>
            <div class="feature">📊 Automated sentiment analysis and categorization</div>
            <div class="feature">🤖 Multi-agent processing pipeline</div>
            <div class="feature">📈 Actionable insights generation</div>
            <div class="feature">📋 Comprehensive reporting</div>
            
            <h2>API Endpoints</h2>
            <ul>
                <li><a href="/docs">API Documentation (Swagger)</a></li>
                <li><a href="/health">System Health Check</a></li>
                <li>POST /upload - Upload feedback documents</li>
                <li>GET /status/{batch_id} - Check processing status</li>
                <li>GET /results/{batch_id} - Get processing results</li>
            </ul>
            
            <h2>Web Interface</h2>
            <p>Access the Streamlit dashboard: <a href="http://localhost:8501">http://localhost:8501</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system": "Specialist Feedback Management System",
        "version": "1.0.0",
        "agents_active": len(feedback_system.master_orchestrator.agents) if hasattr(feedback_system.master_orchestrator, 'agents') else 0
    }

@app.post("/upload")
async def upload_feedback(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload and process feedback documents"""
    try:
        documents = []
        for file in files:
            content = await file.read()
            doc = FeedbackDocument(
                filename=file.filename,
                content=content.decode('utf-8'),
                content_type=file.content_type
            )
            documents.append(doc)
        
        # Start processing in background
        batch_id = await feedback_system.process_feedback_batch(documents)
        
        return {
            "message": "Files uploaded successfully",
            "batch_id": batch_id,
            "document_count": len(documents),
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{batch_id}")
async def get_status(batch_id: str):
    """Get processing status for a batch"""
    status = feedback_system.get_processing_status(batch_id)
    return status

@app.get("/results/{batch_id}")
async def get_results(batch_id: str):
    """Get processing results for a batch"""
    status = feedback_system.get_processing_status(batch_id)
    if status.get('status') == 'completed':
        return status.get('results')
    elif status.get('status') == 'processing':
        return {"message": "Processing in progress", "status": "processing"}
    else:
        raise HTTPException(status_code=404, detail="Batch not found or processing failed")

if __name__ == "__main__":
    # Run FastAPI server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
