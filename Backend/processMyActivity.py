import json
from pathlib import Path

def extract_queries(input_path: str, output_path: str):
    input_file = Path(input_path)
    output_file = Path(output_path)

    with input_file.open("r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []
    for entry in data:
        title = entry.get("title", "")
        time = entry.get("time", "")

        # We only want "Searched for ..." events
        if title.startswith("Searched for "):
            query = title.replace("Searched for ", "", 1).strip()

            record = {
                "query": query,
                "timestamp": time
            }

            cleaned.append(record)
    # Wrap the list in a dict under "queries"
    wrapped = {"queries": cleaned}

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(wrapped, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(cleaned)} queries → {output_file}")


if __name__ == "__main__":
    # Example usage
    extract_queries("../Takeout/My Activity/Search/MyActivity.json", "queries.json")
