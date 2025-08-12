"""
Data Cleaning Agent - Handles data preprocessing, cleaning, and standardization
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import string
from collections import Counter

from models.feedback_models import FeedbackDocument, CleanedDocument
from utils.logger import setup_logger

logger = setup_logger(__name__)

class DataCleaningAgent:
    """
    Data Cleaning Agent responsible for preprocessing, cleaning, and standardizing
    feedback documents to ensure high-quality input for analysis.
    """
    
    def __init__(self):
        self.agent_id = "data_cleaning_agent"
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more',
            'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
            'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get',
            'come', 'made', 'may', 'part'
        }
        
    async def initialize(self):
        """Initialize the data cleaning agent"""
        logger.info(f"Initializing {self.agent_id}")
        
    async def clean_documents(self, input_data: Dict[str, Any]) -> List[CleanedDocument]:
        """
        Clean and preprocess a batch of documents
        """
        documents = input_data.get('documents', [])
        cleaned_documents = []
        
        logger.info(f"Cleaning {len(documents)} documents")
        
        for doc in documents:
            try:
                cleaned_doc = await self._clean_single_document(doc)
                cleaned_documents.append(cleaned_doc)
                logger.debug(f"Document {doc.filename} cleaned successfully")
                
            except Exception as e:
                logger.error(f"Error cleaning document {doc.filename}: {str(e)}")
                continue
        
        logger.info(f"Successfully cleaned {len(cleaned_documents)} documents")
        return cleaned_documents
    
    async def _clean_single_document(self, doc: FeedbackDocument) -> CleanedDocument:
        """Clean a single document"""
        
        preprocessing_notes = []
        original_length = len(doc.content)
        logger.info(f"Cleaning Feedback Document {doc}")
        # Step 1: Basic text cleaning
        cleaned_content = self._basic_text_cleaning(doc.content)
        logger.info(f"Basic text cleaning applied to content: {cleaned_content}")
        if len(cleaned_content) != original_length:
            preprocessing_notes.append("Applied basic text cleaning")
        
        # Step 2: Remove duplicates and redundant content
        cleaned_content = self._remove_duplicates(cleaned_content)
        preprocessing_notes.append("Removed duplicate content")
        
        # Step 3: Normalize whitespace and formatting
        #cleaned_content = self._normalize_formatting(cleaned_content)
        #preprocessing_notes.append("Normalized formatting")
        
        # Step 4: Extract entities and key terms
        entities = self._extract_entities(cleaned_content)
        preprocessing_notes.append(f"Extracted {len(entities)} entities")
        
        # Step 5: Calculate quality metrics
        quality_score = self._calculate_quality_score(cleaned_content, doc.content)
        
        # Step 6: Detect language
        language = self._detect_language(cleaned_content)
        
        # Step 7: Count words
        word_count = len(cleaned_content.split())
        
        return CleanedDocument(
            original_id=doc.id or doc.filename,
            cleaned_content=cleaned_content,
            extracted_entities=entities,
            language=language,
            word_count=word_count,
            quality_score=quality_score,
            preprocessing_notes=preprocessing_notes
        )
    
    def _basic_text_cleaning(self, content: str) -> str:
        """Apply basic text cleaning operations"""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        logger.info(f"Basic text cleaning applied to content: {content}")
        # Remove special characters but keep punctuation
        content = re.sub(r'[^\w\s\.,!?;:()\[\]{}"\'\/\\\-]', '', content)
        logger.info(f"Special characters removed from content: {content}")
        # Fix common encoding issues
        content = content.replace('â€™', "'")
        content = content.replace('â€œ', '"')
        content = content.replace('â€', '"')
        content = content.replace('â€"', '-')
        logger.info(f"Common encoding issues fixed in content: {content}")
        # Remove URLs
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        logger.info(f"URLs removed from content: {content}")
        # Remove email addresses
        content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
        logger.info(f"Email addresses removed from content: {content}")
        return content
    
    def _remove_duplicates(self, content: str) -> str:
        """Remove duplicate sentences and paragraphs"""
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Remove duplicate sentences (case-insensitive)
        seen_sentences = set()
        unique_sentences = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if sentence_lower not in seen_sentences and len(sentence) > 10:
                seen_sentences.add(sentence_lower)
                unique_sentences.append(sentence)
        
        return '. '.join(unique_sentences) + '.'
    
    def _normalize_formatting(self, content: str) -> str:
        """Normalize text formatting"""
        logger.info(f"Normalizing formatting in content: {content}")
        # Normalize quotes
        content = re.sub(r'[""]', '"', content)
        content = re.sub(r'['']', "'", content)
        logger.info(f"Quotes normalized in content: {content}")
        # Normalize dashes
        content = re.sub(r'[–—]', '-', content)
        logger.info(f"Dashes normalized in content: {content}")
        # Fix spacing around punctuation
        content = re.sub(r'\s+([.!?,:;])', r'\1', content)
        content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
        logger.info(f"Spacing around punctuation fixed in content: {content}")
        # Normalize multiple spaces
        content = re.sub(r'\s+', ' ', content)
        logger.info(f"Multiple spaces normalized in content: {content}")
        
        return content.strip()
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract key entities and terms from content"""
        
        entities = []
        
        # Extract capitalized words (potential proper nouns)
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', content)
        entities.extend(capitalized_words)
        
        # Extract technical terms (words with numbers or special patterns)
        technical_terms = re.findall(r'\b[a-zA-Z]+[0-9]+[a-zA-Z]*\b|\b[A-Z]{2,}\b', content)
        entities.extend(technical_terms)
        
        # Extract quoted phrases
        quoted_phrases = re.findall(r'"([^"]*)"', content)
        entities.extend(quoted_phrases)
        
        # Extract domain-specific terms
        domain_terms = self._extract_domain_terms(content)
        entities.extend(domain_terms)
        
        # Remove duplicates and filter
        entities = list(set([e for e in entities if len(e) > 2 and e.lower() not in self.stop_words]))
        
        return entities[:50]  # Limit to top 50 entities
    
    def _extract_domain_terms(self, content: str) -> List[str]:
        """Extract domain-specific terms related to specialist feedback"""
        
        domain_patterns = [
            r'\b(?:process|procedure|workflow|methodology)\b',
            r'\b(?:quality|standard|compliance|audit)\b',
            r'\b(?:technical|system|software|hardware)\b',
            r'\b(?:performance|efficiency|optimization)\b',
            r'\b(?:recommendation|suggestion|improvement)\b',
            r'\b(?:issue|problem|concern|challenge)\b',
            r'\b(?:resource|allocation|budget|cost)\b',
            r'\b(?:training|skill|competency|knowledge)\b',
            r'\b(?:communication|collaboration|coordination)\b',
            r'\b(?:policy|guideline|framework|structure)\b'
        ]
        
        domain_terms = []
        content_lower = content.lower()
        
        for pattern in domain_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            domain_terms.extend(matches)
        
        return list(set(domain_terms))
    
    def _calculate_quality_score(self, cleaned_content: str, original_content: str) -> float:
        """Calculate quality score for the cleaned document"""
        
        if not cleaned_content or not original_content:
            return 0.0
        
        score = 0.0
        
        # Length preservation (0-0.2)
        length_ratio = len(cleaned_content) / len(original_content)
        if 0.7 <= length_ratio <= 1.0:
            score += 0.2
        elif 0.5 <= length_ratio < 0.7:
            score += 0.1
        
        # Sentence structure (0-0.3)
        sentences = re.split(r'[.!?]+', cleaned_content)
        valid_sentences = [s for s in sentences if len(s.strip()) > 5]
        if len(valid_sentences) > 0:
            avg_sentence_length = sum(len(s.split()) for s in valid_sentences) / len(valid_sentences)
            if 5 <= avg_sentence_length <= 30:
                score += 0.3
            elif 3 <= avg_sentence_length < 5 or 30 < avg_sentence_length <= 50:
                score += 0.2
            else:
                score += 0.1
        
        # Vocabulary diversity (0-0.2)
        words = cleaned_content.lower().split()
        if words:
            unique_words = len(set(words))
            diversity_ratio = unique_words / len(words)
            if diversity_ratio > 0.5:
                score += 0.2
            elif diversity_ratio > 0.3:
                score += 0.15
            else:
                score += 0.1
        
        # Punctuation and formatting (0-0.15)
        if re.search(r'[.!?]', cleaned_content):
            score += 0.1
        if re.search(r'[,;:]', cleaned_content):
            score += 0.05
        
        # Content coherence (0-0.15)
        if len(cleaned_content.split()) >= 10:
            score += 0.15
        elif len(cleaned_content.split()) >= 5:
            score += 0.1
        else:
            score += 0.05
        
        return min(score, 1.0)
    
    def _detect_language(self, content: str) -> str:
        """Simple language detection"""
        
        # Count English common words
        english_indicators = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
            'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'this', 'that', 'these', 'those'
        }
        
        words = re.findall(r'\b\w+\b', content.lower())
        if not words:
            return 'unknown'
        
        english_count = sum(1 for word in words if word in english_indicators)
        english_ratio = english_count / len(words)
        
        return 'en' if english_ratio > 0.05 else 'unknown'
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'stop_words_count': len(self.stop_words),
            'capabilities': [
                'text_cleaning',
                'duplicate_removal',
                'entity_extraction',
                'quality_assessment',
                'language_detection'
            ]
        }
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down {self.agent_id}")
