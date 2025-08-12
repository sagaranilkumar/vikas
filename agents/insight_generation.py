"""
Insight Generation Agent - Identifies trends, patterns, and insights from feedback data
"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter

from models.feedback_models import (
    CleanedDocument, CategoryResult, SentimentAnalysis, 
    InsightData, FeedbackCategory, SentimentType
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class InsightGenerationAgent:
    """
    Insight Generation Agent responsible for analyzing feedback data to identify
    trends, patterns, and actionable insights across multiple dimensions.
    """
    
    def __init__(self):
        self.agent_id = "insight_generation_agent"
        self.min_insight_support = 3  # Minimum occurrences for trend detection
        self.min_sentiment_impact = 0.3  # Minimum sentiment impact for insights
        self.time_window_days = 30  # Default time window for temporal analysis
        
        # Insight type configurations
        self.insight_types = {
            'trend': {
                'min_confidence': 0.7,
                'description': 'Identified trends over time in feedback data'
            },
            'pattern': {
                'min_confidence': 0.6,
                'description': 'Recognized patterns in feedback content and metadata'
            },
            'anomaly': {
                'min_confidence': 0.8,
                'description': 'Detected anomalies or outliers in feedback data'
            },
            'correlation': {
                'min_confidence': 0.65,
                'description': 'Found correlations between different feedback aspects'
            },
            'sentiment_shift': {
                'min_confidence': 0.7,
                'description': 'Significant changes in sentiment patterns'
            },
            'emerging_topic': {
                'min_confidence': 0.6,
                'description': 'New or increasing topics in feedback'
            },
            'frequent_issue': {
                'min_confidence': 0.75,
                'description': 'Recurring problems or complaints'
            },
            'improvement_area': {
                'min_confidence': 0.7,
                'description': 'Areas needing attention or enhancement'
            },
            'success_story': {
                'min_confidence': 0.8,
                'description': 'Positive outcomes or effective solutions'
            },
            'feedback_quality': {
                'min_confidence': 0.7,
                'description': 'Insights about feedback quality and characteristics'
            }
        }
        
        # Common phrases indicating importance or frequency
        self.importance_indicators = [
            'critical', 'important', 'essential', 'vital', 'crucial',
            'major', 'significant', 'serious', 'urgent', 'priority',
            'frequent', 'recurring', 'repeated', 'consistent', 'persistent',
            'many', 'several', 'multiple', 'various', 'numerous',
            'always', 'often', 'frequently', 'repeatedly', 'constantly',
            'increasing', 'growing', 'rising', 'escalating', 'worsening',
            'decreasing', 'declining', 'improving', 'better', 'worse'
        ]
        
    async def initialize(self):
        """Initialize the insight generation agent"""
        logger.info(f"Initializing {self.agent_id}")
        # In a real implementation, you might load ML models or historical data here
        
    async def generate_insights(
        self, 
        input_data: Dict[str, Any]
    ) -> List[InsightData]:
        """
        Generate insights from processed feedback data
        """
        documents = input_data.get('documents', [])
        sentiment_results = input_data.get('sentiment_results', [])
        categorization_results = input_data.get('categorization_results', [])
        
        if not documents or not sentiment_results or not categorization_results:
            logger.warning("Insufficient data for insight generation")
            return []
        
        logger.info(f"Generating insights from {len(documents)} documents")
        
        try:
            # Map document IDs to their data for easier access
            doc_map = {doc.original_id: doc for doc in documents}
            sent_map = {s.document_id: s for s in sentiment_results}
            cat_map = {c.document_id: c for c in categorization_results}
            
            # Generate different types of insights
            insights = []
            
            # 1. Sentiment-based insights
            sentiment_insights = await self._generate_sentiment_insights(
                doc_map, sent_map, cat_map
            )
            insights.extend(sentiment_insights)
            
            # 2. Category-based insights
            category_insights = await self._generate_category_insights(
                doc_map, sent_map, cat_map
            )
            insights.extend(category_insights)
            
            # 3. Temporal insights
            temporal_insights = await self._generate_temporal_insights(
                doc_map, sent_map, cat_map
            )
            insights.extend(temporal_insights)
            
            # 4. Content-based insights
            content_insights = await self._generate_content_insights(
                doc_map, sent_map, cat_map
            )
            insights.extend(content_insights)
            
            # 5. Cross-cutting insights
            cross_cutting_insights = await self._generate_cross_cutting_insights(
                doc_map, sent_map, cat_map, insights
            )
            insights.extend(cross_cutting_insights)
            
            # Filter insights by confidence and uniqueness
            unique_insights = self._filter_unique_insights(insights)
            
            logger.info(f"Generated {len(unique_insights)} unique insights")
            return unique_insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return []
    
    async def _generate_sentiment_insights(
        self,
        doc_map: Dict[str, CleanedDocument],
        sent_map: Dict[str, SentimentAnalysis],
        cat_map: Dict[str, CategoryResult]
    ) -> List[InsightData]:
        """Generate insights based on sentiment analysis"""
        
        insights = []
        
        # 1. Overall sentiment distribution
        sentiment_counts = defaultdict(int)
        for sent in sent_map.values():
            sentiment_counts[sent.overall_sentiment] += 1
        
        total = sum(sentiment_counts.values())
        if total > 0:
            positive_ratio = sentiment_counts.get(SentimentType.POSITIVE, 0) / total
            negative_ratio = sentiment_counts.get(SentimentType.NEGATIVE, 0) / total
            neutral_ratio = sentiment_counts.get(SentimentType.NEUTRAL, 0) / total
            
            if negative_ratio > 0.5:
                insights.append(InsightData(
                    insight_type='sentiment_shift',
                    description=f"Negative sentiment is dominant in {negative_ratio*100:.1f}% of feedback",
                    supporting_evidence=[
                        f"{sentiment_counts[SentimentType.NEGATIVE]} out of {total} feedback items are negative",
                        f"Positive feedback ratio: {positive_ratio*100:.1f}%"
                    ],
                    frequency=int(negative_ratio * 100),  # As percentage
                    severity='high' if negative_ratio > 0.6 else 'medium',
                    trend_direction='increasing' if negative_ratio > 0.4 else 'stable',
                    affected_areas=[cat.primary_category.value for cat in cat_map.values()]
                ))
            
            if positive_ratio > 0.6:
                insights.append(InsightData(
                    insight_type='success_story',
                    description=f"Positive sentiment is strong with {positive_ratio*100:.1f}% of feedback being positive",
                    supporting_evidence=[
                        f"{sentiment_counts[SentimentType.POSITIVE]} out of {total} feedback items are positive",
                        f"Negative feedback ratio: {negative_ratio*100:.1f}%"
                    ],
                    frequency=int(positive_ratio * 100),
                    severity='low',
                    trend_direction='increasing' if positive_ratio > 0.5 else 'stable',
                    affected_areas=[cat.primary_category.value for cat in cat_map.values()]
                ))
        
        # 2. Sentiment by category
        category_sentiments = defaultdict(lambda: defaultdict(int))
        for doc_id, cat in cat_map.items():
            if doc_id in sent_map:
                sentiment = sent_map[doc_id].overall_sentiment
                category_sentiments[cat.primary_category][sentiment] += 1
        
        for category, sentiments in category_sentiments.items():
            total = sum(sentiments.values())
            if total >= self.min_insight_support:
                sentiment_dist = {k.value: v/total for k, v in sentiments.items()}
                
                # Check for strong sentiment in a category
                for sentiment, count in sentiments.items():
                    ratio = count / total
                    if ratio > 0.6:  # Strong sentiment in this category
                        insights.append(InsightData(
                            insight_type='sentiment_shift',
                            description=f"{sentiment.value.capitalize()} sentiment is particularly strong in the '{category.value}' category ({ratio*100:.1f}% of feedback)",
                            supporting_evidence=[
                                f"{count} out of {total} items in this category are {sentiment.value}",
                                f"Overall sentiment distribution: {sentiment_dist}"
                            ],
                            frequency=count,
                            severity='high' if ratio > 0.7 else 'medium',
                            trend_direction='increasing' if ratio > 0.5 else 'stable',
                            affected_areas=[category.value]
                        ))
        
        return insights
    
    async def _generate_category_insights(
        self,
        doc_map: Dict[str, CleanedDocument],
        sent_map: Dict[str, SentimentAnalysis],
        cat_map: Dict[str, CategoryResult]
    ) -> List[InsightData]:
        """Generate insights based on category analysis"""
        
        insights = []
        
        # 1. Most common categories
        category_counts = defaultdict(int)
        for cat in cat_map.values():
            category_counts[cat.primary_category] += 1
        
        if category_counts:
            total = sum(category_counts.values())
            sorted_categories = sorted(
                category_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Top categories insight
            top_category, top_count = sorted_categories[0]
            top_ratio = top_count / total
            
            if top_ratio > 0.3:  # If top category is significantly represented
                insights.append(InsightData(
                    insight_type='trend',
                    description=f"The most common feedback category is '{top_category.value}' ({top_ratio*100:.1f}% of all feedback)",
                    supporting_evidence=[
                        f"{top_count} out of {total} feedback items are in this category",
                        f"Top 3 categories: {', '.join([f'{cat.value} ({count/total*100:.1f}%)' for cat, count in sorted_categories[:3]])}"
                    ],
                    frequency=top_count,
                    severity='medium',
                    trend_direction='increasing' if top_ratio > 0.4 else 'stable',
                    affected_areas=[top_category.value]
                ))
            
            # Category distribution insight
            if len(category_counts) >= 3:
                diversity_index = len([v for v in category_counts.values() if v/total >= 0.1])
                if diversity_index >= 3:
                    insights.append(InsightData(
                        insight_type='pattern',
                        description=f"Feedback is distributed across {diversity_index} major categories, indicating diverse concerns",
                        supporting_evidence=[
                            f"Categories with ≥10% of feedback: {diversity_index}",
                            f"Category distribution: {', '.join([f'{cat.value}: {count/total*100:.1f}%' for cat, count in sorted_categories])}"
                        ],
                        frequency=diversity_index,
                        severity='low',
                        trend_direction='stable',
                        affected_areas=[cat.value for cat in category_counts.keys()]
                    ))
        
        # 2. Sentiment by category correlations
        category_sentiments = defaultdict(list)
        for doc_id, sent in sent_map.items():
            if doc_id in cat_map:
                category = cat_map[doc_id].primary_category
                category_sentiments[category].append(sent.sentiment_score)
        
        for category, scores in category_sentiments.items():
            if len(scores) >= self.min_insight_support:
                avg_score = sum(scores) / len(scores)
                if abs(avg_score) >= self.min_sentiment_impact:
                    sentiment_type = 'positive' if avg_score > 0 else 'negative'
                    insights.append(InsightData(
                        insight_type='sentiment_shift',
                        description=f"Feedback in the '{category.value}' category shows {sentiment_type} sentiment on average",
                        supporting_evidence=[
                            f"Average sentiment score: {avg_score:.2f} (range: -1 to 1)",
                            f"Based on {len(scores)} feedback items in this category"
                        ],
                        frequency=len(scores),
                        severity='high' if abs(avg_score) > 0.5 else 'medium',
                        trend_direction='increasing' if abs(avg_score) > 0.4 else 'stable',
                        affected_areas=[category.value]
                    ))
        
        return insights
    
    async def _generate_temporal_insights(
        self,
        doc_map: Dict[str, CleanedDocument],
        sent_map: Dict[str, SentimentAnalysis],
        cat_map: Dict[str, CategoryResult]
    ) -> List[InsightData]:
        """Generate insights based on temporal patterns"""
        
        insights = []
        
        # Extract timestamps and categorize by time periods
        # Note: This assumes documents have timestamps in their metadata
        # For this example, we'll simulate temporal data
        
        # Simulate time-based analysis (in a real implementation, use actual timestamps)
        current_time = datetime.now()
        time_windows = {
            'last_week': (current_time - timedelta(days=7), current_time),
            'last_month': (current_time - timedelta(days=30), current_time)
        }
        
        # Count documents in each time window
        window_counts = {window: 0 for window in time_windows}
        
        # In a real implementation, you would filter documents by their timestamp
        # For now, we'll simulate some temporal patterns
        total_docs = len(doc_map)
        if total_docs > 0:
            # Simulate 40% of documents in the last week
            window_counts['last_week'] = int(total_docs * 0.4)
            window_counts['last_month'] = total_docs  # All documents in the last month
            
            # Check for recent increase in feedback volume
            weekly_ratio = window_counts['last_week'] / (window_counts['last_month'] - window_counts['last_week'] + 1)
            
            if weekly_ratio > 0.5:  # More than 50% of monthly feedback in the last week
                insights.append(InsightData(
                    insight_type='trend',
                    description=f"Significant increase in feedback volume in the last week ({window_counts['last_week']} items)",
                    supporting_evidence=[
                        f"{window_counts['last_week']} feedback items in the last week",
                        f"{window_counts['last_month']} items in the last month"
                    ],
                    frequency=window_counts['last_week'],
                    severity='high' if weekly_ratio > 1.0 else 'medium',
                    trend_direction='increasing',
                    affected_areas=['All categories']
                ))
        
        return insights
    
    async def _generate_content_insights(
        self,
        doc_map: Dict[str, CleanedDocument],
        sent_map: Dict[str, SentimentAnalysis],
        cat_map: Dict[str, CategoryResult]
    ) -> List[InsightData]:
        """Generate insights by analyzing content patterns"""
        
        insights = []
        
        # 1. Common phrases and terms
        all_terms = []
        for doc in doc_map.values():
            # Simple term extraction (in a real implementation, use NLP techniques)
            terms = re.findall(r'\b\w{4,}\b', doc.cleaned_content.lower())
            all_terms.extend(terms)
        
        term_freq = Counter(all_terms)
        common_terms = term_freq.most_common(10)
        
        # 2. Frequent issues or requests
        issue_indicators = ['issue', 'problem', 'error', 'bug', 'fix', 'broken', 'not working']
        issue_docs = []
        
        for doc_id, doc in doc_map.items():
            if any(indicator in doc.cleaned_content.lower() for indicator in issue_indicators):
                issue_docs.append(doc_id)
        
        if len(issue_docs) >= self.min_insight_support:
            issue_categories = [cat_map[doc_id].primary_category for doc_id in issue_docs if doc_id in cat_map]
            if issue_categories:
                most_common_category = Counter(issue_categories).most_common(1)[0]
                
                insights.append(InsightData(
                    insight_type='frequent_issue',
                    description=f"Identified {len(issue_docs)} documents mentioning issues, primarily in the '{most_common_category[0].value}' category",
                    supporting_evidence=[
                        f"{most_common_category[1]} issues in '{most_common_category[0].value}' category",
                        f"Common issue indicators: {', '.join(issue_indicators[:3])}"
                    ],
                    frequency=len(issue_docs),
                    severity='high' if len(issue_docs) > 10 else 'medium',
                    trend_direction='increasing' if len(issue_docs) > 5 else 'stable',
                    affected_areas=[cat.value for cat, _ in Counter(issue_categories).most_common(3)]
                ))
        
        # 3. Content length analysis
        doc_lengths = [len(doc.cleaned_content.split()) for doc in doc_map.values()]
        if doc_lengths:
            avg_length = sum(doc_lengths) / len(doc_lengths)
            
            if avg_length < 50:
                insights.append(InsightData(
                    insight_type='feedback_quality',
                    description="Feedback items are relatively short, which may indicate lack of detail",
                    supporting_evidence=[
                        f"Average feedback length: {avg_length:.1f} words",
                        f"Total feedback items analyzed: {len(doc_lengths)}"
                    ],
                    frequency=len([l for l in doc_lengths if l < 50]),
                    severity='low',
                    trend_direction='stable',
                    affected_areas=['Feedback quality']
                ))
        
        return insights
    
    async def _generate_cross_cutting_insights(
        self,
        doc_map: Dict[str, CleanedDocument],
        sent_map: Dict[str, SentimentAnalysis],
        cat_map: Dict[str, CategoryResult],
        existing_insights: List[InsightData]
    ) -> List[InsightData]:
        """Generate insights that cut across multiple dimensions"""
        
        insights = []
        
        # 1. Correlate sentiment with categories
        category_sentiments = defaultdict(list)
        for doc_id, sent in sent_map.items():
            if doc_id in cat_map:
                category = cat_map[doc_id].primary_category
                category_sentiments[category].append(sent.sentiment_score)
        
        # Find categories with strongest negative sentiment
        negative_categories = []
        for category, scores in category_sentiments.items():
            if len(scores) >= self.min_insight_support:
                avg_score = sum(scores) / len(scores)
                if avg_score < -self.min_sentiment_impact:
                    negative_categories.append((category, avg_score, len(scores)))
        
        # Sort by most negative
        negative_categories.sort(key=lambda x: x[1])
        
        for category, score, count in negative_categories[:3]:  # Top 3 most negative
            insights.append(InsightData(
                insight_type='improvement_area',
                description=f"The '{category.value}' category shows consistently negative sentiment (avg score: {score:.2f})",
                supporting_evidence=[
                    f"Based on {count} feedback items in this category",
                    f"Average sentiment score: {score:.2f} (range: -1 to 1)"
                ],
                frequency=count,
                severity='high' if score < -0.5 else 'medium',
                trend_direction='decreasing' if score < -0.3 else 'stable',
                affected_areas=[category.value]
            ))
        
        # 2. Emerging topics (terms that appear in recent feedback)
        # In a real implementation, compare current terms with historical data
        # For now, we'll just look for less common terms that appear multiple times
        all_terms = []
        for doc in doc_map.values():
            terms = re.findall(r'\b\w{5,}\b', doc.cleaned_content.lower())
            all_terms.extend(terms)
        
        term_freq = Counter(all_terms)
        emerging_terms = [
            term for term, count in term_freq.items() 
            if 2 <= count <= 5  # Terms that appear a few times
        ]
        
        if emerging_terms:
            insights.append(InsightData(
                insight_type='emerging_topic',
                description=f"Potential emerging topics detected in feedback",
                supporting_evidence=[
                    f"Terms appearing multiple times: {', '.join(emerging_terms[:5])}",
                    f"Total unique terms: {len(term_freq)}"
                ],
                frequency=len(emerging_terms),
                severity='low',
                trend_direction='increasing',
                affected_areas=['Content analysis']
            ))
        
        return insights
    
    def _filter_unique_insights(self, insights: List[InsightData]) -> List[InsightData]:
        """Filter and deduplicate insights"""
        
        # Group insights by type and description
        insight_groups = defaultdict(list)
        for insight in insights:
            key = (insight.insight_type, insight.description.split('(')[0].strip())
            insight_groups[key].append(insight)
        
        # Select the highest confidence insight from each group
        unique_insights = []
        for group in insight_groups.values():
            # Sort by confidence (descending)
            group.sort(key=lambda x: x.confidence if hasattr(x, 'confidence') else 0, reverse=True)
            unique_insights.append(group[0])
        
        # Sort all insights by severity and frequency
        unique_insights.sort(
            key=lambda x: (
                {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}.get(x.severity, 4),
                -x.frequency if hasattr(x, 'frequency') else 0
            )
        )
        
        return unique_insights
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'insight_types': list(self.insight_types.keys()),
            'min_insight_support': self.min_insight_support,
            'min_sentiment_impact': self.min_sentiment_impact
        }
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down {self.agent_id}")
