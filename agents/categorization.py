"""
Categorization Agent - Classifies feedback into specific categories and topics
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

from models.feedback_models import CleanedDocument, CategoryResult, FeedbackCategory
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CategorizationAgent:
    """
    Categorization Agent responsible for classifying feedback documents into
    specific categories and topics using rule-based and ML-based approaches.
    """
    
    def __init__(self):
        self.agent_id = "categorization_agent"
        self.min_confidence_threshold = 0.3
        
        # Category patterns with weights
        self.category_patterns = {
            FeedbackCategory.TECHNICAL_ISSUES: [
                (r'\b(?:error|bug|issue|problem|crash|failure|defect|glitch)\b', 0.8),
                (r'\b(?:not working|doesn\'?t work|broken|malfunction|failure)\b', 0.7),
                (r'\b(?:performance|slow|lag|latency|timeout|response time)\b', 0.6),
                (r'\b(?:compatibility|version|update|upgrade|migration)\b', 0.5),
                (r'\b(?:bug|defect|flaw|vulnerability|security|hack|breach)\b', 0.8)
            ],
            FeedbackCategory.PROCEDURAL_INEFFICIENCIES: [
                (r'\b(?:process|procedure|workflow|methodology|steps|protocol)\b', 0.7),
                (r'\b(?:inefficient|bottleneck|redundant|duplicate|repetitive)\b', 0.8),
                (r'\b(?:complicated|complex|convoluted|confusing|unclear|vague)\b', 0.7),
                (r'\b(?:time.?consuming|takes too long|lengthy|delayed|slow)\b', 0.6),
                (r'\b(?:manual|automate|automation|streamline|optimize|improve)\b', 0.6)
            ],
            FeedbackCategory.RESOURCE_ALLOCATION: [
                (r'\b(?:resource|budget|funding|allocation|staffing|personnel)\b', 0.8),
                (r'\b(?:insufficient|limited|lack|shortage|constraint|restriction)\b', 0.7),
                (r'\b(?:need more|require additional|not enough|too few|inadequate)\b', 0.7),
                (r'\b(?:workload|capacity|utilization|overload|overwhelmed|burnout)\b', 0.6),
                (r'\b(?:cost|expensive|over budget|financial|ROI|return on investment)\b', 0.7)
            ],
            FeedbackCategory.COMMUNICATION: [
                (r'\b(?:communication|inform|notify|update|announce|announcement)\b', 0.8),
                (r'\b(?:unclear|confusing|vague|ambiguous|misleading|contradictory)\b', 0.7),
                (r'\b(?:response|reply|answer|feedback|acknowledgment|confirmation)\b', 0.7),
                (r'\b(?:documentation|manual|guide|tutorial|help|instructions|FAQ)\b', 0.6),
                (r'\b(?:language|jargon|technical term|acronym|abbreviation|slang)\b', 0.5)
            ],
            FeedbackCategory.TRAINING_NEEDS: [
                (r'\b(?:train|training|educate|teach|instruct|coach|mentor|workshop)\b', 0.9),
                (r'\b(?:skill|knowledge|expertise|proficiency|competency|ability)\b', 0.7),
                (r'\b(?:new hire|onboarding|orientation|induction|introduction)\b', 0.8),
                (r'\b(?:certification|certify|accreditation|qualification|license)\b', 0.7),
                (r'\b(?:knowledge gap|skill gap|learning curve|familiarity|experience)\b', 0.7)
            ],
            FeedbackCategory.SYSTEM_IMPROVEMENTS: [
                (r'\b(?:feature|functionality|tool|system|application|platform|software)\b', 0.7),
                (r'\b(?:enhance|improve|upgrade|update|modernize|refactor|redesign)\b', 0.8),
                (r'\b(?:user.?friendly|intuitive|easy to use|straightforward|simple)\b', 0.7),
                (r'\b(?:integration|API|interface|connection|compatibility|interoperability)\b', 0.7),
                (r'\b(?:customization|configuration|setting|preference|option|parameter)\b', 0.6)
            ],
            FeedbackCategory.POLICY_RECOMMENDATIONS: [
                (r'\b(?:policy|policies|guideline|rule|regulation|standard|protocol)\b', 0.9),
                (r'\b(?:compliance|regulatory|legal|law|statute|mandate|requirement)\b', 0.8),
                (r'\b(?:change|update|revise|modify|amend|reform|overhaul|update)\b', 0.7),
                (r'\b(?:best practice|industry standard|benchmark|framework|model)\b', 0.7),
                (r'\b(?:risk|liability|responsibility|accountability|governance)\b', 0.6)
            ]
        }
        
        # Topic extraction patterns
        self.topic_patterns = [
            (r'\b(?:focus|concentrate|priority|emphasis|highlight|address)\s+on\s+(?:the\s+)?([\w\s]+?)(?:\.|,|;|\s+and|\s+or|\s+but|$)', 0.8),  # Focus on [topic]
            (r'\b(?:issue|problem|challenge|difficulty|obstacle|barrier|bottleneck)\s+(?:with|in|regarding|related\s+to)\s+(?:the\s+)?([\w\s]+?)(?:\.|,|;|\s+and|\s+or|\s+but|$)', 0.9),  # Issue with [topic]
            (r'\b(?:improve|enhance|upgrade|update|modify|change|fix|resolve|address)\s+(?:the\s+)?([\w\s]+?)(?:\.|,|;|\s+and|\s+or|\s+but|$)', 0.8),  # Improve [topic]
            (r'\b(?:need|require|want|must|should|could|would)\s+(?:to\s+)?(?:have|get|implement|add|create|develop|build|design)\s+(?:a\s+)?(?:new\s+)?([\w\s]+?)(?:\.|,|;|\s+and|\s+or|\s+but|$)', 0.7),  # Need [topic]
            (r'\b(?:the|this|our|current|existing)\s+([\w\s]+?)\s+(?:is|are|was|were|has|have|had|needs?|requires?|lacks?|missing)', 0.6)  # The [topic] is...
        ]
        
        # Category descriptions for better matching
        self.category_descriptions = {
            FeedbackCategory.TECHNICAL_ISSUES: "Problems with software, hardware, or technical systems including bugs, errors, performance issues, and compatibility problems.",
            FeedbackCategory.PROCEDURAL_INEFFICIENCIES: "Ineffective or inefficient processes, workflows, or methodologies that could be streamlined or improved.",
            FeedbackCategory.RESOURCE_ALLOCATION: "Issues related to the distribution or availability of resources including budget, staffing, tools, and time.",
            FeedbackCategory.COMMUNICATION: "Problems with information sharing, clarity, or effectiveness of communication channels and documentation.",
            FeedbackCategory.TRAINING_NEEDS: "Gaps in knowledge, skills, or training that prevent optimal performance or adoption.",
            FeedbackCategory.SYSTEM_IMPROVEMENTS: "Suggestions or needs for enhancing or adding features to systems, tools, or platforms.",
            FeedbackCategory.POLICY_RECOMMENDATIONS: "Proposed changes or additions to policies, guidelines, or standards."
        }
        
    async def initialize(self):
        """Initialize the categorization agent"""
        logger.info(f"Initializing {self.agent_id}")
        # In a real implementation, you might load ML models here
        
    async def categorize_feedback(self, input_data: Dict[str, Any]) -> List[CategoryResult]:
        """
        Categorize a batch of cleaned documents
        """
        documents = input_data.get('documents', [])
        categorization_results = []
        
        logger.info(f"Categorizing {len(documents)} documents")
        
        for doc in documents:
            try:
                category_result = await self._categorize_single_document(doc)
                categorization_results.append(category_result)
                logger.debug(f"Categorized document {doc.original_id} as {category_result.primary_category}")
                
            except Exception as e:
                logger.error(f"Error categorizing document {doc.original_id}: {str(e)}")
                continue
        
        logger.info(f"Successfully categorized {len(categorization_results)} documents")
        return categorization_results
    
    async def _categorize_single_document(self, doc: CleanedDocument) -> CategoryResult:
        """Categorize a single document"""
        
        content = doc.cleaned_content.lower()
        
        # Step 1: Rule-based categorization
        rule_based_categories = self._rule_based_categorization(content)
        
        # Step 2: Extract topics and keywords
        topics = self._extract_topics(content)
        keywords = self._extract_keywords(content)
        
        # Step 3: Determine primary and secondary categories
        primary_category, category_confidences = self._determine_categories(rule_based_categories)
        
        # Step 4: Filter categories by confidence threshold
        filtered_categories = {
            cat: conf for cat, conf in category_confidences.items() 
            if conf >= self.min_confidence_threshold
        }
        
        # Sort categories by confidence (descending)
        sorted_categories = sorted(
            filtered_categories.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Get primary and secondary categories
        primary = sorted_categories[0][0] if sorted_categories else FeedbackCategory.OTHER
        secondaries = [cat for cat, _ in sorted_categories[1:3]]  # Top 2-3 categories
        
        return CategoryResult(
            document_id=doc.original_id,
            primary_category=primary,
            secondary_categories=secondaries,
            category_confidence=dict(sorted_categories[:5]),  # Top 5 categories with confidences
            keywords=keywords[:20],  # Limit to top 20 keywords
            topics=topics[:10]  # Limit to top 10 topics
        )
    
    def _rule_based_categorization(self, content: str) -> Dict[FeedbackCategory, float]:
        """Perform rule-based categorization using pattern matching"""
        
        category_scores = defaultdict(float)
        
        # Score each category based on pattern matches
        for category, patterns in self.category_patterns.items():
            for pattern, weight in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                category_scores[category] += len(matches) * weight
        
        # Normalize scores (0-1 range)
        max_score = max(category_scores.values()) if category_scores else 1.0
        if max_score > 0:
            for category in category_scores:
                category_scores[category] = min(category_scores[category] / max_score, 1.0)
        
        return dict(category_scores)
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract potential topics from content"""
        
        topics = []
        
        # Extract topics using patterns
        for pattern, confidence in self.topic_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle capture groups
                    topic = next((m for m in match if m), '').strip()
                else:
                    topic = match.strip()
                
                if topic and len(topic.split()) <= 5:  # Limit topic length
                    topics.append((topic, confidence))
        
        # Process and rank topics
        topic_scores = defaultdict(float)
        for topic, confidence in topics:
            # Clean up the topic
            topic = re.sub(r'^[^\w]+|[^\w]+$', '', topic)  # Remove leading/trailing non-word chars
            topic = re.sub(r'\s+', ' ', topic).strip()  # Normalize whitespace
            
            if topic and len(topic) >= 3:  # Minimum length
                topic_scores[topic] += confidence
        
        # Sort by score (descending) and return top topics
        sorted_topics = sorted(
            topic_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [topic for topic, _ in sorted_topics]
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content"""
        
        # Remove common words and get word frequencies
        words = re.findall(r'\b[a-z]{3,}\b', content.lower())
        
        # Common words to exclude
        common_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'any', 'can',
            'our', 'was', 'has', 'had', 'she', 'all', 'its', 'her', 'with', 'this',
            'that', 'from', 'have', 'they', 'will', 'would', 'there', 'their', 'what',
            'about', 'which', 'when', 'make', 'like', 'time', 'just', 'know', 'take',
            'into', 'year', 'your', 'good', 'some', 'could', 'them', 'other', 'than',
            'then', 'look', 'only', 'come', 'over', 'think', 'also', 'back', 'after',
            'used', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new',
            'want', 'because', 'any', 'these', 'give', 'most', 'should', 'need', 'when',
            'where', 'why', 'how', 'what', 'who', 'whom', 'whose', 'which', 'that',
            'this', 'these', 'those', 'here', 'there', 'when', 'while', 'before',
            'after', 'since', 'until', 'because', 'although', 'though', 'even', 'if',
            'unless', 'while', 'whereas', 'whether', 'either', 'neither', 'both',
            'each', 'every', 'all', 'any', 'none', 'some', 'such', 'own', 'same',
            'more', 'most', 'less', 'least', 'few', 'many', 'much', 'several', 'one',
            'two', 'three', 'first', 'second', 'last', 'next', 'previous', 'same',
            'different', 'other', 'another', 'such', 'certain', 'various', 'same'
        }
        
        # Filter out common words and count frequencies
        word_freq = Counter(
            word for word in words 
            if word not in common_words and len(word) > 2
        )
        
        # Get most common keywords (up to 20)
        keywords = [word for word, _ in word_freq.most_common(20)]
        
        return keywords
    
    def _determine_categories(
        self, 
        category_scores: Dict[FeedbackCategory, float]
    ) -> Tuple[FeedbackCategory, Dict[FeedbackCategory, float]]:
        """Determine primary and secondary categories based on scores"""
        
        if not category_scores:
            return FeedbackCategory.OTHER, {FeedbackCategory.OTHER: 1.0}
        
        # Sort categories by score (descending)
        sorted_categories = sorted(
            category_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Get primary category (highest score)
        primary_category = sorted_categories[0][0] if sorted_categories[0][1] > 0 else FeedbackCategory.OTHER
        
        # Normalize confidences to sum to 1.0
        total_score = sum(score for _, score in sorted_categories)
        normalized_confidences = {
            category: (score / total_score if total_score > 0 else 0.0)
            for category, score in sorted_categories
        }
        
        return primary_category, normalized_confidences
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'categories': [cat.value for cat in FeedbackCategory],
            'min_confidence_threshold': self.min_confidence_threshold,
            'category_patterns_count': sum(len(patterns) for patterns in self.category_patterns.values()),
            'topic_patterns_count': len(self.topic_patterns)
        }
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down {self.agent_id}")
