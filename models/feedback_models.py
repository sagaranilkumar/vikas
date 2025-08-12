"""
Data models for the Specialist Feedback Management System
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum

class FeedbackSource(str, Enum):
    """Types of feedback sources"""
    EXPERT_REPORT = "expert_report"
    INTERNAL_ASSESSMENT = "internal_assessment"
    PEER_REVIEW = "peer_review"
    TECHNICAL_REVIEW = "technical_review"
    PROCESS_EVALUATION = "process_evaluation"
    QUALITY_AUDIT = "quality_audit"
    OTHER = "other"

class SentimentType(str, Enum):
    """Sentiment classification types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"

class FeedbackCategory(str, Enum):
    """Feedback categorization types"""
    TECHNICAL_ISSUES = "technical_issues"
    PROCEDURAL_INEFFICIENCIES = "procedural_inefficiencies"
    RESOURCE_ALLOCATION = "resource_allocation"
    COMMUNICATION = "communication"
    TRAINING_NEEDS = "training_needs"
    SYSTEM_IMPROVEMENTS = "system_improvements"
    POLICY_RECOMMENDATIONS = "policy_recommendations"
    OTHER = "other"

class ProcessingStatus(str, Enum):
    """Processing status types"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class FeedbackDocument(BaseModel):
    """Model for feedback documents"""
    id: Optional[str] = None
    filename: str
    content: str
    content_type: Optional[str] = "text/plain"
    source: Optional[FeedbackSource] = FeedbackSource.OTHER
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True

class CleanedDocument(BaseModel):
    """Model for cleaned and processed documents"""
    original_id: str
    cleaned_content: str
    extracted_entities: List[str] = Field(default_factory=list)
    language: str = "en"
    word_count: int = 0
    quality_score: float = 0.0
    preprocessing_notes: List[str] = Field(default_factory=list)

class SentimentAnalysis(BaseModel):
    """Model for sentiment analysis results"""
    document_id: str
    overall_sentiment: SentimentType
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    sentiment_breakdown: Dict[str, float] = Field(default_factory=dict)
    key_phrases: List[str] = Field(default_factory=list)
    emotional_indicators: List[str] = Field(default_factory=list)

class CategoryResult(BaseModel):
    """Model for categorization results"""
    document_id: str
    primary_category: FeedbackCategory
    secondary_categories: List[FeedbackCategory] = Field(default_factory=list)
    category_confidence: Dict[str, float] = Field(default_factory=dict)
    keywords: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

class InsightData(BaseModel):
    """Model for generated insights"""
    insight_type: str
    description: str
    supporting_evidence: List[str] = Field(default_factory=list)
    frequency: int = 1
    severity: str = "medium"  # low, medium, high, critical
    trend_direction: Optional[str] = None  # increasing, decreasing, stable
    affected_areas: List[str] = Field(default_factory=list)

class Recommendation(BaseModel):
    """Model for generated recommendations"""
    title: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    category: str
    implementation_effort: str = "medium"  # low, medium, high
    expected_impact: str = "medium"  # low, medium, high
    timeline: str = "short-term"  # short-term, medium-term, long-term
    resources_required: List[str] = Field(default_factory=list)
    success_metrics: List[str] = Field(default_factory=list)
    related_insights: List[str] = Field(default_factory=list)

class ProcessingResult(BaseModel):
    """Complete processing result for a batch of documents"""
    batch_id: str
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    total_documents: int
    processed_documents: int
    failed_documents: int = 0
    
    # Processing results
    sentiment_results: List[SentimentAnalysis] = Field(default_factory=list)
    categorization_results: List[CategoryResult] = Field(default_factory=list)
    insights: List[InsightData] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    
    # Summary statistics
    sentiment_distribution: Dict[str, int] = Field(default_factory=dict)
    category_distribution: Dict[str, int] = Field(default_factory=dict)
    processing_time_seconds: float = 0.0
    
    # Quality metrics
    average_confidence: float = 0.0
    data_quality_score: float = 0.0
    
    class Config:
        use_enum_values = True

class AgentTask(BaseModel):
    """Model for agent tasks"""
    task_id: str
    agent_name: str
    task_type: str
    input_data: Dict[str, Any]
    status: ProcessingStatus = ProcessingStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    class Config:
        use_enum_values = True

class KnowledgeGraphNode(BaseModel):
    """Model for knowledge graph nodes"""
    node_id: str
    node_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    relationships: List[str] = Field(default_factory=list)

class KnowledgeGraphRelationship(BaseModel):
    """Model for knowledge graph relationships"""
    relationship_id: str
    source_node: str
    target_node: str
    relationship_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
