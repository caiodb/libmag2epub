"""
Main entry point for the magazine automation pipeline.
Uses modular imports instead of subprocess calls.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.orchestrator import PipelineOrchestrator
from src.sent_manager import SentManager


async def main():
    """Run the full pipeline: scrape, build, mail, and archive."""
    python_exe = sys.executable
    
    print(f"{'='*60}")
    print(f"RUNNING FULL PIPELINE")
    print(f"Using Python: {python_exe}")
    print(f"{'='*60}")
    
    # STEP 1: Scrape & Build
    print("\n>>> STARTING STEP: SCRAPING AND BUILDING <<<")
    try:
        orchestrator = PipelineOrchestrator()
        await orchestrator.run()
        print(">>> SCRAPING AND BUILDING COMPLETED SUCCESSFULLY <<<\n")
    except Exception as e:
        print(f"!!! ERROR during SCRAPING AND BUILDING: {e} !!!")
        print("Pipeline aborted due to error.")
        return 1
    
    # STEP 2: Mail & Archive
    print("\n>>> STARTING STEP: MAILING & ARCHIVING <<<")
    try:
        manager = SentManager()
        manager.run()
        print(">>> MAILING & ARCHIVING COMPLETED SUCCESSFULLY <<<\n")
    except Exception as e:
        print(f"!!! ERROR during MAILING & ARCHIVING: {e} !!!")
        print("Pipeline aborted during mailing.")
        return 1
    
    print(f"{'='*60}")
    print(f"PIPELINE FINISHED SUCCESSFULLY")
    print(f"{'='*60}")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
