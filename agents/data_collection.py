"""
Data Collection Agent - Handles feedback data collection, validation, and enrichment
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
from pathlib import Path

from models.feedback_models import FeedbackDocument, FeedbackSource
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataCollectionAgent:
    """
    Data Collection Agent responsible for gathering, validating, and enriching
    feedback documents from various specialist sources.
    """
    
    def __init__(self):
        self.agent_id = "data_collection_agent"
        self.supported_formats = ['.txt', '.pdf', '.docx', '.csv', '.json']
        self.min_content_length = 10
        self.max_content_length = 1000000  # 1MB text limit
        
    async def initialize(self):
        """Initialize the data collection agent"""
        logger.info(f"Initializing {self.agent_id}")
        # Initialize any required resources
        
    async def validate_and_enrich(self, input_data: Dict[str, Any]) -> List[FeedbackDocument]:
        """
        Validate and enrich feedback documents
        """
        documents = input_data.get('documents', [])
        validated_documents = []
        
        logger.info(f"Validating and enriching {len(documents)} documents")
        
        for doc in documents:
            try:
                # Validate document
                if await self._validate_document(doc):
                    # Enrich document with metadata
                    enriched_doc = await self._enrich_document(doc)
                    validated_documents.append(enriched_doc)
                    logger.debug(f"Document {doc.filename} validated and enriched")
                else:
                    logger.warning(f"Document {doc.filename} failed validation")
                    
            except Exception as e:
                logger.error(f"Error processing document {doc.filename}: {str(e)}")
                continue
        
        logger.info(f"Successfully validated {len(validated_documents)} out of {len(documents)} documents")
        return validated_documents
    
    async def _validate_document(self, doc: FeedbackDocument) -> bool:
        """Validate a single document"""
        
        # Check content length
        if len(doc.content) < self.min_content_length:
            logger.warning(f"Document {doc.filename} content too short: {len(doc.content)} characters")
            return False
            
        if len(doc.content) > self.max_content_length:
            logger.warning(f"Document {doc.filename} content too long: {len(doc.content)} characters")
            return False
        
        # Check for valid text content
        if not self._is_valid_text(doc.content):
            logger.warning(f"Document {doc.filename} contains invalid text")
            return False
        
        # Check filename
        if not doc.filename or len(doc.filename.strip()) == 0:
            logger.warning("Document has invalid filename")
            return False
        
        return True
    
    def _is_valid_text(self, content: str) -> bool:
        """Check if content contains valid text"""
        # Remove whitespace and check if there's actual content
        clean_content = content.strip()
        if not clean_content:
            return False
        
        # Check for minimum ratio of alphanumeric characters
        alphanumeric_count = sum(1 for c in clean_content if c.isalnum())
        if alphanumeric_count / len(clean_content) < 0.1:  # At least 10% alphanumeric
            return False
        
        return True
    
    async def _enrich_document(self, doc: FeedbackDocument) -> FeedbackDocument:
        """Enrich document with additional metadata"""
        
        # Detect source type based on content and filename
        doc.source = self._detect_source_type(doc)
        
        # Add metadata
        doc.metadata.update({
            'word_count': len(doc.content.split()),
            'character_count': len(doc.content),
            'line_count': len(doc.content.splitlines()),
            'processed_at': datetime.now().isoformat(),
            'agent_version': '1.0.0'
        })
        
        # Extract basic statistics
        doc.metadata.update(self._extract_basic_stats(doc.content))
        
        # Detect language (simple heuristic)
        doc.metadata['detected_language'] = self._detect_language(doc.content)
        
        return doc
    
    def _detect_source_type(self, doc: FeedbackDocument) -> FeedbackSource:
        """Detect the source type of the document based on content and filename"""
        
        content_lower = doc.content.lower()
        filename_lower = doc.filename.lower()
        
        # Check filename patterns
        if any(term in filename_lower for term in ['expert', 'specialist', 'review']):
            return FeedbackSource.EXPERT_REPORT
        elif any(term in filename_lower for term in ['internal', 'assessment']):
            return FeedbackSource.INTERNAL_ASSESSMENT
        elif any(term in filename_lower for term in ['peer', 'colleague']):
            return FeedbackSource.PEER_REVIEW
        elif any(term in filename_lower for term in ['technical', 'tech']):
            return FeedbackSource.TECHNICAL_REVIEW
        elif any(term in filename_lower for term in ['process', 'procedure']):
            return FeedbackSource.PROCESS_EVALUATION
        elif any(term in filename_lower for term in ['quality', 'audit']):
            return FeedbackSource.QUALITY_AUDIT
        
        # Check content patterns
        if any(term in content_lower for term in ['technical issue', 'bug', 'error', 'system']):
            return FeedbackSource.TECHNICAL_REVIEW
        elif any(term in content_lower for term in ['process', 'procedure', 'workflow']):
            return FeedbackSource.PROCESS_EVALUATION
        elif any(term in content_lower for term in ['quality', 'standard', 'compliance']):
            return FeedbackSource.QUALITY_AUDIT
        elif any(term in content_lower for term in ['expert opinion', 'specialist view']):
            return FeedbackSource.EXPERT_REPORT
        
        return FeedbackSource.OTHER
    
    def _extract_basic_stats(self, content: str) -> Dict[str, Any]:
        """Extract basic statistics from content"""
        
        # Count sentences (simple heuristic)
        sentence_count = len(re.findall(r'[.!?]+', content))
        
        # Count paragraphs
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # Count unique words
        words = re.findall(r'\b\w+\b', content.lower())
        unique_words = len(set(words))
        
        # Calculate readability metrics (simple)
        avg_sentence_length = len(words) / max(sentence_count, 1)
        
        return {
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'unique_words': unique_words,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'vocabulary_richness': round(unique_words / max(len(words), 1), 3)
        }
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection (English-focused)"""
        
        # Count English common words
        english_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'a', 'an'
        }
        
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return 'unknown'
        
        english_count = sum(1 for word in words if word in english_words)
        english_ratio = english_count / len(words)
        
        if english_ratio > 0.1:  # At least 10% common English words
            return 'en'
        else:
            return 'unknown'
    
    async def collect_from_directory(self, directory_path: str) -> List[FeedbackDocument]:
        """Collect feedback documents from a directory"""
        
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return documents
        
        logger.info(f"Collecting documents from directory: {directory_path}")
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    content = await self._read_file(file_path)
                    if content:
                        doc = FeedbackDocument(
                            filename=file_path.name,
                            content=content,
                            content_type=self._get_content_type(file_path.suffix)
                        )
                        documents.append(doc)
                        logger.debug(f"Collected document: {file_path.name}")
                        
                except Exception as e:
                    logger.error(f"Error reading file {file_path}: {str(e)}")
                    continue
        
        logger.info(f"Collected {len(documents)} documents from directory")
        return documents
    
    async def _read_file(self, file_path: Path) -> Optional[str]:
        """Read content from a file"""
        
        try:
            if file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # For other formats, return placeholder
                # In a real implementation, you'd use appropriate libraries
                return f"Content from {file_path.name} (format: {file_path.suffix})"
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")
            return None
    
    def _get_content_type(self, file_extension: str) -> str:
        """Get content type based on file extension"""
        
        content_types = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.csv': 'text/csv',
            '.json': 'application/json'
        }
        
        return content_types.get(file_extension.lower(), 'text/plain')
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'supported_formats': self.supported_formats,
            'content_limits': {
                'min_length': self.min_content_length,
                'max_length': self.max_content_length
            }
        }
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down {self.agent_id}")
        # Clean up any resources
