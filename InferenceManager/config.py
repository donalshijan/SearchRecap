from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()
modelName = os.getenv("MODEL_NAME")

# === CONFIGURATION ===
INPUT_FILE: Path = Path("queries.json")
OUTPUT_FILE: Path = Path("queries_classfied.json")
PROMPT_FILE: Path = Path("prompts/system.txt")

BATCH_SIZE: int = 10
if(modelName==None):
    print("provide model name ")
    raise OSError("model name  not specified")
MODEL: str = modelName  # or "gpt-4", etc.

# Inference method to use
INFERENCE_METHOD: str = "batch"  # Options: "batch", "streaming", "parallel"

# Data label configuration - what kind of data are we processing?
DATA_LABEL: str = "queries"  # Examples: "queries", "names", "companies", "products", etc.
DATA_DESCRIPTION: str = "Google search queries"  # Human-readable description of the data

# Task configuration - what are we doing with the data?

TASK_DESCRIPTION: str = "Classifying a person's search queries according to the category that seems fit for that query."
TASK_INSTRUCTIONS: str = (
    "You are given a list of user search query entries. "
    "Each entry is a JSON object with the following fields:\n"
    " - 'query': the search text\n"
    " - 'time': timestamp of the query\n\n"
    "Your task is to classify the query field of each object entry in the list into one of the predefined categories "
    "and return the same list of objects, but with an additional field "
    "called 'category' added to each object. The number of objects in the "
    "output must exactly match the number of objects in the input.\n\n"
    "Predefined taxonomy of categories:\n"
    " - Lexis: meanings, definitions, idioms, slang, expressions, vocabulary.\n"
    " - History: events, wars, civilizations, timelines.\n"
    " - Biography: information about specific people, lives, accomplishments.\n"
    " - Science: natural sciences, discoveries, physics, chemistry, biology.\n"
    " - Technology: computers, AI, inventions, gadgets, engineering.\n"
    " - Culture: art, literature, mythology, religion, traditions.\n"
    " - Society: politics, law, social systems, demographics.\n"
    " - Health: medical info, nutrition, fitness, wellbeing.\n"
    " - Gooning: Pornography, adult content."
    " - Miscellaneous: if none of the above apply.\n\n"
    "Most queries from this user are about word meanings, idioms, or expressions. "
    "Prioritize accurate classification into 'Lexis' for such cases.\n\n"
    "### Input format:\n"
    "[\n"
    "  {\n"
    "    query': <search_text>,\n"
    "    'time': <timestamp>,\n"
    "  },\n"
    "  ...\n"
    "]\n\n"
    "### Output format:\n"
    "[\n"
    "  {\n"
    "    'query': <search_text>,\n"
    "    'time': <timestamp>,\n"
    "    'category': <one_of_taxonomy>\n"
    "  },\n"
    "  ...\n"
    "]\n\n"
    "### Examples:\n\n"
    "Input:\n"
    """[
      {
        "query": "What caused the Flint Michigan water to turn poisoned",
        "time": "2025-10-03T09:23:00Z",
      },
      {
        "query": "Is it possible for a child to develop deeply set eyeballs despite parents not having them",
        "time": "2025-10-02T15:00:00Z",
      },
      {
        "query": "What's the joke about American founding fathers and misola oil around sexual quirks of Ben Franklin",
        "time": "2025-10-03T14:28:00Z",
      },
      {
        "query": "How were apps like Shazam able to identify music when you hum or sing",
        "time": "2025-10-01T21:00:00Z",
      }
    ]\n\n"""
    "Output:\n"
    """[
      {
        "query": "What caused the Flint Michigan water to turn poisoned",
        "time": "2025-10-03T09:23:00Z",
        "category": "Society"
      },
      {
        "query": "Is it possible for a child to develop deeply set eyeballs despite parents not having them",
        "time": "2025-10-02T15:00:00Z",
        "category": "Health"
      },
      {
        "query": "What's the joke about American founding fathers and misola oil around sexual quirks of Ben Franklin",
        "time": "2025-10-03T14:28:00Z",
        "category": "Culture"
      },
      {
        "query": "How were apps like Shazam able to identify music when you hum or sing",
        "time": "2025-10-01T21:00:00Z",
        "category": "Technology"
      }
    ]"""
)

