"""
Generate sample feedback data in JSONL format for testing the feedback processing system.
Creates realistic specialist feedback that matches the FeedbackDocument model format.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

# Specialist feedback sources
FEEDBACK_SOURCES = [
    "expert_report", "internal_assessment", "peer_review", 
    "technical_review", "process_evaluation", "quality_audit", "other"
]

# Technical and procedural feedback content
TECHNICAL_ISSUES = [
    "The system architecture shows significant performance bottlenecks in the data processing layer. Memory usage spikes to 85% during peak loads, requiring immediate optimization.",
    "Critical security vulnerability identified in the authentication module. SQL injection possible through user input validation gaps.",
    "Database query optimization needed - current response times exceed acceptable thresholds by 300% during concurrent operations.",
    "API endpoints lack proper error handling and return inconsistent response formats across different failure scenarios.",
    "The caching mechanism is ineffective, causing redundant database calls and degraded system performance.",
    "Integration with third-party services fails intermittently due to timeout configuration issues.",
    "Code quality analysis reveals high cyclomatic complexity in core business logic modules requiring refactoring."
]

PROCEDURAL_INEFFICIENCIES = [
    "The current approval workflow creates unnecessary delays, with documents sitting in queues for 5-7 business days on average.",
    "Documentation standards are inconsistent across teams, leading to knowledge transfer difficulties and onboarding delays.",
    "The testing protocol lacks comprehensive edge case coverage, resulting in production issues that could be prevented.",
    "Resource allocation process is manual and time-consuming, causing project delays and budget overruns.",
    "Communication channels between departments are fragmented, leading to duplicated efforts and missed dependencies.",
    "Quality assurance checkpoints are insufficient, allowing defects to propagate through the development lifecycle.",
    "Training programs are outdated and don't reflect current best practices or technology stack changes."
]

POSITIVE_OUTCOMES = [
    "The new automated deployment pipeline has reduced release cycle time by 60% while maintaining zero-defect deployments.",
    "Implementation of the monitoring dashboard has improved incident response time by 45% and enhanced system visibility.",
    "The refactored authentication system now handles 10x more concurrent users with improved security compliance.",
    "Process optimization in the data pipeline has increased throughput by 200% while reducing computational costs.",
    "The new documentation framework has improved developer onboarding time from 2 weeks to 3 days.",
    "Implementation of automated testing has increased code coverage to 95% and reduced production bugs by 80%.",
    "The redesigned user interface has improved user satisfaction scores by 40% and reduced support tickets by 30%."
]

IMPROVEMENT_SUGGESTIONS = [
    "Consider implementing microservices architecture to improve system scalability and maintainability.",
    "Recommend adopting infrastructure as code practices to ensure consistent environment deployments.",
    "Suggest implementing continuous integration/continuous deployment (CI/CD) pipeline for faster delivery cycles.",
    "Propose establishing service level objectives (SLOs) and monitoring to ensure system reliability.",
    "Recommend implementing automated security scanning in the development pipeline.",
    "Suggest adopting agile methodologies to improve project delivery and stakeholder communication.",
    "Propose implementing data governance framework to ensure data quality and compliance."
]

# Specialist roles and departments
SPECIALISTS = [
    {"name": "Dr. Sarah Chen", "role": "Senior Software Architect", "department": "Engineering"},
    {"name": "Michael Rodriguez", "role": "DevOps Lead", "department": "Infrastructure"},
    {"name": "Dr. Emily Watson", "role": "Data Science Manager", "department": "Analytics"},
    {"name": "James Thompson", "role": "Security Specialist", "department": "Cybersecurity"},
    {"name": "Lisa Park", "role": "Quality Assurance Director", "department": "QA"},
    {"name": "Robert Kim", "role": "Technical Project Manager", "department": "PMO"},
    {"name": "Dr. Amanda Foster", "role": "Research Lead", "department": "R&D"},
    {"name": "David Martinez", "role": "Systems Integration Specialist", "department": "IT"},
]

# Project and system identifiers
PROJECTS = [
    "PROJ-2024-001", "PROJ-2024-002", "PROJ-2024-003", "PROJ-2024-004",
    "SYS-UPGRADE-2024", "SECURITY-AUDIT-Q4", "PERFORMANCE-OPT-2024"
]

SYSTEMS = [
    "Customer Management System", "Data Analytics Platform", "E-commerce Portal",
    "Mobile Application Backend", "API Gateway", "Authentication Service",
    "Reporting Dashboard", "Integration Hub", "Monitoring System"
]

def generate_feedback_item():
    """Generate a single feedback item with realistic specialist data matching FeedbackDocument format."""
    # Generate a random timestamp within the last 60 days
    days_ago = random.randint(0, 60)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    timestamp = (datetime.now() - timedelta(
        days=days_ago, 
        hours=hours_ago, 
        minutes=minutes_ago
    )).isoformat()
    
    # Determine feedback category and content
    feedback_categories = [
        ("technical_issues", TECHNICAL_ISSUES),
        ("procedural_inefficiencies", PROCEDURAL_INEFFICIENCIES), 
        ("positive_outcomes", POSITIVE_OUTCOMES),
        ("improvement_suggestions", IMPROVEMENT_SUGGESTIONS)
    ]
    
    category, content_pool = random.choice(feedback_categories)
    content = random.choice(content_pool)
    
    # Select specialist and source
    specialist = random.choice(SPECIALISTS)
    source = random.choice(FEEDBACK_SOURCES)
    
    # Generate appropriate filename based on source and content
    date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y%m%d")
    
    filename_patterns = {
        "expert_report": f"expert_review_{date_str}_{random.choice(PROJECTS)}.txt",
        "internal_assessment": f"internal_assessment_{specialist['department'].lower()}_{date_str}.txt",
        "peer_review": f"peer_review_{random.choice(SYSTEMS).lower().replace(' ', '_')}_{date_str}.txt",
        "technical_review": f"technical_review_{random.choice(['security', 'performance', 'architecture'])}_{date_str}.txt",
        "process_evaluation": f"process_evaluation_{random.choice(['Q1', 'Q2', 'Q3', 'Q4'])}_2024.txt",
        "quality_audit": f"quality_audit_{random.choice(PROJECTS)}_{date_str}.txt",
        "other": f"feedback_{category}_{date_str}.txt"
    }
    
    filename = filename_patterns.get(source, f"feedback_{date_str}.txt")
    
    # Generate metadata based on category and source
    metadata = {
        "specialist": specialist["name"],
        "role": specialist["role"],
        "department": specialist["department"],
        "category": category,
        "priority": random.choice(["low", "medium", "high", "critical"]),
        "project_id": random.choice(PROJECTS),
        "system": random.choice(SYSTEMS)
    }
    
    # Add category-specific metadata
    if category == "technical_issues":
        metadata.update({
            "severity": random.choice(["minor", "major", "critical"]),
            "component": random.choice(["database", "api", "frontend", "backend", "infrastructure"]),
            "estimated_effort": f"{random.randint(1, 40)} hours"
        })
    elif category == "procedural_inefficiencies":
        metadata.update({
            "process_id": f"PROC-{random.randint(100, 999)}",
            "efficiency_impact": f"{random.randint(10, 50)}% delay",
            "affected_teams": random.randint(2, 8)
        })
    elif category == "positive_outcomes":
        metadata.update({
            "improvement_metric": f"{random.randint(20, 200)}% improvement",
            "measurement_period": random.choice(["1 month", "3 months", "6 months"]),
            "success_factor": random.choice(["automation", "optimization", "redesign", "training"])
        })
    elif category == "improvement_suggestions":
        metadata.update({
            "implementation_timeline": random.choice(["1-2 weeks", "1 month", "3 months", "6 months"]),
            "resource_requirement": random.choice(["low", "medium", "high"]),
            "expected_benefit": random.choice(["cost_reduction", "performance_improvement", "security_enhancement", "scalability"])
        })
    
    # Create the feedback document matching FeedbackDocument model
    feedback_document = {
        "id": f"fb{random.randint(1000, 9999)}",
        "filename": filename,
        "content": content,
        "content_type": "text/plain",
        "source": source,
        "timestamp": timestamp,
        "metadata": metadata
    }
    
    return feedback_document

def generate_feedback_file(num_items: int = 100, output_file: str = "sample.jsonl"):
    """Generate a JSONL file with sample feedback data matching FeedbackDocument format."""
    output_path = Path(__file__).parent / output_file
    
    print(f"Generating {num_items} specialist feedback items...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(num_items):
            feedback_item = generate_feedback_item()
            f.write(json.dumps(feedback_item, ensure_ascii=False) + '\n')
            
            # Progress indicator
            if (i + 1) % 20 == 0:
                print(f"Generated {i + 1}/{num_items} items...")
    
    print(f"Successfully generated {num_items} specialist feedback items in {output_path}")
    print(f"File location: {output_path.absolute()}")
    return str(output_path)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate sample feedback data in JSONL format")
    parser.add_argument(
        "-n", "--num-items", 
        type=int, 
        default=100,
        help="Number of feedback items to generate (default: 100)"
    )
    parser.add_argument(
        "-o", "--output", 
        default="sample_data/feedback.jsonl",
        help="Output file path (default: sample_data/feedback.jsonl)"
    )
    
    args = parser.parse_args()
    generate_feedback_file(args.num_items, args.output)
