"""
Main Application - Feedback Processing System
"""

import asyncio
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from workflow.workflow_manager import WorkflowManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FeedbackProcessingApp:
    """Main application class for the Feedback Processing System"""
    
    def __init__(self):
        self.workflow_manager = WorkflowManager()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the application and all components"""
        logger.info("Initializing Feedback Processing System...")
        
        try:
            await self.workflow_manager.initialize()
            self.initialized = True
            logger.info("Feedback Processing System initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            return False
    
    async def process_feedback_file(
        self, 
        file_path: str, 
        output_dir: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process feedback from a file"""
        if not self.initialized:
            return {"status": "error", "message": "Application not initialized"}
        
        try:
            # Read the input file
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    input_data = json.load(f)
                except json.JSONDecodeError:
                    # If not JSON, try reading as one document per line
                    f.seek(0)
                    input_data = [json.loads(line.strip()) for line in f if line.strip()]
            
            logger.info(f"Processing {len(input_data) if isinstance(input_data, list) else 1} feedback items from {file_path}")
            
            # Process the feedback
            result = await self.workflow_manager.process_feedback(input_data, task_id)
            
            # Save results if output directory is provided
            if output_dir:
                await self._save_results(result, output_dir)
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing feedback file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def process_feedback_data(
        self, 
        data: Any,
        output_dir: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process feedback data directly"""
        if not self.initialized:
            return {"status": "error", "message": "Application not initialized"}
        
        try:
            logger.info(f"Processing {len(data) if isinstance(data, list) else 1} feedback items")
            
            # Process the feedback
            result = await self.workflow_manager.process_feedback(data, task_id)
            
            # Save results if output directory is provided
            if output_dir:
                await self._save_results(result, output_dir)
            
            return result
            
        except Exception as e:
            error_msg = f"Error processing feedback data: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}
    
    async def _save_results(self, result: Dict[str, Any], output_dir: str) -> None:
        """Save processing results to files"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            task_id = result.get('task_id', 'results')
            
            # Save the full report
            report_path = os.path.join(output_dir, f"{task_id}_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            logger.info(f"Saved full report to {report_path}")
            
            # Save recommendations separately
            if 'report' in result and 'top_recommendations' in result['report']:
                recs_path = os.path.join(output_dir, f"{task_id}_recommendations.json")
                with open(recs_path, 'w', encoding='utf-8') as f:
                    json.dump(result['report']['top_recommendations'], f, indent=2, default=str)
                
                logger.info(f"Saved recommendations to {recs_path}")
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}", exc_info=True)
    
    async def shutdown(self):
        """Shutdown the application"""
        logger.info("Shutting down Feedback Processing System...")
        await self.workflow_manager.shutdown()
        logger.info("Feedback Processing System shut down successfully")


async def main():
    """Main entry point for the command-line interface"""
    parser = argparse.ArgumentParser(description="Feedback Processing System")
    parser.add_argument(
        "-i", "--input", 
        help="Input file or directory containing feedback data (JSON or JSONL)",
        required=True
    )
    parser.add_argument(
        "-o", "--output", 
        help="Output directory for results (default: ./output)",
        default="./output"
    )
    parser.add_argument(
        "-t", "--task-id", 
        help="Task ID for tracking (default: auto-generated)",
        default=None
    )
    parser.add_argument(
        "--debug", 
        help="Enable debug logging",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logger("feedback_processor", log_level=log_level)
    
    # Initialize the application
    app = FeedbackProcessingApp()
    if not await app.initialize():
        print("Failed to initialize the application", file=sys.stderr)
        return 1
    
    try:
        # Check if input is a file or directory
        input_path = Path(args.input)
        if input_path.is_file():
            # Process a single file
            result = await app.process_feedback_file(
                str(input_path),
                args.output,
                args.task_id
            )
            
            if result.get("status") == "success":
                print(f"\nProcessing completed successfully!")
                print(f"Task ID: {result.get('task_id')}")
                print(f"Documents processed: {result.get('processing_stats', {}).get('documents_processed', 0)}")
                print(f"Insights generated: {result.get('report', {}).get('summary', {}).get('total_insights', 0)}")
                print(f"Recommendations generated: {result.get('report', {}).get('summary', {}).get('total_recommendations', 0)}")
                print(f"Results saved to: {args.output}")
                return 0
            else:
                print(f"\nError: {result.get('message', 'Unknown error')}", file=sys.stderr)
                return 1
                
        elif input_path.is_dir():
            # Process all JSON/JSONL files in the directory
            processed = 0
            errors = 0
            
            # Find all JSON/JSONL files in the directory
            files = list(input_path.glob("*.json")) + list(input_path.glob("*.jsonl"))
            
            if not files:
                print(f"No JSON/JSONL files found in {args.input}", file=sys.stderr)
                return 1
            
            print(f"Found {len(files)} files to process...\n")
            
            for i, file_path in enumerate(files, 1):
                print(f"Processing file {i}/{len(files)}: {file_path.name}")
                
                task_id = f"{args.task_id}_{i}" if args.task_id else None
                
                result = await app.process_feedback_file(
                    str(file_path),
                    args.output,
                    task_id
                )
                
                if result.get("status") == "success":
                    print(f"  ✓ Success: {result.get('report', {}).get('summary', {}).get('documents_processed', 0)} documents, "
                          f"{result.get('report', {}).get('summary', {}).get('total_insights', 0)} insights, "
                          f"{result.get('report', {}).get('summary', {}).get('total_recommendations', 0)} recommendations")
                    processed += 1
                else:
                    print(f"  ✗ Error: {result.get('message', 'Unknown error')}")
                    errors += 1
            
            print(f"\nBatch processing complete!")
            print(f"Files processed successfully: {processed}")
            print(f"Files with errors: {errors}")
            print(f"Results saved to: {args.output}")
            return 0 if errors == 0 else 1
            
        else:
            print(f"Input path does not exist: {args.input}", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}", file=sys.stderr)
        return 1
    finally:
        await app.shutdown()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
