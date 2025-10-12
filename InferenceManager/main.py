"""
InferenceManager - Central Control Panel
Main entry point for running different types of AI inference operations.
Generic implementation that works with any type of structured JSON data.
"""

import os

from dotenv import load_dotenv

from config import (
    DATA_DESCRIPTION,
    DATA_LABEL,
    INFERENCE_METHOD,
    INPUT_FILE,
    OUTPUT_FILE,
    PROMPT_FILE,
    TASK_DESCRIPTION,
)
from runInferenceInBatches import run_batch_inference


def validate_environment() -> None:
    """Validate that required environment variables are set."""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OSError("OPENAI_API_KEY not set in environment or .env file")
    model = os.getenv("MODEL_NAME")
    if not model:
        raise OSError("model name  not specified")
    
    print("✅ Environment validation passed")


def validate_files() -> None:
    """Validate that required input files exist."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")
    
    if not PROMPT_FILE.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_FILE}")
    
    print("✅ File validation passed")


def run_inference() -> None:
    """Run inference based on the configured method."""
    print(f"🚀 Starting inference using method: {INFERENCE_METHOD}")
    print(f"📊 Processing {DATA_LABEL}: {DATA_DESCRIPTION}")
    print(f"🎯 Task: {TASK_DESCRIPTION}")
    
    if INFERENCE_METHOD == "batch":
        print("📦 Using batch processing method...")
        run_batch_inference(
            input_file=str(INPUT_FILE),
            output_file=str(OUTPUT_FILE),
            prompt_file=str(PROMPT_FILE)
        )
    elif INFERENCE_METHOD == "streaming":
        print("🌊 Streaming method not yet implemented")
        print("   Please use 'batch' method for now")
    elif INFERENCE_METHOD == "parallel":
        print("⚡ Parallel processing method not yet implemented")
        print("   Please use 'batch' method for now")
    else:
        raise ValueError(f"Unknown inference method: {INFERENCE_METHOD}")


def main() -> None:
    """Main control panel function."""
    print("🎛️  InferenceManager Control Panel")
    print("=" * 40)
    
    try:
        # Validate environment and files
        validate_environment()
        validate_files()
        
        # Run inference
        run_inference()
        
        print("\n✅ Inference completed successfully!")
        print(f"📁 Results saved to: {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check that your .env file contains OPENAI_API_KEY")
        print("   2. Ensure your input JSON file exists and has valid structure")
        print("   3. Verify the prompt template file exists")
        print("   4. Check your internet connection for API access")
        print(
            "   5. Ensure your JSON file contains a list of items or "
            "a dictionary with a data list"
        )


if __name__ == "__main__":
    main()
