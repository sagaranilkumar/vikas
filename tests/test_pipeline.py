"""
Test Script for Feedback Processing Pipeline
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import uuid

from app import FeedbackProcessingApp

# Sample data for generating test feedback
TECHNICAL_ISSUES = [
    "The application crashes when submitting the form.",
    "Slow response time when loading large datasets.",
    "Error 500 when accessing the dashboard.",
    "Login fails with incorrect error message.",
    "File upload fails for files larger than 10MB.",
    "Search functionality returns irrelevant results.",
    "Mobile app freezes on Android devices.",
    "Notification emails not being sent.",
    "Data loss after session timeout.",
    "Incorrect calculations in the reporting module."
]

PROCEDURAL_ISSUES = [
    "The approval process takes too many steps.",
    "No clear documentation for the API.",
    "Difficult to find the export feature.",
    "Confusing error messages.",
    "No confirmation before deleting items.",
    "The workflow is not intuitive.",
    "Missing undo functionality.",
    "Too many clicks to complete common tasks.",
    "No way to customize the dashboard.",
    "Inconsistent navigation between sections."
]

POSITIVE_FEEDBACK = [
    "Great user interface, very intuitive!",
    "The new search feature works perfectly.",
    "Excellent customer support, issue was resolved quickly.",
    "The mobile app is very responsive.",
    "The reporting features are very comprehensive.",
    "The onboarding process was smooth and easy.",
    "The performance has improved significantly.",
    "The documentation is clear and helpful.",
    "The new dark mode is easy on the eyes.",
    "The export to PDF feature works great."
]

USERS = [
    {"id": "user1", "name": "John Doe", "email": "john@example.com"},
    {"id": "user2", "name": "Jane Smith", "email": "jane@example.com"},
    {"id": "user3", "name": "Bob Johnson", "email": "bob@example.com"},
    {"id": "user4", "name": "Alice Brown", "email": "alice@example.com"},
    {"id": "user5", "name": "Charlie Wilson", "email": "charlie@example.com"}
]

def generate_test_data(num_items: int = 100) -> List[Dict[str, Any]]:
    """Generate test feedback data"""
    feedback_items = []
    
    # Generate timestamps over the last 30 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    
    for i in range(num_items):
        # Randomly select feedback type
        feedback_type = random.choice(['technical', 'procedural', 'positive'])
        
        if feedback_type == 'technical':
            content = random.choice(TECHNICAL_ISSUES)
            sentiment = 'NEGATIVE'
            category = 'TECHNICAL_ISSUES'
        elif feedback_type == 'procedural':
            content = random.choice(PROCEDURAL_ISSUES)
            sentiment = random.choice(['NEGATIVE', 'NEUTRAL'])
            category = 'PROCEDURAL_INEFFICIENCIES'
        else:  # positive
            content = random.choice(POSITIVE_FEEDBACK)
            sentiment = 'POSITIVE'
            category = 'USER_EXPERIENCE'
        
        # Random timestamp within the last 30 days
        random_days = random.uniform(0, 30)
        timestamp = (end_time - timedelta(days=random_days)).isoformat()
        
        # Random user
        user = random.choice(USERS)
        
        feedback = {
            "id": str(uuid.uuid4()),
            "content": content,
            "timestamp": timestamp,
            "user": user,
            "metadata": {
                "source": "test",
                "version": "1.0.0",
                "category": category,
                "sentiment": sentiment,
                "tags": ["test", f"type_{feedback_type}"]
            }
        }
        
        feedback_items.append(feedback)
    
    return feedback_items

async def run_test(num_items: int = 100, output_dir: str = "./test_output"):
    """Run the test with the specified number of items"""
    print(f"Generating {num_items} test feedback items...")
    test_data = generate_test_data(num_items)
    
    # Save test data to file
    test_data_file = Path(output_dir) / "test_data.json"
    test_data_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(test_data_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"Test data saved to {test_data_file}")
    
    # Initialize the application
    print("Initializing the application...")
    app = FeedbackProcessingApp()
    if not await app.initialize():
        print("Failed to initialize the application")
        return
    
    # Process the test data
    print(f"Processing {len(test_data)} feedback items...")
    start_time = datetime.now()
    
    result = await app.process_feedback_data(
        data=test_data,
        output_dir=output_dir,
        task_id=f"test_run_{start_time.strftime('%Y%m%d_%H%M%S')}"
    )
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print("\nTest completed!")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Items per second: {num_items / processing_time:.2f}")
    
    if result.get('status') == 'success':
        report_path = result.get('report_path', 'Unknown')
        print(f"\nReport generated: {report_path}")
        
        # Print summary
        print("\nSummary:")
        print(f"- Documents processed: {result.get('report', {}).get('summary', {}).get('document_count', 0)}")
        print(f"- Insights generated: {result.get('report', {}).get('summary', {}).get('total_insights', 0)}")
        print(f"- Recommendations: {result.get('report', {}).get('summary', {}).get('total_recommendations', 0)}")
    else:
        print(f"\nError: {result.get('message', 'Unknown error')}")
    
    # Shutdown the application
    await app.shutdown()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the feedback processing pipeline")
    parser.add_argument(
        "-n", "--num-items", 
        type=int, 
        default=100,
        help="Number of test feedback items to generate (default: 100)"
    )
    parser.add_argument(
        "-o", "--output-dir", 
        default="./test_output",
        help="Output directory for test results (default: ./test_output)"
    )
    
    args = parser.parse_args()
    
    # Run the test
    asyncio.run(run_test(
        num_items=args.num_items,
        output_dir=args.output_dir
    ))
