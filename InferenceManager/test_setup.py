#!/usr/bin/env python3
"""
Simple test script to verify the InferenceManager setup is working correctly.
"""

import json
from pathlib import Path

from config import DATA_LABEL, INPUT_FILE, MODEL, OUTPUT_FILE, PROMPT_FILE
from utils import load_data_items, load_prompt, save_json_file


def test_file_loading() -> None:
    """Test that we can load the sample data and prompt."""
    print("Testing file loading...")
    
    # Test loading sample queries
    if Path("sample_queries.json").exists():
        queries = load_data_items(Path("sample_queries.json"), DATA_LABEL)
        print(f"✓ Loaded {len(queries)} sample queries")
        print(f"  Sample: {queries[:3]}")
    else:
        print("⚠ sample_queries.json not found")
    
    # Test loading prompt
    if PROMPT_FILE.exists():
        prompt = load_prompt(PROMPT_FILE)
        print(f"✓ Loaded system prompt ({len(prompt)} characters)")
        print(f"  Preview: {prompt[:100]}...")
    else:
        print("⚠ System prompt file not found")
    
    print()


def test_config() -> None:
    """Test that configuration is properly set."""
    print("Testing configuration...")
    print(f"✓ Input file: {INPUT_FILE}")
    print(f"✓ Output file: {OUTPUT_FILE}")
    print(f"✓ Prompt file: {PROMPT_FILE}")
    print(f"✓ Model: {MODEL}")
    print(f"✓ Data label: {DATA_LABEL}")
    print()


def test_utils() -> None:
    """Test utility functions."""
    print("Testing utility functions...")
    
    # Test JSON save/load
    test_data = {"test": "data", "numbers": [1, 2, 3]}
    test_file = Path("test_output.json")
    
    try:
        save_json_file(test_data, test_file)
        print("✓ JSON save function works")
        
        loaded_data = json.loads(test_file.read_text())
        if loaded_data == test_data:
            print("✓ JSON load function works")
        else:
            print("✗ JSON load function has issues")
        
        # Clean up
        test_file.unlink()
        print("✓ Cleanup completed")
        
    except Exception as e:
        print(f"✗ Utility test failed: {e}")
    
    print()


def main() -> None:
    """Run all tests."""
    print("🧪 InferenceManager Setup Test")
    print("=" * 40)
    
    test_config()
    test_file_loading()
    test_utils()
    
    print("✅ Setup test completed!")
    print("\nNext steps:")
    print("1. Create a .env file with your OPENAI_API_KEY")
    print("2. Place your queries.json file in the project root")
    print("3. Run: python main.py")


if __name__ == "__main__":
    main()
