"""
Sentiment Analysis Agent - Performs advanced sentiment analysis on feedback documents
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

from models.feedback_models import CleanedDocument, SentimentAnalysis, SentimentType
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SentimentAnalysisAgent:
    """
    Sentiment Analysis Agent responsible for analyzing emotional tone and sentiment
    in specialist feedback using advanced NLP techniques.
    """
    
    def __init__(self):
        self.agent_id = "sentiment_analysis_agent"
        
        # Sentiment lexicons
        self.positive_words = {
            'excellent', 'outstanding', 'exceptional', 'superior', 'effective',
            'efficient', 'successful', 'improved', 'enhanced', 'optimized',
            'beneficial', 'valuable', 'useful', 'helpful', 'positive',
            'good', 'great', 'amazing', 'wonderful', 'fantastic',
            'recommend', 'commend', 'praise', 'appreciate', 'satisfied',
            'pleased', 'impressed', 'delighted', 'thrilled', 'excited',
            'innovative', 'creative', 'brilliant', 'smart', 'clever',
            'professional', 'competent', 'skilled', 'experienced', 'qualified'
        }
        
        self.negative_words = {
            'poor', 'bad', 'terrible', 'awful', 'horrible', 'disappointing',
            'ineffective', 'inefficient', 'problematic', 'concerning', 'worrying',
            'inadequate', 'insufficient', 'lacking', 'missing', 'absent',
            'failed', 'failure', 'error', 'mistake', 'issue', 'problem',
            'difficulty', 'challenge', 'obstacle', 'barrier', 'limitation',
            'frustrated', 'annoyed', 'disappointed', 'concerned', 'worried',
            'critical', 'negative', 'unsatisfactory', 'unacceptable', 'substandard',
            'deficient', 'flawed', 'broken', 'damaged', 'corrupted'
        }
        
        self.neutral_words = {
            'standard', 'normal', 'average', 'typical', 'regular', 'routine',
            'acceptable', 'adequate', 'sufficient', 'reasonable', 'fair',
            'moderate', 'balanced', 'neutral', 'objective', 'factual',
            'informational', 'descriptive', 'explanatory', 'procedural'
        }
        
        # Intensity modifiers
        self.intensifiers = {
            'very': 1.5, 'extremely': 2.0, 'highly': 1.8, 'incredibly': 2.0,
            'absolutely': 2.0, 'completely': 1.8, 'totally': 1.8, 'quite': 1.3,
            'rather': 1.2, 'somewhat': 0.8, 'slightly': 0.6, 'barely': 0.4
        }
        
        self.negators = {'not', 'no', 'never', 'none', 'nothing', 'neither', 'nor'}
        
    async def initialize(self):
        """Initialize the sentiment analysis agent"""
        logger.info(f"Initializing {self.agent_id}")
        # In a real implementation, you might load pre-trained models here
        
    async def analyze_sentiment(self, input_data: Dict[str, Any]) -> List[SentimentAnalysis]:
        """
        Analyze sentiment for a batch of cleaned documents
        """
        documents = input_data.get('documents', [])
        sentiment_results = []
        
        logger.info(f"Analyzing sentiment for {len(documents)} documents")
        
        for doc in documents:
            try:
                sentiment_result = await self._analyze_single_document(doc)
                sentiment_results.append(sentiment_result)
                logger.debug(f"Sentiment analysis completed for document {doc.original_id}")
                
            except Exception as e:
                logger.error(f"Error analyzing sentiment for document {doc.original_id}: {str(e)}")
                continue
        
        logger.info(f"Successfully analyzed sentiment for {len(sentiment_results)} documents")
        return sentiment_results
    
    async def _analyze_single_document(self, doc: CleanedDocument) -> SentimentAnalysis:
        """Analyze sentiment for a single document"""
        
        content = doc.cleaned_content.lower()
        
        # Step 1: Lexicon-based sentiment scoring
        lexicon_score, lexicon_confidence = self._lexicon_based_analysis(content)
        
        # Step 2: Pattern-based sentiment analysis
        pattern_score, pattern_confidence = self._pattern_based_analysis(content)
        
        # Step 3: Context-aware sentiment analysis
        context_score, context_confidence = self._context_aware_analysis(content)
        
        # Step 4: Combine scores with weighted average
        weights = [0.4, 0.3, 0.3]  # lexicon, pattern, context
        confidences = [lexicon_confidence, pattern_confidence, context_confidence]
        scores = [lexicon_score, pattern_score, context_score]
        
        # Weighted average
        overall_score = sum(w * s for w, s in zip(weights, scores))
        overall_confidence = sum(w * c for w, c in zip(weights, confidences))
        
        # Step 5: Determine sentiment type
        sentiment_type = self._score_to_sentiment_type(overall_score)
        
        # Step 6: Extract key phrases and emotional indicators
        key_phrases = self._extract_key_phrases(doc.cleaned_content)
        emotional_indicators = self._extract_emotional_indicators(doc.cleaned_content)
        
        # Step 7: Create sentiment breakdown
        sentiment_breakdown = {
            'lexicon_score': lexicon_score,
            'pattern_score': pattern_score,
            'context_score': context_score,
            'lexicon_confidence': lexicon_confidence,
            'pattern_confidence': pattern_confidence,
            'context_confidence': context_confidence
        }
        
        return SentimentAnalysis(
            document_id=doc.original_id,
            overall_sentiment=sentiment_type,
            sentiment_score=round(overall_score, 3),
            confidence=round(overall_confidence, 3),
            sentiment_breakdown=sentiment_breakdown,
            key_phrases=key_phrases,
            emotional_indicators=emotional_indicators
        )
    
    def _lexicon_based_analysis(self, content: str) -> Tuple[float, float]:
        """Perform lexicon-based sentiment analysis"""
        
        words = re.findall(r'\b\w+\b', content)
        if not words:
            return 0.0, 0.0
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_sentiment_words = 0
        
        i = 0
        while i < len(words):
            word = words[i]
            
            # Check for negation
            negated = False
            if i > 0 and words[i-1] in self.negators:
                negated = True
            
            # Check for intensifiers
            intensity = 1.0
            if i > 0 and words[i-1] in self.intensifiers:
                intensity = self.intensifiers[words[i-1]]
            
            # Score the word
            if word in self.positive_words:
                score = intensity * (1 if not negated else -1)
                positive_count += max(0, score)
                negative_count += max(0, -score)
                total_sentiment_words += 1
            elif word in self.negative_words:
                score = intensity * (-1 if not negated else 1)
                positive_count += max(0, score)
                negative_count += max(0, -score)
                total_sentiment_words += 1
            elif word in self.neutral_words:
                neutral_count += 1
                total_sentiment_words += 1
            
            i += 1
        
        if total_sentiment_words == 0:
            return 0.0, 0.0
        
        # Calculate sentiment score (-1 to 1)
        sentiment_score = (positive_count - negative_count) / total_sentiment_words
        
        # Calculate confidence based on sentiment word density
        confidence = min(total_sentiment_words / len(words), 1.0)
        
        return sentiment_score, confidence
    
    def _pattern_based_analysis(self, content: str) -> Tuple[float, float]:
        """Analyze sentiment based on linguistic patterns"""
        
        score = 0.0
        pattern_count = 0
        
        # Positive patterns
        positive_patterns = [
            r'\b(?:recommend|suggest|advise)\b.*\b(?:highly|strongly)\b',
            r'\b(?:excellent|outstanding|exceptional)\b.*\b(?:work|job|performance)\b',
            r'\b(?:very|extremely)\b.*\b(?:pleased|satisfied|impressed)\b',
            r'\b(?:significant|substantial)\b.*\b(?:improvement|progress|enhancement)\b',
            r'\b(?:well|effectively|efficiently)\b.*\b(?:implemented|executed|managed)\b'
        ]
        
        for pattern in positive_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            score += matches * 0.8
            pattern_count += matches
        
        # Negative patterns
        negative_patterns = [
            r'\b(?:major|serious|significant)\b.*\b(?:issue|problem|concern)\b',
            r'\b(?:failed|failure)\b.*\b(?:to|in)\b',
            r'\b(?:lack|lacking|absence)\b.*\b(?:of|in)\b',
            r'\b(?:disappointed|frustrated|concerned)\b.*\b(?:with|about)\b',
            r'\b(?:needs|requires)\b.*\b(?:immediate|urgent)\b.*\b(?:attention|action)\b'
        ]
        
        for pattern in negative_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            score -= matches * 0.8
            pattern_count += matches
        
        # Neutral/informational patterns
        neutral_patterns = [
            r'\b(?:according|based)\b.*\b(?:to|on)\b',
            r'\b(?:data|statistics|metrics)\b.*\b(?:show|indicate|suggest)\b',
            r'\b(?:process|procedure|method)\b.*\b(?:involves|includes|requires)\b'
        ]
        
        for pattern in neutral_patterns:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            pattern_count += matches
        
        # Normalize score
        if pattern_count > 0:
            score = score / pattern_count
            confidence = min(pattern_count / 10, 1.0)  # Max confidence at 10 patterns
        else:
            confidence = 0.0
        
        return max(-1.0, min(1.0, score)), confidence
    
    def _context_aware_analysis(self, content: str) -> Tuple[float, float]:
        """Perform context-aware sentiment analysis"""
        
        sentences = re.split(r'[.!?]+', content)
        sentence_scores = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 5:
                continue
            
            # Analyze sentence structure and context
            sentence_score = 0.0
            
            # Question vs statement analysis
            if sentence.endswith('?'):
                sentence_score -= 0.1  # Questions often indicate uncertainty/problems
            
            # Conditional statements
            if re.search(r'\b(?:if|unless|provided|assuming)\b', sentence):
                sentence_score -= 0.2  # Conditional statements indicate uncertainty
            
            # Comparative statements
            if re.search(r'\b(?:better|worse|more|less|compared|versus)\b', sentence):
                # Determine if comparison is positive or negative
                if re.search(r'\b(?:better|more|improved|enhanced)\b', sentence):
                    sentence_score += 0.3
                elif re.search(r'\b(?:worse|less|declined|degraded)\b', sentence):
                    sentence_score -= 0.3
            
            # Temporal context
            if re.search(r'\b(?:previously|before|used to)\b', sentence):
                sentence_score -= 0.1  # Past issues
            elif re.search(r'\b(?:now|currently|recently)\b', sentence):
                sentence_score += 0.1  # Current improvements
            
            # Certainty indicators
            if re.search(r'\b(?:clearly|obviously|definitely|certainly)\b', sentence):
                sentence_score += 0.2  # High certainty
            elif re.search(r'\b(?:maybe|perhaps|possibly|might)\b', sentence):
                sentence_score -= 0.1  # Low certainty
            
            sentence_scores.append(sentence_score)
        
        if not sentence_scores:
            return 0.0, 0.0
        
        # Calculate overall context score
        context_score = sum(sentence_scores) / len(sentence_scores)
        confidence = min(len(sentence_scores) / 5, 1.0)  # Max confidence at 5 sentences
        
        return max(-1.0, min(1.0, context_score)), confidence
    
    def _score_to_sentiment_type(self, score: float) -> SentimentType:
        """Convert numerical score to sentiment type"""
        
        if score > 0.1:
            return SentimentType.POSITIVE
        elif score < -0.1:
            return SentimentType.NEGATIVE
        elif abs(score) <= 0.1:
            return SentimentType.NEUTRAL
        else:
            return SentimentType.MIXED
    
    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases that contribute to sentiment"""
        
        key_phrases = []
        
        # Extract phrases with sentiment words
        sentiment_phrase_patterns = [
            r'\b(?:very|extremely|highly|quite)\s+\w+',
            r'\b\w+\s+(?:recommend|suggest|advise)',
            r'\b(?:significant|major|minor)\s+\w+',
            r'\b\w+\s+(?:improvement|enhancement|issue|problem)',
            r'\b(?:well|poorly|effectively|ineffectively)\s+\w+'
        ]
        
        for pattern in sentiment_phrase_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            key_phrases.extend(matches)
        
        # Remove duplicates and limit
        key_phrases = list(set(key_phrases))[:20]
        
        return key_phrases
    
    def _extract_emotional_indicators(self, content: str) -> List[str]:
        """Extract emotional indicators from content"""
        
        emotional_indicators = []
        
        # Emotional words and phrases
        emotional_patterns = [
            r'\b(?:excited|thrilled|delighted|pleased|satisfied)\b',
            r'\b(?:frustrated|disappointed|concerned|worried|annoyed)\b',
            r'\b(?:impressed|amazed|surprised|shocked)\b',
            r'\b(?:confident|uncertain|doubtful|skeptical)\b',
            r'\b(?:optimistic|pessimistic|hopeful|hopeless)\b'
        ]
        
        for pattern in emotional_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            emotional_indicators.extend(matches)
        
        # Remove duplicates
        emotional_indicators = list(set(emotional_indicators))
        
        return emotional_indicators
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'lexicon_stats': {
                'positive_words': len(self.positive_words),
                'negative_words': len(self.negative_words),
                'neutral_words': len(self.neutral_words),
                'intensifiers': len(self.intensifiers),
                'negators': len(self.negators)
            },
            'analysis_methods': [
                'lexicon_based',
                'pattern_based',
                'context_aware'
            ]
        }
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down {self.agent_id}")
