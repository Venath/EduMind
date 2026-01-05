#!/usr/bin/env python
"""
XAI Predictor Pipeline CLI
===========================
Command-line interface for running the ML pipeline.

Usage:
    python -m scripts.run_pipeline --step all
    python -m scripts.run_pipeline --step etl
    python -m scripts.run_pipeline --step train
    python -m scripts.run_pipeline --step validate
    
Example:
    # Run full pipeline
    python scripts/run_pipeline.py --step all
    
    # Only train (assumes ETL already done)
    python scripts/run_pipeline.py --step train
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import (
    DATA_DIR,
    PROCESSED_DATA_DIR,
    PROCESSED_DATA_FILENAME,
    ARTIFACTS_DIR,
    MODELS_DIR,
    VALIDATION_THRESHOLDS,
    get_processed_data_path,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_etl() -> bool:
    """
    Run the ETL pipeline to process OULAD data.
    
    Returns:
        True if successful, False otherwise.
    """
    logger.info("=" * 60)
    logger.info("STEP 1: ETL - Extract, Transform, Load")
    logger.info("=" * 60)
    
    try:
        from src.data.etl import run_etl as etl_process
        
        output_path = etl_process()
        
        if output_path and output_path.exists():
            logger.info(f"ETL completed successfully")
            logger.info(f"   Output: {output_path}")
            return True
        else:
            logger.error("ETL failed - output file not created")
            return False
            
    except Exception as e:
        logger.error(f"ETL failed with error: {e}")
        return False


def run_train() -> bool:
    """
    Run model training.
    
    Returns:
        True if successful, False otherwise.
    """
    logger.info("=" * 60)
    logger.info("STEP 2: TRAIN - Model Training")
    logger.info("=" * 60)
    
    try:
        from src.models.trainer import Trainer
        
        # Ensure output directory exists
        output_dir = MODELS_DIR  # Use artifacts/models/ (recommended)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find processed data using config helper
        data_path = get_processed_data_path(use_legacy=True)
        
        if not data_path.exists():
            logger.error(f"Processed data not found at {data_path}. Run ETL first.")
            return False
        
        logger.info(f"   Using data: {data_path}")
        logger.info(f"   Output dir: {output_dir}")
        
        # Train model
        trainer = Trainer()
        trainer.load_data(data_path)
        trainer.train()
        metrics = trainer.evaluate()
        trainer.save(output_dir=output_dir)
        
        logger.info(f"Training completed successfully")
        logger.info(f"   Accuracy: {metrics['accuracy']:.2%}")
        logger.info(f"   F1 Score: {metrics['f1']:.2%}")
        
        return True
        
    except Exception as e:
        logger.error(f"Training failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_validate() -> bool:
    """
    Validate the trained model meets quality thresholds.
    
    Returns:
        True if validation passes, False otherwise.
    """
    logger.info("=" * 60)
    logger.info("STEP 3: VALIDATE - Model Validation")
    logger.info("=" * 60)
    
    try:
        import json
        
        # Load metadata
        metadata_path = MODELS_DIR / "model_metadata.json"
        if not metadata_path.exists():
            logger.error("Model metadata not found. Train model first.")
            return False
        
        with open(metadata_path) as f:
            metadata = json.load(f)
        
        # Get metrics
        metrics = metadata.get("metrics", {})
        
        if not metrics:
            logger.error("No metrics found in metadata")
            return False
        
        # Check thresholds
        accuracy = metrics.get("accuracy", 0)
        f1 = metrics.get("f1", 0)
        
        min_accuracy = VALIDATION_THRESHOLDS["min_accuracy"]
        min_f1 = VALIDATION_THRESHOLDS["min_f1"]
        
        passed = True
        
        if accuracy >= min_accuracy:
            logger.info(f"Accuracy: {accuracy:.2%} >= {min_accuracy:.2%}")
        else:
            logger.error(f"Accuracy: {accuracy:.2%} < {min_accuracy:.2%}")
            passed = False
        
        if f1 >= min_f1:
            logger.info(f"F1 Score: {f1:.2%} >= {min_f1:.2%}")
        else:
            logger.error(f"F1 Score: {f1:.2%} < {min_f1:.2%}")
            passed = False
        
        # Additional checks
        if metadata.get("total_samples", 0) > 1000:
            logger.info(f"Sample size: {metadata['total_samples']} samples")
        else:
            logger.warning(f"Small sample size: {metadata.get('total_samples', 0)}")
        
        if passed:
            logger.info("All validation checks passed")
        else:
            logger.error("Validation failed")
        
        return passed
        
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="XAI Predictor ML Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.run_pipeline --step all      # Run full pipeline
  python -m scripts.run_pipeline --step etl      # Only ETL
  python -m scripts.run_pipeline --step train    # Only training
  python -m scripts.run_pipeline --step validate # Only validation
        """
    )
    
    parser.add_argument(
        "--step",
        choices=["etl", "train", "validate", "all"],
        default="all",
        help="Pipeline step to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"XAI Predictor Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Project Root: {PROJECT_ROOT}")
    logger.info(f"Step: {args.step}")
    logger.info("")
    
    success = True
    
    if args.step in ["etl", "all"]:
        success = run_etl() and success
    
    if args.step in ["train", "all"]:
        success = run_train() and success
    
    if args.step in ["validate", "all"]:
        success = run_validate() and success
    
    logger.info("")
    if success:
        logger.info("Pipeline completed successfully!")
        sys.exit(0)
    else:
        logger.error("Pipeline failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
