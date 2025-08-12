"""
Recommendation Agent - Generates actionable recommendations based on insights
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter

from models.feedback_models import (
    InsightData, Recommendation, FeedbackCategory, SentimentType
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

class RecommendationAgent:
    """
    Recommendation Agent responsible for generating actionable recommendations
    based on insights from feedback analysis.
    """
    
    def __init__(self):
        self.agent_id = "recommendation_agent"
        
        # Recommendation templates by insight type
        self.recommendation_templates = {
            'trend': {
                'title': "Address the {trend_direction} trend in {category}",
                'description': (
                    "The analysis shows a {trend_direction} trend in {category} feedback. "
                    "{action} to {objective}."
                ),
                'priority_map': {
                    'increasing': 'high',
                    'decreasing': 'medium',
                    'stable': 'low'
                },
                'effort_map': {
                    'high': 'high',
                    'medium': 'medium',
                    'low': 'low'
                }
            },
            'pattern': {
                'title': "Address the pattern of {pattern_type} in {category}",
                'description': (
                    "A consistent pattern of {pattern_type} has been identified in {category} feedback. "
                    "Consider {action} to {objective}."
                ),
                'priority': 'medium',
                'effort': 'medium'
            },
            'anomaly': {
                'title': "Investigate anomaly in {category}",
                'description': (
                    "An anomaly has been detected in {category} feedback. "
                    "{action} to {objective}."
                ),
                'priority': 'high',
                'effort': 'high'
            },
            'correlation': {
                'title': "Address correlation between {category1} and {category2}",
                'description': (
                    "A correlation has been identified between {category1} and {category2}. "
                    "Consider {action} to {objective}."
                ),
                'priority': 'medium',
                'effort': 'medium'
            },
            'sentiment_shift': {
                'title': "Address {sentiment} sentiment in {category}",
                'description': (
                    "{sentiment_capitalized} sentiment has been identified in {category} feedback. "
                    "{action} to {objective}."
                ),
                'priority_map': {
                    'positive': 'low',
                    'negative': 'high',
                    'neutral': 'medium'
                },
                'effort_map': {
                    'positive': 'low',
                    'negative': 'high',
                    'neutral': 'medium'
                }
            },
            'emerging_topic': {
                'title': "Address emerging topic: {topic}",
                'description': (
                    "An emerging topic '{topic}' has been identified in the feedback. "
                    "Consider {action} to {objective}."
                ),
                'priority': 'medium',
                'effort': 'medium'
            },
            'frequent_issue': {
                'title': "Resolve frequent issue in {category}",
                'description': (
                    "A frequent issue has been reported in {category}. "
                    "{action} to {objective}."
                ),
                'priority': 'high',
                'effort': 'high'
            },
            'improvement_area': {
                'title': "Improve {area} in {category}",
                'description': (
                    "An area for improvement has been identified in {category} related to {area}. "
                    "{action} to {objective}."
                ),
                'priority': 'medium',
                'effort': 'medium'
            },
            'success_story': {
                'title': "Leverage success in {category}",
                'description': (
                    "Positive outcomes have been reported in {category}. "
                    "Consider {action} to {objective}."
                ),
                'priority': 'low',
                'effort': 'low'
            },
            'feedback_quality': {
                'title': "Improve feedback quality in {category}",
                'description': (
                    "Opportunities to improve feedback quality have been identified in {category}. "
                    "{action} to {objective}."
                ),
                'priority': 'low',
                'effort': 'medium'
            }
        }
        
        # Action templates by category and sentiment
        self.action_templates = {
            FeedbackCategory.TECHNICAL_ISSUES: {
                'positive': [
                    ("document and share", "leverage this success in other areas"),
                    ("recognize the team", "acknowledge their contribution"),
                    ("analyze the success factors", "replicate them elsewhere")
                ],
                'negative': [
                    ("investigate the root cause", "prevent recurrence"),
                    ("prioritize bug fixes", "address the most critical issues first"),
                    ("improve testing procedures", "catch issues earlier")
                ],
                'neutral': [
                    ("monitor the situation", "identify any emerging patterns"),
                    ("gather more data", "better understand the context"),
                    ("review documentation", "ensure clarity and completeness")
                ]
            },
            FeedbackCategory.PROCEDURAL_INEFFICIENCIES: {
                'positive': [
                    ("document the process", "share best practices"),
                    ("recognize the team", "acknowledge their efficiency"),
                    ("consider automation", "further improve productivity")
                ],
                'negative': [
                    ("streamline the process", "reduce inefficiencies"),
                    ("review and update procedures", "align with current needs"),
                    ("provide additional training", "ensure proper implementation")
                ],
                'neutral': [
                    ("analyze the process", "identify potential improvements"),
                    ("gather more feedback", "understand pain points"),
                    ("benchmark against industry standards", "identify gaps")
                ]
            },
            # Add more categories as needed
        }
        
        # Default actions if no specific match is found
        self.default_actions = {
            'positive': [
                ("leverage this success", "reinforce positive outcomes"),
                ("recognize the team", "acknowledge their contribution"),
                ("document best practices", "share knowledge across teams")
            ],
            'negative': [
                ("investigate the issue", "understand the root cause"),
                ("develop an action plan", "address the concerns"),
                ("communicate with stakeholders", "keep them informed")
            ],
            'neutral': [
                ("monitor the situation", "identify emerging trends"),
                ("gather more information", "better understand the context"),
                ("review related processes", "ensure consistency")
            ]
        }
        
    async def initialize(self):
        """Initialize the recommendation agent"""
        logger.info(f"Initializing {self.agent_id}")
        # In a real implementation, you might load recommendation models here
        
    async def generate_recommendations(
        self, 
        input_data: Dict[str, Any]
    ) -> List[Recommendation]:
        """
        Generate recommendations based on insights
        """
        insights = input_data.get('insights', [])
        
        if not insights:
            logger.warning("No insights provided for recommendation generation")
            return []
        
        logger.info(f"Generating recommendations from {len(insights)} insights")
        
        try:
            recommendations = []
            
            # Process each insight and generate recommendations
            for insight in insights:
                try:
                    insight_recommendations = await self._generate_insight_recommendations(insight)
                    recommendations.extend(insight_recommendations)
                except Exception as e:
                    logger.error(f"Error generating recommendations for insight: {str(e)}")
                    continue
            
            # Filter and prioritize recommendations
            filtered_recommendations = self._filter_recommendations(recommendations)
            
            logger.info(f"Generated {len(filtered_recommendations)} recommendations")
            return filtered_recommendations
            
        except Exception as e:
            logger.error(f"Error in generate_recommendations: {str(e)}")
            return []
    
    async def _generate_insight_recommendations(
        self, 
        insight: InsightData
    ) -> List[Recommendation]:
        """Generate recommendations for a single insight"""
        
        recommendations = []
        
        # Get the appropriate template based on insight type
        template = self.recommendation_templates.get(
            insight.insight_type,
            self.recommendation_templates['trend']  # Default to trend template
        )
        
        # Determine recommendation parameters
        params = self._get_recommendation_params(insight)
        
        # Generate recommendations based on the number of affected areas
        affected_areas = insight.affected_areas or ['general']
        
        for area in affected_areas[:3]:  # Limit to top 3 areas
            # Update params with area-specific information
            area_params = params.copy()
            area_params['category'] = area
            
            # Get actions specific to the category and sentiment
            actions = self._get_actions(insight, area)
            
            # Generate recommendations for each action
            for action, objective in actions:
                action_params = area_params.copy()
                action_params.update({
                    'action': action,
                    'objective': objective
                })
                
                # Format title and description
                try:
                    title = template['title'].format(**action_params)
                    description = template['description'].format(**action_params)
                except KeyError as e:
                    logger.warning(f"Error formatting recommendation: {str(e)}")
                    continue
                
                # Determine priority and effort
                priority = self._determine_priority(insight, template, action_params)
                effort = self._determine_effort(insight, template, action_params)
                
                # Create recommendation
                recommendation = Recommendation(
                    title=title,
                    description=description,
                    priority=priority,
                    category=insight.insight_type,
                    implementation_effort=effort,
                    expected_impact=priority,  # Same as priority for now
                    timeline=self._determine_timeline(priority, effort),
                    resources_required=self._determine_resources(priority, effort, area),
                    success_metrics=self._determine_success_metrics(insight, area),
                    related_insights=[insight.insight_type]
                )
                
                recommendations.append(recommendation)
        
        return recommendations
    
    def _get_recommendation_params(self, insight: InsightData) -> Dict[str, Any]:
        """Extract parameters for recommendation templates"""
        
        sentiment = getattr(insight, 'sentiment', 'neutral')
        params = {
            'category': insight.affected_areas[0] if insight.affected_areas else 'general',
            'trend_direction': getattr(insight, 'trend_direction', 'stable'),
            'sentiment': sentiment,
            'sentiment_capitalized': sentiment.capitalize() if isinstance(sentiment, str) else 'Neutral',
            'severity': getattr(insight, 'severity', 'medium'),
            'frequency': getattr(insight, 'frequency', 1),
            'area': insight.affected_areas[0] if insight.affected_areas else 'the identified area',
            'pattern_type': insight.insight_type.replace('_', ' ')  # Convert insight type to readable pattern type
        }
        
        # Add specific parameters based on insight type
        if insight.insight_type == 'correlation' and len(insight.affected_areas) >= 2:
            params.update({
                'category1': insight.affected_areas[0],
                'category2': insight.affected_areas[1]
            })
        elif insight.insight_type == 'emerging_topic':
            params['topic'] = insight.affected_areas[0] if insight.affected_areas else 'an emerging topic'
        elif insight.insight_type == 'pattern':
            # For pattern insights, try to extract more specific pattern type from description
            pattern_desc = insight.description.lower()
            if 'recurring' in pattern_desc or 'frequent' in pattern_desc:
                params['pattern_type'] = 'recurring issues'
            elif 'increasing' in pattern_desc or 'growing' in pattern_desc:
                params['pattern_type'] = 'increasing concerns'
            elif 'consistent' in pattern_desc:
                params['pattern_type'] = 'consistent feedback'
            else:
                params['pattern_type'] = 'identified patterns'
        
        return params
    
    def _get_actions(
        self, 
        insight: InsightData, 
        area: str
    ) -> List[Tuple[str, str]]:
        """Get appropriate actions for the insight and area"""
        
        # Determine the sentiment for action selection
        sentiment = 'neutral'
        if hasattr(insight, 'sentiment'):
            sentiment = insight.sentiment
        elif hasattr(insight, 'sentiment_score'):
            if insight.sentiment_score > 0.2:
                sentiment = 'positive'
            elif insight.sentiment_score < -0.2:
                sentiment = 'negative'
        
        # Try to get category-specific actions
        category = None
        for cat in FeedbackCategory:
            if cat.value.lower() in area.lower():
                category = cat
                break
        
        actions = []
        
        if category and category in self.action_templates:
            # Get category and sentiment specific actions
            category_actions = self.action_templates[category].get(
                sentiment,
                self.action_templates[category].get('neutral', [])
            )
            actions.extend(category_actions)
        
        # Add default actions if needed
        if len(actions) < 3:
            default_actions = self.default_actions.get(sentiment, [])
            actions.extend(default_actions)
        
        # Ensure we have at least one action
        if not actions:
            actions = [("take appropriate action", "address this issue")]
        
        return actions[:3]  # Return up to 3 actions
        
    def _determine_priority(
        self, 
        insight: InsightData, 
        template: Dict[str, Any],
        params: Dict[str, Any]
    ) -> str:
        """Determine recommendation priority"""
        
        # If template has a priority map, use it
        if 'priority_map' in template:
            if 'sentiment' in params and params['sentiment'] in template['priority_map']:
                return template['priority_map'][params['sentiment']]
            elif 'trend_direction' in params and params['trend_direction'] in template['priority_map']:
                return template['priority_map'][params['trend_direction']]
        
        # Default to template priority or 'medium'
        return template.get('priority', 'medium')
    
    def _determine_effort(
        self, 
        insight: InsightData, 
        template: Dict[str, Any],
        params: Dict[str, Any]
    ) -> str:
        """Determine implementation effort"""
        
        # If template has an effort map, use it
        if 'effort_map' in template:
            if 'sentiment' in params and params['sentiment'] in template['effort_map']:
                return template['effort_map'][params['sentiment']]
            elif 'trend_direction' in params and params['trend_direction'] in template['effort_map']:
                return template['effort_map'][params['trend_direction']]
        
        # Default to template effort or 'medium'
        return template.get('effort', 'medium')
    
    def _determine_timeline(self, priority: str, effort: str) -> str:
        """Estimate timeline based on priority and effort"""
        
        if priority == 'critical' or (priority == 'high' and effort == 'high'):
            return 'immediate'
        elif priority == 'high' or (priority == 'medium' and effort == 'high'):
            return 'short-term'
        elif priority == 'medium' or (priority == 'low' and effort == 'high'):
            return 'medium-term'
        else:
            return 'long-term'
    
    def _determine_resources(
        self, 
        priority: str, 
        effort: str, 
        area: str
    ) -> List[str]:
        """Determine required resources based on priority, effort, and area"""
        resources = []
        
        # Add resources based on priority
        if priority in ['high', 'critical']:
            resources.append('cross-functional team')
        
        # Add resources based on effort
        if effort == 'high':
            resources.extend(['dedicated development time', 'budget allocation'])
        elif effort == 'medium':
            resources.append('dedicated development time')
        
        # Add resources based on area
        if 'technical' in area.lower():
            resources.append('technical expertise')
        if 'process' in area.lower() or 'procedural' in area.lower():
            resources.append('process improvement team')
        
        # Ensure at least one resource
        if not resources:
            resources = ['standard team resources']
            
        return list(set(resources))  # Remove duplicates
    
    def _determine_success_metrics(
        self, 
        insight: InsightData, 
        area: str
    ) -> List[str]:
        """Determine appropriate success metrics for the recommendation"""
        metrics = []
        
        # Add metrics based on insight type
        if hasattr(insight, 'sentiment'):
            metrics.append(f"Improvement in {area} sentiment score")
        
        if insight.insight_type in ['frequent_issue', 'improvement_area']:
            metrics.append(f"Reduction in {area} related issues")
        
        if insight.insight_type == 'success_story':
            metrics.append(f"Replication of {area} success in other areas")
        
        # Add general metrics
        metrics.extend([
            f"Stakeholder satisfaction with {area} improvements",
            f"Time to resolution for {area} related items"
        ])
        
        return metrics[:3]  # Return up to 3 metrics
    
    def _filter_recommendations(
        self, 
        recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """Filter and deduplicate recommendations"""
        
        # Group similar recommendations
        recommendation_groups = defaultdict(list)
        for rec in recommendations:
            # Create a key based on title and description (first 20 chars)
            key = (
                rec.title.split(':')[0],  # Just the prefix before the first colon
                rec.description[:50] if rec.description else ''
            )
            recommendation_groups[key].append(rec)
        
        # Select the highest priority recommendation from each group
        filtered_recommendations = []
        for group in recommendation_groups.values():
            # Sort by priority (critical > high > medium > low)
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            group.sort(key=lambda x: priority_order.get(x.priority, 4))
            filtered_recommendations.append(group[0])
        
        # Sort all recommendations by priority and effort
        filtered_recommendations.sort(
            key=lambda x: (
                priority_order.get(x.priority, 4),
                0 if x.implementation_effort == 'high' else 
                1 if x.implementation_effort == 'medium' else 2
            )
        )
        
        return filtered_recommendations
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': 'active',
            'insight_types': list(self.recommendation_templates.keys()),
            'action_templates': list(self.action_templates.keys())
        }
    
    async def shutdown(self):
        """Shutdown the agent"""
        logger.info(f"Shutting down {self.agent_id}")
