import json
from pathlib import Path
from typing import Any, cast

# Type alias for JSON-compatible data
JSONData = dict[str, Any] | list[Any] | str | int | float | bool | None


def load_json_file(path: Path) -> JSONData:
    with path.open("r", encoding="utf-8") as f:
        return cast(JSONData, json.load(f))


def save_json_file(data: JSONData, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_data_items(path: Path, data_label: str) -> list[dict]:
    """
    Load data from a JSON file based on the specified data label.
    The file should contain either:
    - A list of objects directly
    - A dictionary with a key matching the data_label containing a list of objects
    
    This function is generic and works with any structured JSON data.
    """
    data = load_json_file(path)
    if isinstance(data, dict):
        if data_label in data and isinstance(data[data_label], list):
            return data[data_label]  # keep objects as-is
        raise ValueError(
            f"Expected JSON with a list under the key '{data_label}'. "
            f"Found keys: {list(data.keys())}"
        )
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(
            "Unsupported input format. Expected JSON list or "
            f"dictionary with a list under the '{data_label}' key."
        )


def load_prompt(path: Path) -> str:
    """Load a prompt template from a text file."""
    with path.open("r", encoding="utf-8") as f:
        return f.read().strip()


def generate_dynamic_prompt(template: str, config: dict[str, str]) -> str:
    """
    Generate a dynamic prompt by substituting configuration values into a template.
    
    Args:
        template: The prompt template with placeholders like {DATA_LABEL}
        config: Dictionary containing values to substitute
        
    Returns:
        The generated prompt with all placeholders replaced
    """
    try:
        return template.format(**config)
    except KeyError as e:
        raise ValueError(f"Missing configuration value for prompt template: {e}") from e


def validate_json_structure(file_path: Path, data_label: str) -> bool:
    """
    Validate that a JSON file has the expected structure for processing.
    
    Args:
        file_path: Path to the JSON file to validate
        data_label: The expected key name containing the data list
        
    Returns:
        True if the file has valid structure, False otherwise
    """
    try:
        data = load_json_file(file_path)
        
        if isinstance(data, list):
            # Direct list of items
            return (
                len(data) > 0 and 
                all(isinstance(item, str | int | float | bool) for item in data)
            )
        elif isinstance(data, dict):
            # Dictionary with data under the specified label
            if (
                data_label in data and 
                isinstance(data[data_label], list) and 
                len(data[data_label]) > 0
            ):
                return True
            return False
        else:
            return False
            
    except Exception:
        return False
