#!/usr/bin/env python3
"""
Example usage script for InferenceManager.
This demonstrates how to use the system with custom data and prompts.
"""

from pathlib import Path

from config import BATCH_SIZE, DATA_LABEL
from utils import load_data_items, save_json_file


def create_custom_prompt(task_description: str) -> str:
    """Create a custom system prompt for different inference tasks."""
    return f"""You are an expert AI classifier.
Your task: {task_description}

Return your results as a JSON array of strings containing only the items that match your criteria.
"""


def process_with_custom_prompt(
    queries: list[dict], 
    system_prompt: str, 
    output_file: str,
    batch_size: int = BATCH_SIZE
) -> None:
    """
    Process queries with a custom prompt and save results.
    
    This is a simplified version that shows the concept.
    In practice, you'd use the full OpenAI client integration.
    """
    print(f"Processing {len(queries)} queries with custom prompt...")
    print(f"System prompt: {system_prompt[:100]}...")
    print(f"Batch size: {batch_size}")
    print(f"Output will be saved to: {output_file}")
    
    # This is where you'd integrate with OpenAI API
    # For now, we'll just save the original queries as an example
    results = queries[:5]  # Just take first 5 as example
    
    save_json_file({"queries": results}, Path(output_file))
    print(f"Example completed! Saved {len(results)} results to {output_file}")


def main() -> None:
    """Demonstrate different use cases."""
    print("🚀 InferenceManager Example Usage")
    print("=" * 50)
    
    # Example 1: Load sample data
    print("\n1. Loading sample data...")
    if Path("sample_queries.json").exists():
        queries = load_data_items(Path("sample_queries.json"), DATA_LABEL)
        print(f"   ✓ Loaded {len(queries)} queries from sample data")
    else:
        print("   ⚠ No sample data found")
        return
    
    # Example 2: Custom prompt for educational queries
    print("\n2. Creating custom prompt for educational queries...")
    educational_prompt = create_custom_prompt(
        "Extract queries that are clearly asking for educational information, "
        "definitions, explanations, or learning resources. "
        "Exclude queries about entertainment, shopping, or personal matters."
    )
    
    # Example 3: Process with custom prompt
    print("\n3. Processing with custom prompt...")
    process_with_custom_prompt(
        queries=queries,
        system_prompt=educational_prompt,
        output_file="educational_queries.json"
    )
    
    # Example 4: Show how to create different prompt types
    print("\n4. Other prompt examples you could use:")
    examples = [
        "Extract queries about technology and programming",
        "Find queries asking for step-by-step instructions or how-to guides",
        "Identify queries about scientific concepts or research",
        "Extract queries asking for comparisons between different things"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")
    
    print("\n" + "=" * 50)
    print("💡 To use with real OpenAI API:")
    print("   1. Set your OPENAI_API_KEY in .env file")
    print("   2. Replace the example logic with actual API calls")
    print("   3. Use main.py or runInferenceInBatches.py for full functionality")
    print("   4. Adjust BATCH_SIZE in config.py based on your API limits")


if __name__ == "__main__":
    main()
