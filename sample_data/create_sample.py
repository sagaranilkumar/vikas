#!/usr/bin/env python3
"""
Simple script to generate sample.jsonl with realistic specialist feedback data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_feedback import generate_feedback_file

if __name__ == "__main__":
    print("Creating sample.jsonl with specialist feedback data...")
    
    # Generate 50 realistic specialist feedback items
    output_path = generate_feedback_file(num_items=50, output_file="sample.jsonl")
    
    print("Sample data created successfully!")
    print(f"You can now use {output_path} for testing the pipeline.")
